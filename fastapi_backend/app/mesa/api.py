import re
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import compare_digest, token_urlsafe
from time import monotonic
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.mesa.engine import respond, scenario_save
from app.mesa.models import MesaConversation, MesaDailyMetric, MesaScenario
from app.mesa.routing import simplify
from app.mesa.schemas import Action, Answer, Consent, Context, Preferences, ResultTable, SessionView, Turn, TurnInput
from app.security.auth import get_current_user

router = APIRouter(prefix="/mesa", tags=["Mesa"])
optional_bearer = OAuth2PasswordBearer(tokenUrl="/api/users/login", auto_error=False)
Database = Annotated[AsyncSession, Depends(get_db)]
GuestToken = Annotated[str | None, Header(alias="X-Mesa-Guest", max_length=120)]
_creation_windows = {}


def now():
    return datetime.now(timezone.utc)


def digest(value):
    return sha256(value.encode()).hexdigest()


async def identity(request: Request, db: Database, token: Annotated[str | None, Depends(optional_bearer)]):
    if token is None and request.headers.get("authorization"):
        raise HTTPException(401, "Invalid authentication credentials")
    return (await get_current_user(token, db)).id if token else None


Owner = Annotated[int | None, Depends(identity)]


def enforce_creation_rate(request):
    timestamp = monotonic()
    address = request.client.host if request.client else "unknown"
    if len(_creation_windows) >= 2048:
        for key in [key for key, (until, _) in _creation_windows.items() if until <= timestamp]:
            _creation_windows.pop(key, None)
        if len(_creation_windows) >= 2048 and address not in _creation_windows:
            raise HTTPException(429, "Too many new conversations")
    until, count = _creation_windows.get(address, (0, 0))
    if until <= timestamp:
        until, count = timestamp + 60, 0
    if count >= 20:
        raise HTTPException(429, "Wait a minute before starting another conversation")
    _creation_windows[address] = (until, count + 1)


async def conversation(db, session_id, owner, guest, *, lock=False):
    query = select(MesaConversation).where(MesaConversation.id == session_id, MesaConversation.expires_at > now())
    entry = (await db.scalars(query.with_for_update() if lock else query)).one_or_none()
    if entry and entry.user_id is not None and owner == entry.user_id:
        return entry
    if entry and owner is None and entry.user_id is None and guest and entry.guest_digest:
        if compare_digest(entry.guest_digest, digest(guest)):
            return entry
    raise HTTPException(404, "This conversation is missing or has expired")


def view(entry, guest_token=None):
    turns = [Turn.model_validate(item["turn"]) for item in entry.state.get("turns", [])]
    if turns:
        if entry.state.get("choices_stale"):
            turns[-1].answer.choices = []
            turns[-1].answer.suggestions = []
            turns[-1].answer.follow_more = []
        if not entry.state.get("pending_action"):
            turns[-1].answer.action = None
    return SessionView(id=entry.id, guest_token=guest_token, retain_history=entry.retained,
                       expires_at=entry.expires_at.isoformat(), context=entry.state.get("context", {}), turns=turns)


def touch(entry):
    entry.updated_at = now()
    if entry.retained:
        entry.expires_at = entry.updated_at + timedelta(days=30)


async def metric(db, intent, event, count=1):
    if not count or db.bind.dialect.name != "postgresql":
        return
    values = {"day": now().date().isoformat(), "intent": intent, "event": event, "count": count}
    statement = insert(MesaDailyMetric).values(**values).on_conflict_do_update(
        index_elements=["day", "intent", "event"], set_={"count": MesaDailyMetric.count + count}
    )
    await db.execute(statement)


@router.post("/conversations", response_model=SessionView, status_code=201)
async def create_conversation(payload: Consent, request: Request, response: Response, db: Database, owner: Owner):
    response.headers["Cache-Control"] = "no-store"
    enforce_creation_rate(request)
    if payload.retain_history and owner is None:
        raise HTTPException(401, "Sign in to keep a conversation")
    timestamp = now()
    await db.execute(delete(MesaConversation).where(MesaConversation.expires_at <= timestamp))
    guest = token_urlsafe(32) if owner is None else None
    entry = MesaConversation(id=uuid4(), user_id=owner, guest_digest=digest(guest) if guest else None,
        retained=payload.retain_history, updated_at=timestamp,
        expires_at=timestamp + timedelta(days=30 if payload.retain_history else 1),
        state={"context": {}, "turns": []})
    db.add(entry)
    await db.commit()
    return view(entry, guest)


