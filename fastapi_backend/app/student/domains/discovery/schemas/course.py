from __future__ import annotations

from pydantic import BaseModel, Field

from app.student.domains.discovery.schemas.program import ProgramSummary


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


class CoursePrerequisiteResponse(BaseModel):
    id: str
    course_id: str
    prerequisite_course_id: str
    course: CourseSummary


class CourseCorequisiteResponse(BaseModel):
    id: str
    course_id: str
    corequisite_course_id: str
    course: CourseSummary


class CourseDetail(CourseSummary):
    program: ProgramSummary
    prerequisites: list[CoursePrerequisiteResponse] = Field(default_factory=list)
    corequisites: list[CourseCorequisiteResponse] = Field(default_factory=list)


class CourseListResponse(BaseModel):
    success: bool
    data: list[CourseSummary]
    metadata: dict


class CourseDetailResponse(BaseModel):
    success: bool
    data: CourseDetail


class CoursePrerequisiteListResponse(BaseModel):
    success: bool
    data: list[CoursePrerequisiteResponse]
    metadata: dict


class CourseCorequisiteListResponse(BaseModel):
    success: bool
    data: list[CourseCorequisiteResponse]
    metadata: dict
