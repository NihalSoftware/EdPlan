from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from app.student.domains.planning.schemas.normalized_plan import (
    PlanCourseCreateRequest,
    PlanCourseUpdateRequest,
)
from app.student.domains.planning.tools._payloads import coerce_payload

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.student.domains.planning.services.normalized_plan_service import (
        NormalizedPlanService,
    )


def _default_service():
    from app.student.domains.planning.services.normalized_plan_service import (
        normalized_plan_service,
    )

    return normalized_plan_service


class AddCourseTool:
    name = "add_course"
    description = "Add a course to a student education plan"

    def __init__(self, service: "NormalizedPlanService | None" = None) -> None:
        self.service = service

    async def execute(
        self,
        db: "AsyncSession",
        plan_id: str,
        payload: PlanCourseCreateRequest | dict[str, Any],
    ) -> dict:
        service = self.service or _default_service()
        return await service.add_plan_course(
            db,
            plan_id,
            coerce_payload(PlanCourseCreateRequest, payload),
        )


class RemoveCourseTool:
    name = "remove_course"
    description = "Remove a course from a student education plan"

    def __init__(self, service: "NormalizedPlanService | None" = None) -> None:
        self.service = service

    async def execute(self, db: "AsyncSession", plan_id: str, course_id: str) -> None:
        service = self.service or _default_service()
        return await service.delete_plan_course(db, plan_id, course_id)


class MoveCourseTool:
    name = "move_course"
    description = "Move a planned course to another academic term"

    def __init__(self, service: "NormalizedPlanService | None" = None) -> None:
        self.service = service

    async def execute(
        self,
        db: "AsyncSession",
        plan_id: str,
        course_id: str,
        payload: PlanCourseUpdateRequest | dict[str, Any],
    ) -> dict:
        service = self.service or _default_service()
        return await service.update_plan_course(
            db,
            plan_id,
            course_id,
            coerce_payload(PlanCourseUpdateRequest, payload),
        )
