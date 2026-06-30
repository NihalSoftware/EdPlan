from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.education_plan import CourseReschedule, EducationPlan
from app.models.user import User
from app.student.domains.auth.services import user_service
from app.student.domains.planning.repositories import plan_repository, reschedule_repository
from app.student.domains.planning.schemas.education import (
    EducationPlanListQuery,
    EducationPlanQuery,
    EducationPlanRequest,
    ProgramCoursePayload,
    RescheduleRequest,
)


def _normalize_degree(value: str | None) -> str:
    if not value:
        return ""
    return str(value).strip().lower()


def _infer_program(payload: Sequence[ProgramCoursePayload]) -> tuple[str, str]:
    program_name = next((item.program for item in payload if item.program), None)
    university_name = next((item.university for item in payload if item.university), None)

    if not program_name or not university_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program and university are required in at least one course entry.",
        )
    return program_name, university_name


def _plan_payload(plan: EducationPlan) -> dict:
    payload = dict(plan.payload or {})
    if plan.degree and not payload.get("degree"):
        payload["degree"] = plan.degree
    return payload


async def add_or_replace_plan_for_request(
    db: AsyncSession, payload: EducationPlanRequest
) -> dict:
    user = await user_service.get_user_by_email(db, payload.emailaddress)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    plan = await add_or_replace_plan(db, user, payload)
    return plan.payload


async def query_plan_payload(db: AsyncSession, query: EducationPlanQuery) -> dict | None:
    plan = await query_plan(db, query)
    if not plan:
        return None
    return _plan_payload(plan)


async def list_plan_payloads(
    db: AsyncSession, query: EducationPlanListQuery
) -> list[dict]:
    plans = await list_plans(db, query)
    return [_plan_payload(plan) for plan in plans]


async def delete_plan_for_request(
    db: AsyncSession, request: EducationPlanDeleteRequest
) -> None:
    user = await user_service.get_user_by_email(db, request.email.lower())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await delete_plan(db, user, request.programname, request.univerityname, request.degree)


async def save_reschedule_for_request(
    db: AsyncSession, request: RescheduleRequest
) -> dict:
    user = await user_service.get_user_by_email(db, request.emailaddress)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entry = await save_reschedule(db, user, request)
    return entry.payload


async def add_or_replace_plan(
    db: AsyncSession, user: User, payload: EducationPlanRequest
) -> EducationPlan:
    if not payload.program:
        raise HTTPException(status_code=400, detail="Program payload is empty")

    program_name, university_name = _infer_program(payload.program)
    degree_value = payload.degree.strip() if payload.degree else None

    existing = await get_plan_by_program(
        db, user.id, program_name, university_name, degree_value
    )
    plan_payload = {"program": [course.model_dump(by_alias=True) for course in payload.program]}
    if degree_value:
        plan_payload["degree"] = degree_value

    if existing:
        await plan_repository.update_plan(existing, payload=plan_payload, degree=degree_value)
        await plan_repository.delete_program_courses(
            db, education_plan_id=existing.id
        )
        await _persist_courses(db, existing, payload.program)
        await db.commit()
        await db.refresh(existing)
        return existing

    plan = await plan_repository.create_plan(
        db,
        user_id=user.id,
        program_name=program_name,
        university_name=university_name,
        degree=degree_value,
        payload=plan_payload,
    )
    await _persist_courses(db, plan, payload.program)
    await db.commit()
    await db.refresh(plan)
    return plan


async def _persist_courses(
    db: AsyncSession, plan: EducationPlan, courses: Sequence[ProgramCoursePayload]
) -> None:
    await plan_repository.persist_courses(db, plan=plan, courses=courses)


async def get_plan_by_program(
    db: AsyncSession,
    user_id: int,
    program_name: str,
    university_name: str,
    degree: str | None = None,
) -> EducationPlan | None:
    plans = await plan_repository.get_plan(
        db,
        user_id=user_id,
        program_name=program_name,
        university_name=university_name,
    )

    # No specific degree requested; return the first match (maintains legacy behavior)
    if not degree:
        return plans[0] if plans else None

    target_degree = _normalize_degree(degree)
    for plan in plans:
        existing_degree = _normalize_degree(plan.degree or (plan.payload or {}).get("degree"))
        if existing_degree == target_degree:
            return plan

    return None


async def query_plan(db: AsyncSession, query: EducationPlanQuery) -> EducationPlan | None:
    plans = await plan_repository.get_plan(
        db,
        program_name=query.programname,
        university_name=query.univerityname,
    )
    if not plans:
        return None
    if not query.degree:
        return plans[0]
    target_degree = _normalize_degree(query.degree)
    for plan in plans:
        existing_degree = _normalize_degree(plan.degree or (plan.payload or {}).get("degree"))
        if existing_degree == target_degree:
            return plan
    return None


async def list_plans(db: AsyncSession, query: EducationPlanListQuery) -> Sequence[EducationPlan]:
    return await plan_repository.list_plans(db, email=query.email.lower())


async def delete_plan(
    db: AsyncSession,
    user: User,
    program_name: str,
    university_name: str,
    degree: str | None = None,
) -> None:
    plan = await get_plan_by_program(db, user.id, program_name, university_name, degree)
    if not plan:
        raise HTTPException(status_code=404, detail="Education plan not found")
    await plan_repository.delete_plan(db, plan)


async def save_reschedule(
    db: AsyncSession, user: User, payload: RescheduleRequest
) -> CourseReschedule:
    entry = await reschedule_repository.create_reschedule(
        db,
        user_id=user.id,
        payload={"reschedule": [item.dict() for item in payload.reschedule]},
    )
    return entry