@router.get("/conversations")
async def recent_conversations(response: Response, db: Database, owner: Owner):
    response.headers["Cache-Control"] = "no-store"
    if owner is None:
        return []
    rows = (await db.scalars(select(MesaConversation).where(
        MesaConversation.user_id == owner, MesaConversation.retained.is_(True), MesaConversation.expires_at > now()
    ).order_by(MesaConversation.updated_at.desc()).limit(20))).all()
    return [{"id": entry.id, "updated_at": entry.updated_at,
             "title": f"Mesa conversation · {entry.updated_at:%b %d}"} for entry in rows]


@router.get("/conversations/{session_id}", response_model=SessionView)
async def get_conversation(session_id: UUID, response: Response, db: Database, owner: Owner, guest: GuestToken = None):
    response.headers["Cache-Control"] = "no-store"
    return view(await conversation(db, session_id, owner, guest))


@router.delete("/conversations/{session_id}", status_code=204)
async def delete_conversation(session_id: UUID, db: Database, owner: Owner, guest: GuestToken = None):
    await db.delete(await conversation(db, session_id, owner, guest, lock=True))
    await db.commit()
    return Response(status_code=204, headers={"Cache-Control": "no-store"})


@router.patch("/conversations/{session_id}/history", response_model=SessionView)
async def change_consent(session_id: UUID, payload: Consent, response: Response, db: Database, owner: Owner, guest: GuestToken = None):
    response.headers["Cache-Control"] = "no-store"
    if owner is None:
        raise HTTPException(401, "Sign in to keep a conversation")
    entry = await conversation(db, session_id, owner, guest, lock=True)
    entry.retained = payload.retain_history
    touch(entry)
    if not entry.retained:
        entry.expires_at = now() + timedelta(days=1)
    await db.commit()
    return view(entry)


@router.patch("/conversations/{session_id}/context", response_model=SessionView)
async def edit_context(session_id: UUID, payload: Preferences, response: Response, db: Database, owner: Owner, guest: GuestToken = None):
    response.headers["Cache-Control"] = "no-store"
    entry = await conversation(db, session_id, owner, guest, lock=True)
    context = Context.model_validate(entry.state.get("context", {}))
    changes = payload.model_dump(exclude_unset=True)
    if any(name in changes and changes[name] != getattr(context, name) for name in ("subject", "campus", "credential")):
        changes["program_id"] = None
    context = Context.model_validate(context.model_dump() | changes)
    entry.state = {**entry.state, "context": context.model_dump(mode="json"), "choices_stale": True,
                   "pending_action": None, "scenario": None}
    touch(entry)
    await db.commit()
    return view(entry)


def find_choice(payload, previous, stale):
    if stale or not previous:
        if payload.choice_id:
            raise HTTPException(409, "This choice is stale. Type a question to get new choices.")
        return None
    latest = Turn.model_validate(previous[-1]["turn"])
    numbered = re.fullmatch(r"option\s+(\d{1,2})[.!]?", simplify(payload.message or ""))
    if numbered:
        index = int(numbered[1]) - 1
        choices = latest.answer.choices or latest.answer.suggestions
        return choices[index] if 0 <= index < len(choices) else None
    if not payload.choice_id:
        return None
    for choice in (*latest.answer.choices, *latest.answer.suggestions, *latest.answer.follow_more):
        if choice.id == payload.choice_id:
            return choice
    raise HTTPException(409, "This choice is no longer available")


