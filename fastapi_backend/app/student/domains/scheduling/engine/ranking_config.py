from __future__ import annotations

from pydantic import BaseModel


class ScheduleRankingConfig(BaseModel):
    max_options: int = 10
    enforce_unique_section_sets: bool = True


DEFAULT_RANKING_CONFIG = ScheduleRankingConfig()
