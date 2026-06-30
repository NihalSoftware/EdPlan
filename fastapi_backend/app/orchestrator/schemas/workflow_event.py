from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WorkflowEvent(BaseModel):
    """In-memory event emitted while the orchestration workflow runs."""

    event_type: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: dict[str, Any] = Field(default_factory=dict)

