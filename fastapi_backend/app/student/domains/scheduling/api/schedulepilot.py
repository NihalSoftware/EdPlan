from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.orchestrator.schemas.student_context import StudentContext
from app.student.domains.scheduling.module import SchedulePilotModule
from app.student.domains.scheduling.schemas.schedule_persistence import (
    ActivationRequest,
    SaveScheduleRequest,
)
from app.student.domains.scheduling.schemas.schedulepilot_api import (
    ActivateScheduleRequest,
    ActivationResponse,
    ArchiveScheduleResponse,
    CompareSchedulesRequest,
    CompareSchedulesResponse,
    GenerateScheduleRequest,
    GenerateScheduleResponse,
    SaveScheduleApiRequest,
    SavedScheduleDetailResponse,
    SavedScheduleListResponse,
    ScheduleComparisonItem,
)
from app.student.domains.scheduling.schemas.revision import (
    LockSectionRequest,
    RestoreOriginalScheduleRequest,
    ScheduleRevisionRequest,
    ScheduleRevisionResult,
    UnlockSectionRequest,
)
from app.student.domains.scheduling.schemas.session import (
    CompareOptionsRequest,
    RegenerateSessionRequest,
    SelectOptionRequest,
    SessionIdRequest,
    SessionOperationResult,
    StartSessionRequest,
)
from app.student.domains.scheduling.services.schedule_persistence_service import (
    SchedulePersistenceService,
    schedule_persistence_service,
)
from app.student.domains.scheduling.services.session_service import (
    SchedulingSessionService,
    scheduling_session_service,
)
from app.student.domains.scheduling.services.revision_service import (
    ScheduleRevisionService,
    schedule_revision_service,
)

router = APIRouter(prefix="/schedulepilot", tags=["schedulepilot"])


def get_schedule_persistence_service() -> SchedulePersistenceService:
    return schedule_persistence_service


def get_scheduling_session_service() -> SchedulingSessionService:
    return scheduling_session_service


def get_schedule_revision_service() -> ScheduleRevisionService:
    return schedule_revision_service


@router.post("/generate", response_model=GenerateScheduleResponse)
async def generate_schedule(
    request: GenerateScheduleRequest,
    db: AsyncSession = Depends(get_db),
):
    context = StudentContext(
        user={"id": request.user_id},
        plan={"plan_id": request.plan_id},
        preferences=request.preferences,
    )
    module = SchedulePilotModule(db=db)
    response = await module.execute(
        context,
        request.query or "Generate schedule options.",
    )
    if response.metadata.get("status") == "failed":
        raise HTTPException(
            status_code=400,
            detail=response.metadata.get("errors") or "schedule_generation_failed",
        )
    return {
        "success": True,
        "data": response.data,
        "metadata": response.metadata,
    }


