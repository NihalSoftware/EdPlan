from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel

from app.student.domains.discovery.schemas.course import CourseSummary


class AcademicTermSummary(BaseModel):
    term_id: str
    term_name: str
    start_date: date
    end_date: date
    is_active: bool


class CourseOfferingSummary(BaseModel):
    offering_id: str
    course_id: str
    term_id: str
    offering_type: str
    course: CourseSummary
    term: AcademicTermSummary


class SectionSummary(BaseModel):
    section_id: str
    offering_id: str
    section_number: str
    crn: str
    campus: str | None = None
    instructor: str | None = None
    instruction_method: str
    capacity: int
    enrolled: int
    status: str


class SectionDetail(SectionSummary):
    offering: CourseOfferingSummary


class SectionMeetingSummary(BaseModel):
    meeting_id: str
    section_id: str
    weekday: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    building: str | None = None
    room: str | None = None
    meeting_type: str


class AcademicTermListResponse(BaseModel):
    success: bool
    data: list[AcademicTermSummary]
    metadata: dict


class AcademicTermDetailResponse(BaseModel):
    success: bool
    data: AcademicTermSummary


class CourseOfferingListResponse(BaseModel):
    success: bool
    data: list[CourseOfferingSummary]
    metadata: dict


class CourseOfferingDetailResponse(BaseModel):
    success: bool
    data: CourseOfferingSummary


class SectionListResponse(BaseModel):
    success: bool
    data: list[SectionSummary]
    metadata: dict


class SectionDetailResponse(BaseModel):
    success: bool
    data: SectionDetail


class SectionMeetingListResponse(BaseModel):
    success: bool
    data: list[SectionMeetingSummary]
    metadata: dict
