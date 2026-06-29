from __future__ import annotations

from time import perf_counter

from app.student.domains.scheduling.engine.candidate_models import ScheduleCandidate
from app.student.domains.scheduling.engine.metrics_engine import ScheduleMetricsEngine


class ScheduleMetricsService:
    """Enriches validated candidates with objective schedule metrics."""

    def __init__(self, metrics_engine: ScheduleMetricsEngine | None = None) -> None:
        self.metrics_engine = metrics_engine or ScheduleMetricsEngine()

    def compute_for_candidates(
        self,
        candidates: list[ScheduleCandidate],
    ) -> tuple[list[ScheduleCandidate], dict]:
        started_at = perf_counter()
        enriched_candidates = self.metrics_engine.compute_many(candidates)
        computation_time_ms = max(0, round((perf_counter() - started_at) * 1000))
        return enriched_candidates, {
            "candidate_count": len(enriched_candidates),
            "metric_version": "1.0",
            "computation_time_ms": computation_time_ms,
        }