@router.post("/conversations/{session_id}/turns", response_model=Turn)
async def send_turn(session_id: UUID, payload: TurnInput, response: Response, db: Database, owner: Owner, guest: GuestToken = None):
    response.headers["Cache-Control"] = "no-store"
    entry = await conversation(db, session_id, owner, guest, lock=True)
    previous = entry.state.get("turns", [])
    key = str(payload.request_id)
    fingerprint = digest(payload.message or str(payload.choice_id))
    for item in previous:
        if item["key"] == key:
            if item["input"] != fingerprint:
                raise HTTPException(409, "This retry key belongs to a different question")
            return Turn.model_validate(item["turn"])
    if len(previous) >= 80:
        raise HTTPException(409, "This conversation is full. Start a new conversation.")
    timestamp = now()
    if sum(item["at"] > (timestamp - timedelta(minutes=1)).isoformat() for item in previous) >= 12:
        raise HTTPException(429, "Please wait before sending another question")
    context = Context.model_validate(entry.state.get("context", {}))
    choice = find_choice(payload, previous, entry.state.get("choices_stale"))
    message = choice.label if choice else payload.message
    prior = previous[-1]["turn"]["answer"]["intent"] if previous else None
    scenario = entry.state.get("scenario")
    if not choice and simplify(message) in {"save scenario", "save this scenario", "save as a new scenario"}:
        answer = Answer(intent="M27", status="partial", text="Run a What-If calculation, then sign in to save it.")
        if scenario and owner is not None:
            answer = Answer(intent="M27", text="Review the alternative before saving it.", action=scenario_save(ResultTable.model_validate(scenario)))
    elif not choice and re.fullmatch(r"option\s+\d+[.!]?", simplify(message)):
        answer = Answer(intent="M37", status="clarification", text="There’s no matching numbered choice in the latest reply.",
                        clarification="Which college, program, or question did you mean?")
    else:
        context, answer = await respond(db, message, context, user_id=owner, prior_intent=prior, choice=choice,
                                        previous=[item["turn"]["message"] for item in previous[-8:]])
    if answer.intent in {"M27", "M31", "M34"} and answer.tables:
        scenario = answer.tables[0].model_dump(mode="json")
        if owner is not None:
            answer.action = scenario_save(answer.tables[0])
    if simplify(message).startswith(("return to", "reset scenario")):
        scenario = None
    turn = Turn(id=uuid4(), message=message, answer=answer, context=context)
    entry.state = {**entry.state, "context": context.model_dump(mode="json"), "scenario": scenario,
        "pending_action": answer.action.model_dump(mode="json") if answer.action else None,
        "choices_stale": False, "turns": [*previous, {"key": key,
            "input": fingerprint, "at": timestamp.isoformat(), "turn": turn.model_dump(mode="json")}]}
    touch(entry)
    await metric(db, answer.intent, answer.status)
    await metric(db, answer.intent, "suggestions_shown", len(answer.suggestions))
    if choice and choice.kind == "suggestion":
        await metric(db, choice.intent, "suggestion_selected")
    await db.commit()
    return turn


@router.post("/conversations/{session_id}/actions/{action_id}")
async def confirm(session_id: UUID, action_id: UUID, response: Response, db: Database, owner: Owner):
    response.headers["Cache-Control"] = "no-store"
    if owner is None:
        raise HTTPException(401, "Sign in to save a scenario")
    entry = await conversation(db, session_id, owner, None, lock=True)
    saved = await db.get(MesaScenario, action_id)
    if saved and saved.conversation_id == entry.id:
        return {"status": "saved", "scenario_id": action_id}
    pending = entry.state.get("pending_action")
    action = Action.model_validate(pending) if pending else None
    if not action or action.id != action_id or action.expires_at <= now().isoformat():
        raise HTTPException(409, "This confirmation is missing or has expired")
    db.add(MesaScenario(id=action_id, conversation_id=entry.id, comparison=action.preview.model_dump(mode="json")))
    entry.state = {**entry.state, "pending_action": None}
    touch(entry)
    await metric(db, "M27", "scenario_saved")
    await db.commit()
    return {"status": "saved", "scenario_id": action_id}


@router.get("/conversations/{session_id}/scenarios")
async def saved_scenarios(session_id: UUID, response: Response, db: Database, owner: Owner):
    response.headers["Cache-Control"] = "no-store"
    if owner is None:
        raise HTTPException(401, "Sign in to view saved scenarios")
    entry = await conversation(db, session_id, owner, None)
    rows = (await db.scalars(select(MesaScenario).where(MesaScenario.conversation_id == entry.id).limit(80))).all()
    return [{"id": row.id, "comparison": row.comparison} for row in rows]
