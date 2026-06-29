from __future__ import annotations

from time import perf_counter

from app.student.domains.scheduling.engine.candidate_models import (
    ScheduleCandidate,
    ScheduleRankingMetadata,
    ScheduleRankingResult,
)
from app.student.domains.scheduling.engine.ranking_config import (
    DEFAULT_RANKING_CONFIG,
    ScheduleRankingConfig,
)
from app.student.domains.scheduling.engine.ranking_engine import ScheduleRankingEngine


class ScheduleRankingService:
    """Coordinates deterministic schedule ranking and metadata generation."""

    def __init__(
        self,
        engine: ScheduleRankingEngine | None = None,
        config: ScheduleRankingConfig | None = None,
    ) -> None:
        self.config = config or DEFAULT_RANKING_CONFIG
        self.engine = engine or ScheduleRankingEngine(config=self.config)

    def rank_candidates(self, candidates: list[ScheduleCandidate]) -> ScheduleRankingResult:
        started_at = perf_counter()
        options, duplicate_count = self.engine.rank(candidates)
        ranking_time_ms = max(0, round((perf_counter() - started_at) * 1000))
        feasible_count = len(
            [candidate for candidate in candidates if candidate.is_feasible is True]
        )
        metadata = ScheduleRankingMetadata(
            evaluated_candidates=len(candidates),
            feasible_candidates=feasible_count,
            ranked_candidates=len(options),
            returned_candidates=len(options),
            ranking_time_ms=ranking_time_ms,
            duplicate_candidates_filtered=duplicate_count,
            max_options=self.config.max_options,
        )
        return ScheduleRankingResult(
            options=options,
            top_option=options[0] if options else None,
            metadata=metadata,
        )
