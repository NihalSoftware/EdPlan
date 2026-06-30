from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.student.domains.planning.schemas.normalized_plan import (
    PlanCourseCreateRequest,
    PlanCourseDeleteResponse,
    PlanCourseDetailResponse,
    PlanCourseListResponse,
    PlanCourseUpdateRequest,
    PlanCreateRequest,
    PlanDetailResponse,
    PlanListResponse,
    PlanUpdateRequest,
)
from app.student.domains.planning.schemas.planning_validation import (
    PlanCourseValidationRequest,
    PlanValidationRequest,
    PlanValidationResponse,
)
from app.student.domains.planning.services.normalized_plan_service import (
    MAX_TERM_CREDITS,
    normalized_plan_service,
)
from app.student.domains.planning.services.planning_validation_service import (
    planning_validation_service,
)

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=PlanListResponse)
async def list_plans(
    user_id: int | None = Query(default=None, gt=0),
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    plans = await normalized_plan_service.list_plans(
        db,
        user_id=user_id,
        is_active=is_active,
    )
    return _success(plans, metadata={"count": len(plans)})


@router.post("", response_model=PlanDetailResponse)
async def create_plan(
    request: PlanCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    plan = await normalized_plan_service.create_plan(db, request)
    return _success(plan)


@router.get("/{plan_id}", response_model=PlanDetailResponse)
async def get_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    plan = await normalized_plan_service.get_plan_by_id(db, plan_id)
    return _success(plan)


@router.patch("/{plan_id}", response_model=PlanDetailResponse)
async def update_plan(
    plan_id: str,
    request: PlanUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    plan = await normalized_plan_service.update_plan(db, plan_id, request)
    return _success(plan)


@router.delete("/{plan_id}", response_model=PlanDetailResponse)
async def deactivate_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    plan = await normalized_plan_service.deactivate_plan(db, plan_id)
    return _success(plan)


@router.post("/{plan_id}/validate", response_model=PlanValidationResponse)
async def validate_plan(
    plan_id: str,
    request: PlanValidationRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    validation = await planning_validation_service.validate_plan(db, plan_id, request)
    return _success(validation)


@router.post("/{plan_id}/validate-course", response_model=PlanValidationResponse)
async def validate_plan_course(
    plan_id: str,
    request: PlanCourseValidationRequest,
    db: AsyncSession = Depends(get_db),
):
    validation = await planning_validation_service.validate_course(db, plan_id, request)
    return _success(validation)


@router.get("/{plan_id}/courses", response_model=PlanCourseListResponse)
async def list_plan_courses(plan_id: str, db: AsyncSession = Depends(get_db)):
    courses = await normalized_plan_service.list_plan_courses(db, plan_id)
    return _success(
        courses,
        metadata={
            "count": len(courses),
            "max_term_credits": MAX_TERM_CREDITS,
            "term_credit_totals": _term_credit_totals(courses),
        },
    )


@router.post("/{plan_id}/courses", response_model=PlanCourseDetailResponse)
async def add_plan_course(
    plan_id: str,
    request: PlanCourseCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    plan_course = await normalized_plan_service.add_plan_course(db, plan_id, request)
    return _success(plan_course, metadata={"max_term_credits": MAX_TERM_CREDITS})


@router.patch("/{plan_id}/courses/{course_id}", response_model=PlanCourseDetailResponse)
async def update_plan_course(
    plan_id: str,
    course_id: str,
    request: PlanCourseUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    plan_course = await normalized_plan_service.update_plan_course(
        db,
        plan_id,
        course_id,
        request,
    )
    return _success(plan_course, metadata={"max_term_credits": MAX_TERM_CREDITS})


@router.delete("/{plan_id}/courses/{course_id}", response_model=PlanCourseDeleteResponse)
async def delete_plan_course(
    plan_id: str,
    course_id: str,
    db: AsyncSession = Depends(get_db),
):
    await normalized_plan_service.delete_plan_course(db, plan_id, course_id)
    return _success(None, metadata={"plan_id": plan_id, "course_id": course_id})


def _success(data, *, metadata: dict | None = None) -> dict:
    response = {"success": True, "data": data}
    if metadata is not None:
        response["metadata"] = metadata
    return response


def _term_credit_totals(courses: list[dict]) -> list[dict]:
    totals: dict[str | None, dict] = {}
    for plan_course in courses:
        term_id = plan_course.get("planned_term_id")
        if term_id not in totals:
            term = plan_course.get("planned_term") or {}
            totals[term_id] = {
                "planned_term_id": term_id,
                "term_name": term.get("term_name"),
                "credits": 0,
            }
        course = plan_course.get("course") or {}
        totals[term_id]["credits"] += course.get("credits") or 0
    return list(totals.values())
