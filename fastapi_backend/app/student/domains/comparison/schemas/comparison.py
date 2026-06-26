from __future__ import annotations

from pydantic import BaseModel, Field


class UniversitySearchRequest(BaseModel):
    state: str | None = None
    city: str | None = None
    name: str | None = None
    limit: int = Field(default=10, ge=1, le=50)


class UniversityCompareRequest(BaseModel):
    university_ids: list[str] = Field(..., min_length=2, max_length=5)


class ProgramSearchRequest(BaseModel):
    university_id: str | None = None
    degree: str | None = None
    name: str | None = None
    limit: int = Field(default=20, ge=1, le=50)


class ProgramCompareRequest(BaseModel):
    program_ids: list[str] = Field(..., min_length=2, max_length=6)


class CareerPathCompareRequest(BaseModel):
    program_ids: list[str] = Field(..., min_length=2, max_length=6)
