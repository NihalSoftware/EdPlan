from __future__ import annotations

from pydantic import BaseModel, Field


class ScoringWeights(BaseModel):
    base_score: float = 50.0
    infeasible_penalty: float = -40.0
    satisfied_bonus: float = 8.0
    violation_penalty: float = -10.0
    partial_bonus: float = 4.0
    small_penalty: float = -4.0
    gap_penalty_per_hour: float = -2.0
    campus_day_penalty: float = -3.0
    seat_availability_bonus: float = 6.0
    compact_gap_threshold_minutes: int = 60
    large_break_threshold_minutes: int = 90
    preferred_max_campus_days: int = 3
    morning_end_hour: int = 12
    afternoon_start_hour: int = 12
    afternoon_end_hour: int = 17
    evening_start_hour: int = 17
    max_score: float = 100.0
    min_score: float = 0.0
    supported_preferences: set[str] = Field(
        default_factory=lambda: {
            "morning_classes",
            "afternoon_classes",
            "evening_classes",
            "no_friday",
            "friday_only_if_required",
            "minimize_campus_days",
            "maximize_free_days",
            "online_only",
            "online_preferred",
            "hybrid_preferred",
            "in_person_preferred",
            "minimize_gaps",
            "maximize_back_to_back_classes",
            "avoid_large_breaks",
            "minimum_credits",
            "maximum_credits",
            "preferred_credit_range",
            "prefer_available_seats",
        }
    )


DEFAULT_SCORING_WEIGHTS = ScoringWeights()
