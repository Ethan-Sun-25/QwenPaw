# -*- coding: utf-8 -*-
"""GET /skills/stats — Skill call leaderboard."""

from typing import Optional

from fastapi import APIRouter, Query

from .aggregators import skills_stats
from .schemas import SkillsStatsResponse

router = APIRouter(tags=["dashboard-skills"])


@router.get(
    "/skills/stats", response_model=SkillsStatsResponse
)
def get_skills_stats(
    range: str = Query(
        "today",
        alias="range",
        description="today|7d|30d|custom",
    ),
    top: int = Query(
        10, ge=1, le=100, description="Top N skills"
    ),
    start: Optional[str] = Query(
        None, description="ISO date start"
    ),
    end: Optional[str] = Query(
        None, description="ISO date end"
    ),
):
    return skills_stats(
        range_=range, top=top, start=start, end=end
    )
