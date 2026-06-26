from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.student.domains.planning.repositories.normalized_plan_repository import (
    NormalizedPlanRepository,
    PlanCourseRepository,
    normalized_plan_repository,
    plan_course_repository,
)
from app.student.domains.planning.schemas.normalized_plan import (
    PlanCourseCreateRequest,
    PlanCourseUpdateRequest,
    PlanCreateRequest,
    PlanUpdateRequest,
)

logger = logging.getLogger(__name__)

MAX_TERM_CREDITS = 18


def _parse_uuid(value: str, field_name: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}",
        ) from exc


def _integrity_error(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NormalizedPlanService:
    def __init__(
        self,
        plan_repository: NormalizedPlanRepository = normalized_plan_repository,
        course_repository: PlanCourseRepository = plan_course_repository,
    ) -> None:
        self.plan_repository = plan_repository
        self.course_repository = course_repository

    async def list_plans(
        self,
        db: AsyncSession,
        *,
        user_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[dict]:
        return await self.plan_repository.list_plans(
            db,
            user_id=user_id,
            is_active=is_active,
        )

    async def create_plan(self, db: AsyncSession, payload: PlanCreateRequest) -> dict:
        university_id = _parse_uuid(payload.university_id, "university_id")
        program_id = _parse_uuid(payload.program_id, "program_id")
        try:
            plan = await self.plan_repository.create_plan(
                db,
                user_id=payload.user_id,
                university_id=university_id,
                program_id=program_id,
                plan_name=payload.plan_name.strip(),
                description=payload.description,
                is_active=payload.is_active,
            )
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            logger.exception("Integrity error while creating normalized plan")
            raise _integrity_error("Plan could not be created") from exc
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("Database error while creating normalized plan")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            ) from exc

        created = await self.plan_repository.get_plan_by_id(db, plan.plan_id)
        if not created:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found after creation",
            )
        return created

    async def get_plan_by_id(self, db: AsyncSession, plan_id: str) -> dict:
        _parse_uuid(plan_id, "plan_id")
        plan = await self.plan_repository.get_plan_by_id(db, plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        return plan

    async def update_plan(
        self,
        db: AsyncSession,
        plan_id: str,
        payload: PlanUpdateRequest,
    ) -> dict:
        _parse_uuid(plan_id, "plan_id")
        plan = await self.plan_repository.get_plan_model(db, plan_id, include_courses=False)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        fields = payload.model_fields_set
        try:
            await self.plan_repository.update_plan(
                plan,
                plan_name=payload.plan_name.strip() if payload.plan_name is not None else None,
                description=payload.description,
                update_description="description" in fields,
                is_active=payload.is_active if "is_active" in fields else None,
            )
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            logger.exception("Integrity error while updating normalized plan=%s", plan_id)
            raise _integrity_error("Plan could not be updated") from exc
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("Database error while updating normalized plan=%s", plan_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            ) from exc

        return await self.get_plan_by_id(db, plan_id)

    async def deactivate_plan(self, db: AsyncSession, plan_id: str) -> dict:
        _parse_uuid(plan_id, "plan_id")
        plan = await self.plan_repository.get_plan_model(db, plan_id, include_courses=False)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        try:
            await self.plan_repository.deactivate_plan(plan)
            await db.commit()
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("Database error while deactivating normalized plan=%s", plan_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            ) from exc
        return await self.get_plan_by_id(db, plan_id)

    async def list_plan_courses(self, db: AsyncSession, plan_id: str) -> list[dict]:
        _parse_uuid(plan_id, "plan_id")
        await self._require_plan(db, plan_id)
        courses = await self.course_repository.list_plan_courses(db, plan_id)
        return courses or []

    async def add_plan_course(
        self,
        db: AsyncSession,
        plan_id: str,
        payload: PlanCourseCreateRequest,
    ) -> dict:
        parsed_plan_id = _parse_uuid(plan_id, "plan_id")
        course_id = _parse_uuid(payload.course_id, "course_id")
        planned_term_id = (
            _parse_uuid(payload.planned_term_id, "planned_term_id")
            if payload.planned_term_id
            else None
        )
        await self._require_plan(db, plan_id)

        try:
            await self.course_repository.add_plan_course(
                db,
                plan_id=parsed_plan_id,
                course_id=course_id,
                planned_term_id=planned_term_id,
                status=payload.status,
                notes=payload.notes,
            )
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            logger.exception("Integrity error while adding course to normalized plan=%s", plan_id)
            raise _integrity_error("Course could not be added to plan") from exc
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("Database error while adding course to normalized plan=%s", plan_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            ) from exc

        plan_course = await self.course_repository.get_plan_course(
            db,
            plan_id=plan_id,
            course_id=payload.course_id,
        )
        if not plan_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan course not found after creation",
            )
        return plan_course

    async def update_plan_course(
        self,
        db: AsyncSession,
        plan_id: str,
        course_id: str,
        payload: PlanCourseUpdateRequest,
    ) -> dict:
        _parse_uuid(plan_id, "plan_id")
        _parse_uuid(course_id, "course_id")
        plan_course = await self.course_repository.get_plan_course_model(
            db,
            plan_id=plan_id,
            course_id=course_id,
        )
        if not plan_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan course not found",
            )

        fields = payload.model_fields_set
        planned_term_id = None
        if "planned_term_id" in fields and payload.planned_term_id:
            planned_term_id = _parse_uuid(payload.planned_term_id, "planned_term_id")

        try:
            await self.course_repository.update_plan_course(
                plan_course,
                planned_term_id=planned_term_id,
                update_planned_term="planned_term_id" in fields,
                status=payload.status if "status" in fields else None,
                notes=payload.notes,
                update_notes="notes" in fields,
            )
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            logger.exception("Integrity error while updating plan course=%s/%s", plan_id, course_id)
            raise _integrity_error("Plan course could not be updated") from exc
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("Database error while updating plan course=%s/%s", plan_id, course_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            ) from exc

        updated = await self.course_repository.get_plan_course(
            db,
            plan_id=plan_id,
            course_id=course_id,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan course not found after update",
            )
        return updated

    async def delete_plan_course(self, db: AsyncSession, plan_id: str, course_id: str) -> None:
        _parse_uuid(plan_id, "plan_id")
        _parse_uuid(course_id, "course_id")
        plan_course = await self.course_repository.get_plan_course_model(
            db,
            plan_id=plan_id,
            course_id=course_id,
        )
        if not plan_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan course not found",
            )
        try:
            await self.course_repository.delete_plan_course(db, plan_course)
            await db.commit()
        except SQLAlchemyError as exc:
            await db.rollback()
            logger.exception("Database error while deleting plan course=%s/%s", plan_id, course_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            ) from exc

    async def _require_plan(self, db: AsyncSession, plan_id: str) -> None:
        plan = await self.plan_repository.get_plan_model(db, plan_id, include_courses=False)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")


normalized_plan_service = NormalizedPlanService()
