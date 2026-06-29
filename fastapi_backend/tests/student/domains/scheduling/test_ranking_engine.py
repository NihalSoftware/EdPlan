from __future__ import annotations

from datetime import time

from app.student.domains.scheduling.engine import (
    ScheduleCandidate,
    ScheduleConflict,
    ScheduleMetrics,
    ScheduleRankingConfig,
    ScheduleRankingEngine,
    ScheduleRankingService,
    ScheduleWarning,
)
from app.student.domains.scheduling.schemas.schedulepilot import (
    ScheduleCourse,
    ScheduleMeeting,
    ScheduleSection,
)


def _course(course_id: str = "course-1") -> ScheduleCourse:
    return ScheduleCourse(
        plan_course_id=f"pc-{course_id}",
        plan_id="plan-1",
        course_id=course_id,
        planned_term_id="term-1",
        status="Planned",
        course_code=course_id.upper(),
        course_name=f"{course_id} Name",
        credits=3,
        lecture_hours=3,
        lab_hours=0,
    )


def _section(section_id: str, course_id: str = "course-1") -> ScheduleSection:
    return ScheduleSection(
        section_id=section_id,
        offering_id=f"offering-{section_id}",
        course_id=course_id,
        term_id="term-1",
        offering_type="Lecture",
        section_number=section_id,
        crn=f"crn-{section_id}",
        instruction_method="In Person",
        capacity=30,
        enrolled=10,
        available_seats=20,
        status="Open",
    )


def _meeting(section_id: str, *, weekday: int = 1) -> ScheduleMeeting:
    return ScheduleMeeting(
        meeting_id=f"meeting-{section_id}",
        section_id=section_id,
        weekday=weekday,
        start_time=time(9, 0),
        end_time=time(10, 0),
        meeting_type="Class",
        is_async=False,
    )


def _metrics(**overrides) -> ScheduleMetrics:
    values = {
        "total_credits": 3,
        "earliest_start_time": time(9, 0),
        "latest_end_time": time(10, 0),
        "total_instruction_minutes": 60,
        "total_gap_minutes": 0,
        "average_gap_minutes": 0.0,
        "maximum_gap_minutes": 0,
        "campus_days": 1,
        "monday_classes": 1,
        "tuesday_classes": 0,
        "wednesday_classes": 0,
        "thursday_classes": 0,
        "friday_classes": 0,
        "saturday_classes": 0,
        "sunday_classes": 0,
        "online_section_count": 0,
        "hybrid_section_count": 0,
        "in_person_section_count": 1,
        "asynchronous_section_count": 0,
        "total_sections": 1,
        "open_sections": 1,
        "closed_sections": 0,
        "cancelled_sections": 0,
        "available_seat_count": 20,
        "total_capacity": 30,
        "total_enrollment": 10,
        "open_seat_ratio": 20 / 30,
        "total_meetings": 1,
        "synchronous_meetings": 1,
        "asynchronous_meetings": 0,
        "average_meeting_duration": 60.0,
        "longest_meeting_duration": 60,
        "total_courses": 1,
        "lecture_count": 1,
        "lab_count": 0,
        "discussion_count": 0,
        "other_component_count": 0,
    }
    values.update(overrides)
    return ScheduleMetrics(**values)


def _candidate(
    candidate_id: str,
    *,
    score: float = 50.0,
    feasible: bool = True,
    section_id: str | None = None,
    warning_count: int = 0,
    conflict_count: int = 0,
    **metric_overrides,
) -> ScheduleCandidate:
    section_id = section_id or f"section-{candidate_id}"
    return ScheduleCandidate(
        candidate_id=candidate_id,
        courses=[_course()],
        sections=[_section(section_id)],
        meetings=[_meeting(section_id)],
        warnings=[
            ScheduleWarning(warning_id=f"warning-{index}", type="test", message="warning")
            for index in range(warning_count)
        ],
        conflicts=[
            ScheduleConflict(conflict_id=f"conflict-{index}", type="test", message="conflict")
            for index in range(conflict_count)
        ],
        is_feasible=feasible,
        metrics=_metrics(**metric_overrides),
        score=score,
        normalized_score=score,
    )


