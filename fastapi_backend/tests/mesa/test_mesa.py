"""Mesa contract tests, plus PostgreSQL integration tests for opt-in disposable databases."""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, text

from app.db.session import AsyncSessionLocal, engine
from app.main import app
from app.mesa import api, catalog
from app.mesa.models import MesaConversation, MesaScenario
from app.mesa.routing import SPEC, edits, followups, route
from app.mesa.schemas import Context
from app.models.user import User
from app.security.auth import create_access_token
from app.student.domains.discovery.models import Program, University
from app.student.domains.planning.models.normalized_plan import EdPlan

FLOWS = json.loads(Path(__file__).with_name("guided_flows.json").read_text(encoding="utf-8"))
EXAMPLES = [(intent, text) for intent, item in SPEC.items() for text in item["utterances"]]
ROOT = "/api/mesa/conversations"
requires_postgres = pytest.mark.skipif(
    os.getenv("MESA_TEST_DISPOSABLE_DB") != "1", reason="Run against a migrated disposable PostgreSQL database"
)


@pytest.mark.parametrize("intent,message", EXAMPLES)
def test_authored_examples_route(intent, message):
    assert route(message) == intent


@pytest.mark.parametrize("message,intent", [
    ("Could you explain how many credits my schedule needs?", "M18"),
    ("I'm interested in becoming a nurse someday. What careers might fit?", "M03"),
    ("What are the prerequisites for the first nursing course?", "M17"),
    ("Does the university list any job postings this week?", "M25"),
    ("What if I only take 9 credits each semester?", "M27"),
    ("I am in immediate danger and need help", "M38"),
])
def test_separate_rule_examples(message, intent):
    assert route(message, authored_examples=False) == intent


def test_preference_and_scenario_are_separate():
    baseline = edits("I am an international student", Context(credits_per_term=18), "M02")
    context = edits("What if I lived in California instead?", baseline, "M30")
    assert context.tuition_category == "international"
    assert context.scenario.tuition_category == "nonresident"
    assert edits("Return to my actual international status", context, "M36") == baseline
    context = edits("What if I take 12 credits instead of 18?", baseline, "M27")
    context = edits("60 credits remaining", context, route("60 credits remaining", "M27"))
    assert context.credits_per_term == context.scenario.baseline_credits == 18
    assert context.scenario.credits_per_term == 12
    assert context.scenario.remaining_credits == 60
    assert catalog.credit_scenario(60, 18, 12).rows[2] == ["Minimum terms by credit load", 4, 5, 1]


def test_suggestions_avoid_prior_and_unavailable_items():
    choices = followups("M03", Context(subject="nursing"), "Find colleges offering nursing",
                        ["Compare nursing tuition"], {"M23", "M24", "M25"})
    assert 5 <= len(choices) <= 8
    assert len({choice.label for choice in choices}) == len(choices)
    assert "Find colleges offering nursing" not in {choice.label for choice in choices}
    assert "Compare nursing tuition" not in {choice.label for choice in choices}
    assert all(choice.intent not in {"M23", "M24", "M25"} for choice in choices)


