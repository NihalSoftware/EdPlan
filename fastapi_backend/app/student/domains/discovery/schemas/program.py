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
    degree: str
    total_credit_hours: int
    university: UniversitySummary


class CourseSummary(BaseModel):
    course_id: str
    program_id: str
    course_code: str
    code: str | None = None
    course_name: str
    credits: int
    lecture_hours: int = 0
    lab_hours: int = 0
    recommended_year: int | None = None
    year: int | str | None = None
    recommended_semester: str | None = None
    semester: str | None = None
    description: str | None = None


class ProgramDetail(ProgramSummary):
    average_annual_cost: str | None = None
    eligibility_criteria: str | None = None
    courses: list[CourseSummary] = Field(default_factory=list)
    years: list[dict] = Field(default_factory=list)


class ProgramListResponse(BaseModel):
    success: bool
    data: list[ProgramSummary]
    metadata: dict


class ProgramDetailResponse(BaseModel):
    success: bool
    data: ProgramDetail
