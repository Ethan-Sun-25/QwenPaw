# -*- coding: utf-8 -*-
"""GET /tokens — Token consumption timeline and by-model."""

from typing import Optional

from fastapi import APIRouter, Query

from .aggregators import tokens_timeseries
from .schemas import TokensResponse

router = APIRouter(tags=["dashboard-tokens"])


@router.get("/tokens", response_model=TokensResponse)
def get_tokens(
    range: str = Query(
        "today",
        alias="range",
        description="today|7d|30d|custom",
    ),
    group_by: str = Query("day", description="day|model"),
    start: Optional[str] = Query(
        None, description="ISO date start"
    ),
    end: Optional[str] = Query(
        None, description="ISO date end"
    ),
):
    return tokens_timeseries(
        range_=range,
        group_by=group_by,
        start=start,
        end=end,
    )