@pytest_asyncio.fixture
async def qa(monkeypatch):
    await engine.dispose()
    users = [User(email=f"mesa-{uuid4()}@example.test", password_hash="test-only") for _ in range(2)]
    university = University(university_name="Northern New Mexico College", city="Espanola",
                            state="NM", website="https://nnmc.edu/")
    program = Program(program_name="Nursing", degree="Associate", total_credit_hours=68, university=university)
    university.programs.extend([
        Program(program_name="Nursing", degree="Bachelor", total_credit_hours=120),
        Program(program_name="Computer Science", degree="Bachelor", total_credit_hours=120),
        Program(program_name="Healthcare Administration", degree="Associate", total_credit_hours=60),
    ])
    career_id = uuid4()
    async with AsyncSessionLocal.begin() as db:
        db.add_all([*users, university])
        await db.flush()
        plan = EdPlan(user_id=users[0].id, university_id=university.university_id,
                      program_id=program.program_id, plan_name="Mesa test plan")
        db.add(plan)
        await db.execute(
            text("""
                INSERT INTO careers (career_id, career_name, career_description, industry, career_level)
                VALUES (:id, :name, 'A nursing career', 'Healthcare', 'Entry')
            """),
            {"id": career_id, "name": f"Mesa QA nurse {career_id}"},
        )
        await db.execute(
            text("INSERT INTO program_careers (program_id, career_id) VALUES (:program, :career)"),
            {"program": program.program_id, "career": career_id},
        )
    clock = datetime.now(timezone.utc)
    monkeypatch.setattr(api, "now", lambda: clock)
    monkeypatch.setattr(api, "_creation_windows", {})
    async def metrics(universities):
        return {school.university_id: {"in_state_tuition": 4000, "out_of_state_tuition": 11000,
                  "average_annual_cost": 9500, "year": 2024, "organization_type": "Public"} for school in universities}
    monkeypatch.setattr(catalog, "public_metrics", metrics)

    def advance(minutes=1):
        nonlocal clock
        clock += timedelta(minutes=minutes)

    conversation_ids = []

    async def track_conversations(response):
        if response.request.method == "POST" and response.request.url.path == ROOT and response.status_code == 201:
            from uuid import UUID

            await response.aread()
            conversation_ids.append(UUID(response.json()["id"]))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://mesa.test",
                           event_hooks={"response": [track_conversations]}) as client:
        yield client, users, plan, advance
    async with AsyncSessionLocal.begin() as db:
        await db.execute(delete(MesaConversation).where(MesaConversation.id.in_(conversation_ids)))
        await db.execute(delete(User).where(User.id.in_([user.id for user in users])))
        await db.execute(delete(Program).where(Program.university_id == university.university_id))
        await db.execute(delete(University).where(University.university_id == university.university_id))
        await db.execute(text("DELETE FROM careers WHERE career_id = :id"), {"id": career_id})
    await engine.dispose()


def authorization(user):
    return {"Authorization": f"Bearer {create_access_token(user.email)}"}


async def turn(client, path, headers, message=None, choice_id=None, request_id=None):
    return await client.post(f"{path}/turns", headers=headers, json={
        "request_id": str(request_id or uuid4()), "message": message, "choice_id": choice_id,
    })


@requires_postgres
@pytest.mark.asyncio
@pytest.mark.parametrize("flow", FLOWS, ids=[flow["title"] for flow in FLOWS])
async def test_guided_flow(qa, flow):
    client, users, _, advance = qa
    signed_in = flow is FLOWS[4] or flow is FLOWS[9]
    headers = authorization(users[0]) if signed_in else {}
    session = await client.post(ROOT, json={}, headers=headers)
    assert session.status_code == 201, session.text
    data = session.json()
    if not signed_in:
        headers["X-Mesa-Guest"] = data["guest_token"]
    path = f'{ROOT}/{data["id"]}'
    answers = []
    for entry in flow["turns"]:
        advance()
        response = await turn(client, path, headers, message=entry["message"])
        assert response.status_code == 200, response.text
        item = response.json()
        assert item["answer"]["intent"] == entry["intent"], entry["message"]
        assert item["answer"]["text"]
        assert len(item["answer"]["suggestions"]) <= 5
        answers.append(item)
    final = answers[-1]
    title = flow["title"]
    if title == "nursing":
        first_answer = answers[0]["answer"]
        assert first_answer["status"] == "partial"
        assert first_answer["tables"][0]["title"] == "Catalog career mappings"
        course_path = first_answer["tables"][0]["rows"][0]
        assert course_path[0] == "Nursing" and course_path[1].startswith("Mesa QA nurse ")
        assert final["context"]["education_stage"] == "GED"
        assert final["context"]["subject"] == "nursing"
        assert final["context"]["tuition_category"] == "international"
        assert final["context"]["scenario"]["tuition_category"] == "nonresident"
    elif title.startswith("Multi-parameter"):
        assert final["context"]["budget_annual"] == 12000
        assert final["context"]["budget_basis"] == "attendance"
        assert final["context"]["max_drive_minutes"] == 90
        assert "cannot verify driving-time" in final["answer"]["text"]
    elif title.startswith("Employer"):
        assert final["answer"]["status"] == "unavailable"
        assert not final["answer"]["tables"]
    elif title.startswith("Residency"):
        assert final["context"]["scenario"] is None
        assert final["context"]["tuition_category"] == "international"
    elif title.startswith("What-if"):
        assert final["context"]["scenario"]["include_summer"] is True
        assert final["context"]["credits_per_term"] is None
    elif title.startswith("Saved plan"):
        assert final["answer"]["choices"][0]["plan_id"]
        response = await turn(client, path, headers, choice_id=final["answer"]["choices"][0]["id"])
        assert response.status_code == 200, response.text
        assert "Mesa test plan" in response.json()["answer"]["text"]
        assert response.json()["answer"]["action"] is None


