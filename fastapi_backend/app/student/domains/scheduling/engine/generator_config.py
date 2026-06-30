from __future__ import annotations

from pydantic import BaseModel, Field


class ScheduleGeneratorConfig(BaseModel):
    """Configuration for deterministic schedule candidate generation."""

    max_candidate_count: int = Field(default=500, gt=0)
