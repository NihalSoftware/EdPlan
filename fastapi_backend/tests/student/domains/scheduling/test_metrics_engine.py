from __future__ import annotations

from datetime import time

from app.student.domains.scheduling.engine import ScheduleCandidate, ScheduleMetricsEngine
from app.student.domains.scheduling.schemas.schedulepilot import (
    ScheduleCourse,
    ScheduleMeeting,
    ScheduleSection,
)


def _course(course_id: str, credits: int = 3) -> ScheduleCourse:
    return ScheduleCourse(
        plan_course_id=f"pc-{course_id}",
        plan_id="plan-1",
        course_id=course_id,
        status="Planned",
        course_code=course_id.upper(),
        course_name=f"{course_id} Name",
        credits=credits,
        lecture_hours=3,
        lab_hours=0,
    )


def _section(
    section_id: str,
    course_id: str,
    *,
    instruction_method: str = "In Person",
    status: str = "Open",
    capacity: int | None = 30,
    enrolled: int | None = 10,
    available_seats: int | None = 20,
    offering_type: str | None = "Lecture",
) -> ScheduleSection:
    return ScheduleSection(
        section_id=section_id,
        offering_id=f"offering-{section_id}",
        course_id=course_id,
        term_id="term-1",
        offering_type=offering_type,
        section_number=section_id,
        crn=f"crn-{section_id}",
        instruction_method=instruction_method,
        capacity=capacity,
        enrolled=enrolled,
        available_seats=available_seats,
        status=status,
    )


def _meeting(
    meeting_id: str,
    section_id: str,
    *,
    weekday: int | None = 1,
    start_time: time | None = time(9, 0),
    end_time: time | None = time(10, 0),
    is_async: bool = False,
) -> ScheduleMeeting:
    return ScheduleMeeting(
        meeting_id=meeting_id,
        section_id=section_id,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        meeting_type="Online Async" if is_async else "Class",
        is_async=is_async,
    )


def _candidate(courses=None, sections=None, meetings=None) -> ScheduleCandidate:
    return ScheduleCandidate(
        candidate_id="candidate-000001",
        courses=courses or [],
        sections=sections or [],
        meetings=meetings or [],
        is_feasible=True,
    )


def test_metrics_engine_computes_empty_schedule_metrics():
    enriched = ScheduleMetricsEngine().compute(_candidate())

    assert enriched.metrics.total_credits == 0
    assert enriched.metrics.total_courses == 0
    assert enriched.metrics.total_sections == 0
    assert enriched.metrics.total_meetings == 0
    assert enriched.metrics.earliest_start_time is None
    assert enriched.metrics.average_gap_minutes is None
    assert enriched.metrics_summary.metric_version == "1.0"
    assert enriched.metrics_summary.meeting_count == 0


def test_metrics_engine_computes_credit_and_section_metrics():
    enriched = ScheduleMetricsEngine().compute(
        _candidate(
            courses=[_course("course-a", 3), _course("course-b", 4)],
            sections=[
                _section("section-a", "course-a", status="Open"),
                _section("section-b", "course-b", status="Closed"),
                _section("section-c", "course-b", status="Cancelled"),
            ],
        )
    )

    assert enriched.metrics.total_credits == 7
    assert enriched.metrics.total_courses == 2
    assert enriched.metrics.total_sections == 3
    assert enriched.metrics.open_sections == 1
    assert enriched.metrics.closed_sections == 1
    assert enriched.metrics.cancelled_sections == 1


def test_metrics_engine_computes_time_and_gap_metrics_by_weekday():
    enriched = ScheduleMetricsEngine().compute(
        _candidate(
            meetings=[
                _meeting("m1", "s1", weekday=1, start_time=time(9, 0), end_time=time(10, 0)),
                _meeting("m2", "s2", weekday=1, start_time=time(11, 0), end_time=time(12, 0)),
                _meeting("m3", "s3", weekday=2, start_time=time(8, 30), end_time=time(9, 30)),
            ]
        )
    )

    assert enriched.metrics.earliest_start_time == time(8, 30)
    assert enriched.metrics.latest_end_time == time(12, 0)
    assert enriched.metrics.total_instruction_minutes == 180
    assert enriched.metrics.total_gap_minutes == 60
    assert enriched.metrics.average_gap_minutes == 60
    assert enriched.metrics.maximum_gap_minutes == 60
    assert enriched.metrics.campus_days == 2
    assert enriched.metrics.monday_classes == 2
    assert enriched.metrics.tuesday_classes == 1


