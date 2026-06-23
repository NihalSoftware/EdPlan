from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from app.student.domains.planning.schemas.normalized_plan import (
    PlanCreateRequest,
    PlanUpdateRequest,
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


class CreatePlanTool:
    name = "create_plan"
    description = "Create a student education plan"

    def __init__(self, service: "NormalizedPlanService | None" = None) -> None:
        self.service = service

    async def execute(
        self,
        db: "AsyncSession",
        payload: PlanCreateRequest | dict[str, Any],
    ) -> dict:
        service = self.service or _default_service()
        return await service.create_plan(db, coerce_payload(PlanCreateRequest, payload))


class UpdatePlanTool:
    name = "update_plan"
    description = "Update a student education plan"

    def __init__(self, service: "NormalizedPlanService | None" = None) -> None:
        self.service = service

    async def execute(
        self,
        db: "AsyncSession",
        plan_id: str,
        payload: PlanUpdateRequest | dict[str, Any],
    ) -> dict:
        service = self.service or _default_service()
        return await service.update_plan(
            db,
            plan_id,
            coerce_payload(PlanUpdateRequest, payload),
        )


class DeletePlanTool:
    name = "delete_plan"
    description = "Delete a student education plan"

    def __init__(self, service: "NormalizedPlanService | None" = None) -> None:
        self.service = service

    async def execute(self, db: "AsyncSession", plan_id: str) -> dict:
        service = self.service or _default_service()
        return await service.deactivate_plan(db, plan_id)


class GetPlanTool:
    name = "get_plan"
    description = "Get a student education plan"

    def __init__(self, service: "NormalizedPlanService | None" = None) -> None:
        self.service = service

    async def execute(self, db: "AsyncSession", plan_id: str) -> dict:
        service = self.service or _default_service()
        return await service.get_plan_by_id(db, plan_id)
