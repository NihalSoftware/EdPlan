from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agentic import WorkflowEvent

CONTEXT_LOADED = "CONTEXT_LOADED"
INTENT_IDENTIFIED = "INTENT_IDENTIFIED"
MODULES_SELECTED = "MODULES_SELECTED"
MODULE_EXECUTION_STARTED = "MODULE_EXECUTION_STARTED"
MODULE_EXECUTION_COMPLETED = "MODULE_EXECUTION_COMPLETED"
RESPONSE_COMPOSED = "RESPONSE_COMPOSED"
MEMORY_UPDATE_STARTED = "MEMORY_UPDATE_STARTED"
MEMORY_UPDATE_COMPLETED = "MEMORY_UPDATE_COMPLETED"
MEMORY_UPDATE_FAILED = "MEMORY_UPDATE_FAILED"
FAILURE = "FAILURE"


class WorkflowTracker:
    """Persists durable workflow events for an orchestrator run."""

    def __init__(self, db: AsyncSession | None) -> None:
        self.db = db

    async def record_event(
        self,
        run_id: UUID | None,
        event_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowEvent | None:
        if self.db is None or run_id is None:
            return None
        event = WorkflowEvent(
            event_id=uuid4(),
            run_id=run_id,
            event_type=event_type,
            event_metadata=metadata or {},
        )
        self.db.add(event)
        await self._commit()
        return event

    async def _commit(self) -> None:
        if self.db is None:
            return
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