@requires_postgres
@pytest.mark.asyncio
async def test_ownership_consent_idempotency_expiry_and_scenario(qa):
    client, users, plan, advance = qa
    owner, outsider = map(authorization, users)
    response = await client.post(ROOT, json={"retain_history": True})
    assert response.status_code == 401
    guest = (await client.post(ROOT, json={})).json()
    guest_path = f'{ROOT}/{guest["id"]}'
    assert (await client.get(guest_path)).status_code == 404
    assert (await client.get(guest_path, headers={"X-Mesa-Guest": guest["guest_token"]})).status_code == 200
    session = (await client.post(ROOT, json={}, headers=owner)).json()
    path = f'{ROOT}/{session["id"]}'
    assert (await client.get(ROOT, headers=owner)).json() == []
    assert (await client.get(path, headers=outsider)).status_code == 404
    assert (await client.patch(f"{path}/history", json={"retain_history": True}, headers=owner)).status_code == 200
    assert (await client.get(ROOT, headers=owner)).json()[0]["id"] == session["id"]
    assert (await client.get(f"/api/plans/{plan.plan_id}", headers=outsider)).status_code == 404
    assert (await client.get(f"/api/plans/{plan.plan_id}", headers=owner)).status_code == 200
    key = uuid4()
    question = "What if I take 12 credits instead of 18?"
    initial = await turn(client, path, owner, message=question, request_id=key)
    assert initial.status_code == 200, initial.text
    assert (await turn(client, path, owner, message=question, request_id=key)).json() == initial.json()
    assert (await turn(client, path, owner, message="New text", request_id=key)).status_code == 409
    assert (await turn(client, path, owner, message="60 credits remaining")).status_code == 200
    answer = (await client.get(path, headers=owner)).json()["turns"][-1]["answer"]
    assert answer["tables"][0]["rows"][2][1:] == [4, 5, 1]
    action = answer["action"]["id"]
    async with AsyncSessionLocal() as db:
        assert await db.get(MesaScenario, action) is None
    assert (await client.post(f"{path}/actions/{action}", headers=outsider)).status_code == 404
    saved = await client.post(f"{path}/actions/{action}", headers=owner)
    assert saved.status_code == 200, saved.text
    assert (await client.post(f"{path}/actions/{action}", headers=owner)).json() == saved.json()
    assert len((await client.get(f"{path}/scenarios", headers=owner)).json()) == 1
    assert (await client.delete(path, headers=owner)).status_code == 204
    assert (await client.get(path, headers=owner)).status_code == 404
    advance(24 * 60 + 1)
    assert (await client.get(guest_path, headers={"X-Mesa-Guest": guest["guest_token"]})).status_code == 404
