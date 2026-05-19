# -*- coding: utf-8 -*-
"""GET /overview — 12 KPI overview."""

from typing import Optional

from fastapi import APIRouter, Query

from .aggregators import overview_metrics
from .schemas import OverviewResponse

router = APIRouter(tags=["dashboard-overview"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview(
    range: str = Query(
        "today",
        alias="range",
        description="today|7d|30d|custom",
    ),
    start: Optional[str] = Query(
        None, description="ISO date start"
    ),
    end: Optional[str] = Query(
        None, description="ISO date end"
    ),
):
    return overview_metrics(
        range_=range, start=start, end=end
    )
