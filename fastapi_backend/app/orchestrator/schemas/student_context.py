from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StudentContext(BaseModel):
    """Shared student context contract for future orchestration modules."""

    user: dict[str, Any] | None = None
    plan: dict[str, Any] | None = None
    program: dict[str, Any] | None = None
    university: dict[str, Any] | None = None
    completed_courses: list[dict[str, Any]] = Field(default_factory=list)
    preferences: list[dict[str, Any]] = Field(default_factory=list)
    memory: list[dict[str, Any]] = Field(default_factory=list)
    career_goal: str | None = None