@router.post("/session/start", response_model=SessionOperationResult)
async def start_session(
    request: StartSessionRequest,
    db: AsyncSession = Depends(get_db),
    service: SchedulingSessionService = Depends(get_scheduling_session_service),
):
    try:
        return await service.start_session(db, request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.get("/session", response_model=SessionOperationResult)
async def load_session(
    session_id: str = Query(...),
    service: SchedulingSessionService = Depends(get_scheduling_session_service),
):
    try:
        return service.load_session(SessionIdRequest(session_id=session_id))
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/select", response_model=SessionOperationResult)
async def select_session_option(
    request: SelectOptionRequest,
    service: SchedulingSessionService = Depends(get_scheduling_session_service),
):
    try:
        return service.select_option(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/compare", response_model=SessionOperationResult)
async def compare_session_options(
    request: CompareOptionsRequest,
    service: SchedulingSessionService = Depends(get_scheduling_session_service),
):
    try:
        return service.compare_options(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/regenerate", response_model=SessionOperationResult)
async def regenerate_session(
    request: RegenerateSessionRequest,
    db: AsyncSession = Depends(get_db),
    service: SchedulingSessionService = Depends(get_scheduling_session_service),
):
    try:
        return await service.regenerate(db, request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/undo", response_model=SessionOperationResult)
async def undo_session_action(
    request: SessionIdRequest,
    service: SchedulingSessionService = Depends(get_scheduling_session_service),
):
    try:
        return service.undo_last_action(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/reset", response_model=SessionOperationResult)
async def reset_session(
    request: SessionIdRequest,
    service: SchedulingSessionService = Depends(get_scheduling_session_service),
):
    try:
        return service.reset_session(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/close", response_model=SessionOperationResult)
async def close_session(
    request: SessionIdRequest,
    service: SchedulingSessionService = Depends(get_scheduling_session_service),
):
    try:
        return service.close_session(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/revise", response_model=ScheduleRevisionResult)
async def revise_session_schedule(
    request: ScheduleRevisionRequest,
    service: ScheduleRevisionService = Depends(get_schedule_revision_service),
):
    try:
        return service.revise(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/lock", response_model=SessionOperationResult)
async def lock_session_section(
    request: LockSectionRequest,
    service: ScheduleRevisionService = Depends(get_schedule_revision_service),
):
    try:
        return service.lock_section(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/unlock", response_model=SessionOperationResult)
async def unlock_session_section(
    request: UnlockSectionRequest,
    service: ScheduleRevisionService = Depends(get_schedule_revision_service),
):
    try:
        return service.unlock_section(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/restore", response_model=SessionOperationResult)
async def restore_session_original_schedule(
    request: RestoreOriginalScheduleRequest,
    service: ScheduleRevisionService = Depends(get_schedule_revision_service),
):
    try:
        return service.restore_original(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/revision/undo", response_model=SessionOperationResult)
async def undo_session_revision(
    request: SessionIdRequest,
    service: ScheduleRevisionService = Depends(get_schedule_revision_service),
):
    try:
        return service.undo_last_revision(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/session/revision/redo", response_model=SessionOperationResult)
async def redo_session_revision(
    request: SessionIdRequest,
    service: ScheduleRevisionService = Depends(get_schedule_revision_service),
):
    try:
        return service.redo_last_revision(request)
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/schedules", response_model=SavedScheduleDetailResponse, status_code=201)
async def save_schedule(
    request: SaveScheduleApiRequest,
    db: AsyncSession = Depends(get_db),
    service: SchedulePersistenceService = Depends(get_schedule_persistence_service),
):
    try:
        result = await service.save_schedule(
            db,
            SaveScheduleRequest(
                user_id=request.user_id,
                plan_id=request.plan_id,
                selected_option=request.selected_option,
                schedule_name=request.schedule_name,
                notes=request.notes,
                confirmed=request.confirmed,
            ),
        )
        detail = await service.get_saved_schedule(
            db,
            user_id=request.user_id,
            plan_id=request.plan_id,
            schedule_id=result.schedule.schedule_id,
        )
        return {"success": True, "data": detail}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.get("/plans/{plan_id}/schedules", response_model=SavedScheduleListResponse)
async def list_saved_schedules(
    plan_id: str,
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    service: SchedulePersistenceService = Depends(get_schedule_persistence_service),
):
    try:
        schedules = await service.list_plan_schedules(
            db,
            user_id=user_id,
            plan_id=plan_id,
        )
        return {
            "success": True,
            "data": schedules,
            "metadata": {"count": len(schedules), "plan_id": plan_id},
        }
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.get("/schedules/{schedule_id}", response_model=SavedScheduleDetailResponse)
async def get_saved_schedule(
    schedule_id: str,
    user_id: int = Query(...),
    plan_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    service: SchedulePersistenceService = Depends(get_schedule_persistence_service),
):
    try:
        detail = await service.get_saved_schedule(
            db,
            user_id=user_id,
            plan_id=plan_id,
            schedule_id=schedule_id,
        )
        return {"success": True, "data": detail}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/schedules/{schedule_id}/activate", response_model=ActivationResponse)
async def activate_schedule(
    schedule_id: str,
    request: ActivateScheduleRequest,
    db: AsyncSession = Depends(get_db),
    service: SchedulePersistenceService = Depends(get_schedule_persistence_service),
):
    try:
        result = await service.activate_schedule(
            db,
            ActivationRequest(
                user_id=request.user_id,
                plan_id=request.plan_id,
                schedule_id=schedule_id,
                confirmed=request.confirmed,
            ),
        )
        return {"success": True, "data": result}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/schedules/{schedule_id}/archive", response_model=ArchiveScheduleResponse)
async def archive_schedule(
    schedule_id: str,
    request: ActivateScheduleRequest,
    db: AsyncSession = Depends(get_db),
    service: SchedulePersistenceService = Depends(get_schedule_persistence_service),
):
    try:
        summary = await service.archive_schedule(
            db,
            ActivationRequest(
                user_id=request.user_id,
                plan_id=request.plan_id,
                schedule_id=schedule_id,
                confirmed=request.confirmed,
            ),
        )
        return {"success": True, "data": summary}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


@router.post("/compare", response_model=CompareSchedulesResponse)
async def compare_schedules(
    request: CompareSchedulesRequest,
    db: AsyncSession = Depends(get_db),
    service: SchedulePersistenceService = Depends(get_schedule_persistence_service),
):
    try:
        details = [
            await service.get_saved_schedule(
                db,
                user_id=request.user_id,
                plan_id=request.plan_id,
                schedule_id=schedule_id,
            )
            for schedule_id in request.schedule_ids
        ]
        items = [
            ScheduleComparisonItem(
                schedule_id=detail.schedule_id,
                schedule_name=detail.schedule_name,
                status=detail.status,
                is_active=detail.is_active,
                is_favorite=detail.is_favorite,
                total_credits=detail.total_credits,
                score=detail.score,
                normalized_score=detail.normalized_score,
                rank_at_generation=detail.rank_at_generation,
                selected_term_id=detail.selected_term_id,
                selected_section_count=len(detail.selected_sections),
                conflict_count=len(detail.conflicts_snapshot),
                warning_count=len(detail.warnings_snapshot),
                metrics_snapshot=detail.metrics_snapshot,
                tradeoffs_snapshot=detail.tradeoffs_snapshot,
                explanation_snapshot=detail.explanation_snapshot,
            )
            for detail in details
        ]
        return {
            "success": True,
            "data": items,
            "metadata": {"count": len(items), "plan_id": request.plan_id},
        }
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise _value_error_to_http(exc) from exc


def _value_error_to_http(exc: ValueError) -> HTTPException:
    message = str(exc)
    status_code = 404 if "not found" in message.lower() else 400
    return HTTPException(status_code=status_code, detail=message)