def test_metrics_engine_treats_adjacent_meetings_as_no_gap():
    enriched = ScheduleMetricsEngine().compute(
        _candidate(
            meetings=[
                _meeting("m1", "s1", start_time=time(9, 0), end_time=time(10, 0)),
                _meeting("m2", "s2", start_time=time(10, 0), end_time=time(11, 0)),
            ]
        )
    )

    assert enriched.metrics.total_gap_minutes == 0
    assert enriched.metrics.average_gap_minutes is None
    assert enriched.metrics.maximum_gap_minutes is None


def test_metrics_engine_computes_delivery_and_async_metrics():
    enriched = ScheduleMetricsEngine().compute(
        _candidate(
            sections=[
                _section("s1", "c1", instruction_method="Online"),
                _section("s2", "c2", instruction_method="Hybrid"),
                _section("s3", "c3", instruction_method="In Person"),
            ],
            meetings=[
                _meeting("m1", "s1", weekday=None, start_time=None, end_time=None, is_async=True),
                _meeting("m2", "s2"),
            ],
        )
    )

    assert enriched.metrics.online_section_count == 1
    assert enriched.metrics.hybrid_section_count == 1
    assert enriched.metrics.in_person_section_count == 1
    assert enriched.metrics.asynchronous_section_count == 1
    assert enriched.metrics.total_meetings == 2
    assert enriched.metrics.synchronous_meetings == 1
    assert enriched.metrics.asynchronous_meetings == 1
    assert enriched.metrics.average_meeting_duration == 60
    assert enriched.metrics.longest_meeting_duration == 60


def test_metrics_engine_computes_capacity_ratio_and_nulls_missing_capacity():
    complete = ScheduleMetricsEngine().compute(
        _candidate(
            sections=[
                _section("s1", "c1", capacity=20, enrolled=15, available_seats=5),
                _section("s2", "c2", capacity=30, enrolled=10, available_seats=20),
            ]
        )
    )

    assert complete.metrics.available_seat_count == 25
    assert complete.metrics.total_capacity == 50
    assert complete.metrics.total_enrollment == 25
    assert complete.metrics.open_seat_ratio == 0.5

    incomplete = ScheduleMetricsEngine().compute(
        _candidate(sections=[_section("s1", "c1", capacity=None)])
    )

    assert incomplete.metrics.available_seat_count is None
    assert incomplete.metrics.total_capacity is None
    assert incomplete.metrics.total_enrollment is None
    assert incomplete.metrics.open_seat_ratio is None


def test_metrics_engine_computes_component_counts_from_section_offering_type():
    enriched = ScheduleMetricsEngine().compute(
        _candidate(
            sections=[
                _section("s1", "c1", offering_type="Lecture"),
                _section("s2", "c1", offering_type="Lab"),
                _section("s3", "c2", offering_type="Recitation"),
                _section("s4", "c3", offering_type="Online"),
                _section("s5", "c4", offering_type="Lecture+Lab"),
            ]
        )
    )

    assert enriched.metrics.lecture_count == 2
    assert enriched.metrics.lab_count == 2
    assert enriched.metrics.discussion_count == 1
    assert enriched.metrics.other_component_count == 1


def test_metrics_engine_is_deterministic_for_metric_values():
    candidate = _candidate(
        courses=[_course("course-a", 3)],
        sections=[_section("section-a", "course-a")],
        meetings=[_meeting("meeting-a", "section-a")],
    )

    first = ScheduleMetricsEngine().compute(candidate)
    second = ScheduleMetricsEngine().compute(candidate)

    assert first.metrics == second.metrics
    assert first.metrics_summary.metric_version == second.metrics_summary.metric_version
    assert first.metrics_summary.meeting_count == second.metrics_summary.meeting_count
    assert first.metrics_summary.section_count == second.metrics_summary.section_count
