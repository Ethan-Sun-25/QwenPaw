# -*- coding: utf-8 -*-
"""GET /agents/stats — Agent-level statistics."""

from typing import Optional

from fastapi import APIRouter, Query

from .aggregators import agents_stats
from .schemas import AgentsStatsResponse

router = APIRouter(tags=["dashboard-agents"])


@router.get(
    "/agents/stats", response_model=AgentsStatsResponse
)
def get_agents_stats(
    range: str = Query(
        "today",
        alias="range",
        description="today|7d|30d|custom",
    ),
    agent_id: Optional[str] = Query(
        None, description="Filter by agent_id"
    ),
    start: Optional[str] = Query(
        None, description="ISO date start"
    ),
    end: Optional[str] = Query(
        None, description="ISO date end"
    ),
):
    return agents_stats(
        range_=range,
        agent_id=agent_id,
        start=start,
        end=end,
    )