def test_ranking_engine_orders_by_descending_normalized_score():
    options, duplicate_count = ScheduleRankingEngine().rank(
        [
            _candidate("candidate-b", score=70),
            _candidate("candidate-a", score=90),
            _candidate("candidate-c", score=80),
        ]
    )

    assert duplicate_count == 0
    assert [option.metadata["source_candidate_id"] for option in options] == [
        "candidate-a",
        "candidate-c",
        "candidate-b",
    ]
    assert [option.rank for option in options] == [1, 2, 3]


def test_ranking_engine_applies_deterministic_tie_breakers():
    options, _ = ScheduleRankingEngine().rank(
        [
            _candidate("candidate-d", score=80, total_gap_minutes=20, campus_days=2),
            _candidate("candidate-c", score=80, warning_count=1),
            _candidate("candidate-b", score=80, total_gap_minutes=10, campus_days=3),
            _candidate("candidate-a", score=80, total_gap_minutes=10, campus_days=2),
        ]
    )

    assert [option.metadata["source_candidate_id"] for option in options] == [
        "candidate-a",
        "candidate-b",
        "candidate-d",
        "candidate-c",
    ]


def test_ranking_engine_excludes_infeasible_candidates():
    options, _ = ScheduleRankingEngine().rank(
        [
            _candidate("candidate-infeasible", score=100, feasible=False),
            _candidate("candidate-feasible", score=40, feasible=True),
        ]
    )

    assert len(options) == 1
    assert options[0].metadata["source_candidate_id"] == "candidate-feasible"


def test_ranking_engine_maps_candidates_to_schedule_options():
    option = ScheduleRankingEngine().rank([_candidate("candidate-a", score=82)])[0][0]

    assert option.option_id == "schedule-option-000001"
    assert option.rank == 1
    assert option.normalized_score == 82
    assert option.selected_sections[0].section_id == "section-candidate-a"
    assert option.selected_meetings[0].meeting_id == "meeting-section-candidate-a"
    assert option.metrics is not None
    assert option.explanation.startswith("This schedule ranked highly")
    assert option.metadata["source_candidate_id"] == "candidate-a"
    assert option.metadata["ranking_version"] == "1.0"


def test_ranking_engine_generates_rule_based_tradeoffs():
    option = ScheduleRankingEngine().rank(
        [
            _candidate(
                "candidate-a",
                score=82,
                friday_classes=1,
                maximum_gap_minutes=120,
                latest_end_time=time(18, 0),
                hybrid_section_count=1,
                campus_days=4,
                open_seat_ratio=0.75,
            )
        ]
    )[0][0]

    assert option.tradeoffs == [
        "Friday class included",
        "Long gap included",
        "Evening class included",
        "Hybrid delivery included",
        "Uses 4 campus days",
        "High seat availability",
    ]


def test_ranking_engine_filters_duplicate_section_combinations():
    engine = ScheduleRankingEngine(config=ScheduleRankingConfig(max_options=10))
    options, duplicate_count = engine.rank(
        [
            _candidate("candidate-a", score=90, section_id="same-section"),
            _candidate("candidate-b", score=80, section_id="same-section"),
            _candidate("candidate-c", score=70, section_id="other-section"),
        ]
    )

    assert duplicate_count == 1
    assert [option.metadata["source_candidate_id"] for option in options] == [
        "candidate-a",
        "candidate-c",
    ]


def test_ranking_service_returns_metadata_and_top_option():
    result = ScheduleRankingService().rank_candidates(
        [
            _candidate("candidate-a", score=90),
            _candidate("candidate-b", score=50, feasible=False),
            _candidate("candidate-c", score=80),
        ]
    )

    assert result.top_option is not None
    assert result.top_option.metadata["source_candidate_id"] == "candidate-a"
    assert result.metadata.evaluated_candidates == 3
    assert result.metadata.feasible_candidates == 2
    assert result.metadata.ranked_candidates == 2
    assert result.metadata.returned_candidates == 2
    assert result.metadata.ranking_version == "1.0"


def test_ranking_service_is_deterministic_for_identical_inputs():
    candidates = [
        _candidate("candidate-b", score=80),
        _candidate("candidate-a", score=80),
    ]

    first = ScheduleRankingService().rank_candidates(candidates)
    second = ScheduleRankingService().rank_candidates(candidates)

    assert [option.model_dump(exclude={"metadata"}) for option in first.options] == [
        option.model_dump(exclude={"metadata"}) for option in second.options
    ]
    assert [option.metadata for option in first.options] == [
        option.metadata for option in second.options
    ]
