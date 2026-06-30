from __future__ import annotations

from datetime import date, time

from app.student.domains.scheduling.engine import CandidateGenerator, ScheduleGeneratorConfig
from app.student.domains.scheduling.schemas.schedulepilot import (
    ScheduleCourse,
    ScheduleCourseOffering,
    ScheduleMeeting,
    ScheduleRetrievalContext,
    ScheduleSection,
    ScheduleStudentPlan,
    ScheduleTerm,
)


def _plan() -> ScheduleStudentPlan:
    return ScheduleStudentPlan(
        plan_id="plan-1",
        user_id=1,
        university_id="university-1",
        program_id="program-1",
        plan_name="Primary Plan",
        is_active=True,
    )


def _term() -> ScheduleTerm:
    return ScheduleTerm(
        term_id="term-1",
        term_name="Fall 2026",
        start_date=date(2026, 8, 17),
        end_date=date(2026, 12, 11),
        is_active=True,
    )


def _course(course_id: str, code: str) -> ScheduleCourse:
    return ScheduleCourse(
        plan_course_id=f"pc-{course_id}",
        plan_id="plan-1",
        course_id=course_id,
        planned_term_id="term-1",
        status="Planned",
        course_code=code,
        course_name=f"{code} Name",
        credits=3,
        lecture_hours=3,
        lab_hours=0,
    )


def _offering(course_id: str, offering_id: str, offering_type: str = "Lecture"):
    return ScheduleCourseOffering(
        offering_id=offering_id,
        course_id=course_id,
        term_id="term-1",
        offering_type=offering_type,
        course_code=course_id.upper(),
        course_name=f"{course_id} Name",
        credits=3,
        term=_term(),
    )


def _section(course_id: str, offering_id: str, section_id: str, number: str):
    return ScheduleSection(
        section_id=section_id,
        offering_id=offering_id,
        course_id=course_id,
        term_id="term-1",
        section_number=number,
        crn=f"crn-{section_id}",
        instruction_method="In Person",
        capacity=30,
        enrolled=10,
        available_seats=20,
        status="Open",
    )


def _meeting(section_id: str, meeting_id: str):
    return ScheduleMeeting(
        meeting_id=meeting_id,
        section_id=section_id,
        weekday=1,
        start_time=time(9, 0),
        end_time=time(10, 15),
        meeting_type="Class",
        is_async=False,
    )


def _context(courses, offerings=None, sections=None, meetings=None):
    return ScheduleRetrievalContext(
        plan=_plan(),
        courses=courses,
        terms=[_term()],
        offerings=offerings or [],
        sections=sections or [],
        meetings=meetings or [],
    )


def test_candidate_generator_returns_no_candidates_for_empty_plan():
    result = CandidateGenerator().generate(_context([]))

    assert result.candidates == []
    assert result.metadata.generated_count == 0
    assert result.metadata.truncated is False


def test_candidate_generator_builds_single_course_candidates():
    course = _course("course-a", "CS 101")
    offering = _offering("course-a", "offering-a")
    section = _section("course-a", "offering-a", "section-a", "001")
    meeting = _meeting("section-a", "meeting-a")

    result = CandidateGenerator().generate(_context([course], [offering], [section], [meeting]))

    assert result.metadata.generated_count == 1
    assert result.candidates[0].candidate_id == "candidate-000001"
    assert result.candidates[0].courses == [course]
    assert result.candidates[0].sections == [section]
    assert result.candidates[0].meetings == [meeting]
    assert result.candidates[0].conflicts == []
    assert result.candidates[0].warnings == []


def test_candidate_generator_builds_cartesian_product_for_multiple_courses():
    course_a = _course("course-a", "CS 101")
    course_b = _course("course-b", "MATH 101")
    offering_a = _offering("course-a", "offering-a")
    offering_b = _offering("course-b", "offering-b")
    sections = [
        _section("course-a", "offering-a", "section-a1", "001"),
        _section("course-a", "offering-a", "section-a2", "002"),
        _section("course-b", "offering-b", "section-b1", "001"),
        _section("course-b", "offering-b", "section-b2", "002"),
    ]

    result = CandidateGenerator().generate(
        _context([course_a, course_b], [offering_a, offering_b], sections)
    )

    assert result.metadata.generated_count == 4
    assert [candidate.candidate_id for candidate in result.candidates] == [
        "candidate-000001",
        "candidate-000002",
        "candidate-000003",
        "candidate-000004",
    ]
    assert [
        [section.section_id for section in candidate.sections] for candidate in result.candidates
    ] == [
        ["section-a1", "section-b1"],
        ["section-a1", "section-b2"],
        ["section-a2", "section-b1"],
        ["section-a2", "section-b2"],
    ]


def test_candidate_generator_supports_multiple_required_components():
    course = _course("course-a", "BIOL 101")
    lecture = _offering("course-a", "offering-lecture", "Lecture")
    lab = _offering("course-a", "offering-lab", "Lab")
    sections = [
        _section("course-a", "offering-lecture", "lecture-001", "001"),
        _section("course-a", "offering-lab", "lab-001", "001"),
        _section("course-a", "offering-lab", "lab-002", "002"),
    ]

    result = CandidateGenerator().generate(_context([course], [lecture, lab], sections))

    assert result.metadata.generated_count == 2
    assert [
        [section.section_id for section in candidate.sections] for candidate in result.candidates
    ] == [["lecture-001", "lab-001"], ["lecture-001", "lab-002"]]
    assert result.candidates[0].metadata["component_count"] == 2


def test_candidate_generator_respects_max_candidate_cap():
    course_a = _course("course-a", "CS 101")
    course_b = _course("course-b", "MATH 101")
    offering_a = _offering("course-a", "offering-a")
    offering_b = _offering("course-b", "offering-b")
    sections = [
        _section("course-a", "offering-a", "section-a1", "001"),
        _section("course-a", "offering-a", "section-a2", "002"),
        _section("course-b", "offering-b", "section-b1", "001"),
        _section("course-b", "offering-b", "section-b2", "002"),
    ]

    result = CandidateGenerator(ScheduleGeneratorConfig(max_candidate_count=3)).generate(
        _context([course_a, course_b], [offering_a, offering_b], sections)
    )

    assert result.metadata.generated_count == 3
    assert result.metadata.truncated is True
    assert result.metadata.max_candidate_count == 3


def test_candidate_generator_reports_missing_offerings_and_sections():
    course = _course("course-a", "CS 101")
    no_offerings = CandidateGenerator().generate(_context([course]))
    assert no_offerings.candidates == []
    assert no_offerings.warnings == ["No offerings found for course course-a."]

    offering = _offering("course-a", "offering-a")
    no_sections = CandidateGenerator().generate(_context([course], [offering]))
    assert no_sections.candidates == []
    assert no_sections.warnings == ["No sections found for course course-a component Lecture."]
