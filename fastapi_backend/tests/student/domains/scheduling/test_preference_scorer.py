from __future__ import annotations

from datetime import time

from app.student.domains.scheduling.engine import (
    PreferenceScorer,
    PreferenceScoringService,
    ScheduleCandidate,
    ScheduleMetrics,
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
        course_code="CS 101",
        course_name="Intro",
        credits=3,
        lecture_hours=3,
        lab_hours=0,
    )


def _section(section_id: str = "section-1", course_id: str = "course-1") -> ScheduleSection:
    return ScheduleSection(
        section_id=section_id,
        offering_id=f"offering-{course_id}",
        course_id=course_id,
        term_id="term-1",
        offering_type="Lecture",
        section_number="001",
        crn="12345",
        instruction_method="In Person",
        capacity=30,
        enrolled=10,
        available_seats=20,
        status="Open",
    )


def _meeting(section_id: str = "section-1") -> ScheduleMeeting:
    return ScheduleMeeting(
        meeting_id=f"meeting-{section_id}",
        section_id=section_id,
        weekday=1,
        start_time=time(9, 0),
        end_time=time(10, 15),
        meeting_type="Class",
        is_async=False,
    )


def _metrics(**overrides) -> ScheduleMetrics:
    values = {
        "total_credits": 3,
        "earliest_start_time": time(9, 0),
        "latest_end_time": time(10, 15),
        "total_instruction_minutes": 75,
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
        "average_meeting_duration": 75.0,
        "longest_meeting_duration": 75,
        "total_courses": 1,
        "lecture_count": 1,
        "lab_count": 0,
        "discussion_count": 0,
        "other_component_count": 0,
    }
    values.update(overrides)
    return ScheduleMetrics(**values)


def _candidate(**metric_overrides) -> ScheduleCandidate:
    return ScheduleCandidate(
        candidate_id="candidate-000001",
        courses=[_course()],
        sections=[_section()],
        meetings=[_meeting()],
        is_feasible=True,
        metrics=_metrics(**metric_overrides),
    )


def test_preference_scorer_rewards_satisfied_morning_preference():
    scored = PreferenceScorer().score(
        _candidate(),
        [{"key": "class_preference", "value": "morning classes"}],
    )

    assert scored.score == 58.0
    assert scored.normalized_score == 58.0
    assert scored.scoring_summary.evaluated_preferences == 1
    assert scored.scoring_summary.satisfied_preferences == ["morning_classes"]
    assert scored.scoring_summary.violated_preferences == []


def test_preference_scorer_penalizes_unsatisfied_evening_preference():
    scored = PreferenceScorer().score(
        _candidate(),
        [{"key": "class_preference", "value": "evening classes"}],
    )

    assert scored.normalized_score == 40.0
    assert scored.scoring_summary.applied_penalty_count == 1
    assert scored.scoring_summary.violated_preferences == ["evening_classes"]


def test_preference_scorer_scores_friday_and_gap_preferences_from_metrics():
    scored = PreferenceScorer().score(
        _candidate(friday_classes=1, total_gap_minutes=180, maximum_gap_minutes=180),
        [
            {"key": "schedule_preference", "value": "no classes on Friday"},
            {"key": "schedule_preference", "value": "compact schedule"},
            {"key": "schedule_preference", "value": "avoid large breaks"},
        ],
    )

    assert scored.normalized_score == 26.0
    assert scored.scoring_summary.violated_preferences == [
        "no_friday",
        "minimize_gaps",
        "avoid_large_breaks",
    ]


def test_preference_scorer_scores_delivery_mode_and_available_seats():
    scored = PreferenceScorer().score(
        _candidate(online_section_count=1, in_person_section_count=1, total_sections=2),
        [
            {"key": "delivery", "value": "online preferred"},
            {"key": "availability", "value": "prefer available seats"},
        ],
    )

    assert scored.normalized_score == 58.0
    assert scored.scoring_summary.applied_bonus_count == 2
    assert scored.scoring_summary.satisfied_preferences == [
        "online_preferred",
        "prefer_available_seats",
    ]


def test_preference_scorer_scores_credit_preferences():
    scored = PreferenceScorer().score(
        _candidate(total_credits=15),
        [
            {"key": "credits", "value": "12-18 credits"},
            {"key": "maximum_credits", "value": 12},
        ],
    )

    assert scored.normalized_score == 48.0
    assert scored.scoring_summary.satisfied_preferences == ["preferred_credit_range"]
    assert scored.scoring_summary.violated_preferences == ["maximum_credits"]


def test_preference_scorer_penalizes_infeasible_candidates():
    candidate = _candidate()
    candidate.is_feasible = False

    scored = PreferenceScorer().score(candidate, [])

    assert scored.normalized_score == 10.0
    assert scored.scoring_summary.violated_preferences == ["candidate_feasibility"]
    assert scored.scoring_summary.evaluations[0].preference_key == "candidate_feasibility"


def test_preference_scoring_service_scores_candidates_without_ranking_them():
    candidates = [_candidate(), _candidate()]

    scored_candidates, metadata = PreferenceScoringService().score_candidates(
        candidates,
        [{"key": "class_preference", "value": "morning classes"}],
    )

    assert len(scored_candidates) == 2
    assert [candidate.candidate_id for candidate in scored_candidates] == [
        "candidate-000001",
        "candidate-000001",
    ]
    assert all(candidate.normalized_score == 58.0 for candidate in scored_candidates)
    assert all(not hasattr(candidate, "rank") for candidate in scored_candidates)
    assert metadata["candidate_count"] == 2
    assert metadata["scoring_version"] == "1.0"
    assert metadata["preference_count"] == 1
