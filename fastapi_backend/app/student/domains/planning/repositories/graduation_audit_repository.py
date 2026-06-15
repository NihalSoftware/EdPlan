from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

# Initialize Base metadata before importing model packages from a cold route import.
from app.db.base import Base as _Base  # noqa: F401
from app.student.domains.discovery.models import Course
from app.student.domains.planning.models import EdPlan, PlanCourse


class GraduationAuditRepository:
    async def get_plan(self, db: AsyncSession, plan_id: uuid.UUID) -> EdPlan | None:
        result = await db.execute(
            select(EdPlan)
            .options(
                joinedload(EdPlan.program),
                selectinload(EdPlan.courses).joinedload(PlanCourse.course),
            )
            .where(EdPlan.plan_id == plan_id)
        )
        return result.scalar_one_or_none()

    async def list_program_courses(
        self,
        db: AsyncSession,
        program_id: uuid.UUID,
    ) -> list[Course]:
        result = await db.execute(
            select(Course)
            .where(Course.program_id == program_id)
            .order_by(
                Course.recommended_year,
                Course.recommended_semester,
                Course.course_code,
            )
        )
        return list(result.scalars().all())


graduation_audit_repository = GraduationAuditRepository()
