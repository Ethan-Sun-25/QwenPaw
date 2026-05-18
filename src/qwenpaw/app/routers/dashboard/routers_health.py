# -*- coding: utf-8 -*-
"""GET /health — health check."""

from fastapi import APIRouter

from .schemas import HealthResponse
from .utils import now_iso

router = APIRouter(tags=["dashboard-health"])


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        timestamp=now_iso(),
        message="Dashboard API healthy",
    )
