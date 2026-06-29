from __future__ import annotations

from time import perf_counter
from typing import Any

from app.student.domains.scheduling.engine.candidate_models import ScheduleCandidate
from app.student.domains.scheduling.engine.preference_scorer import PreferenceScorer


class PreferenceScoringService:
    """Applies deterministic preference scoring to metric-enriched candidates."""

    def __init__(self, scorer: PreferenceScorer | None = None) -> None:
        self.scorer = scorer or PreferenceScorer()

    def score_candidates(
        self,
        candidates: list[ScheduleCandidate],
        preferences: list[dict[str, Any]],
    ) -> tuple[list[ScheduleCandidate], dict]:
        started_at = perf_counter()
        scored_candidates = [self.scorer.score(candidate, preferences) for candidate in candidates]
        scoring_time_ms = max(0, round((perf_counter() - started_at) * 1000))
        return scored_candidates, {
            "candidate_count": len(scored_candidates),
            "scoring_version": "1.0",
            "scoring_time_ms": scoring_time_ms,
            "preference_count": len(preferences),
        }
