from pydantic import BaseModel, Field


class UniversitySummary(BaseModel):
    university_id: str
    university_name: str
    city: str | None = None
    state: str | None = None
    website: str | None = None


class ProgramSummary(BaseModel):
    program_id: str
    program_name: str
    degree: str | None = None
    total_credit_hours: int | None = None
    university: UniversitySummary


class ProgramDetail(ProgramSummary):
    average_annual_cost: str | None = None
    eligibility_criteria: str | None = None
    years: list[dict] = Field(default_factory=list)


class ProgramListResponse(BaseModel):
    success: bool
    data: list[ProgramSummary]
    metadata: dict


class ProgramDetailResponse(BaseModel):
    success: bool
    data: ProgramDetail
