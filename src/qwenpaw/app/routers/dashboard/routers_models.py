# -*- coding: utf-8 -*-
"""GET /models/stats — Model call distribution."""

from typing import Optional

from fastapi import APIRouter, Query

from .aggregators import models_stats
from .schemas import ModelsStatsResponse

router = APIRouter(tags=["dashboard-models"])


@router.get(
    "/models/stats", response_model=ModelsStatsResponse
)
def get_models_stats(
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
    return models_stats(
        range_=range, start=start, end=end
    )
