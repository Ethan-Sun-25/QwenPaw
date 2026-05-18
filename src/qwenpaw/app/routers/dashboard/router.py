# -*- coding: utf-8 -*-
"""Dashboard APIRouter — prefix /api/dashboard, includes 6 sub-routers."""

from fastapi import APIRouter

from .routers_agents import router as agents_router
from .routers_health import router as health_router
from .routers_models import router as models_router
from .routers_overview import router as overview_router
from .routers_skills import router as skills_router
from .routers_tokens import router as tokens_router

router = APIRouter(
    prefix="/api/dashboard", tags=["dashboard"]
)

router.include_router(health_router)
router.include_router(overview_router)
router.include_router(tokens_router)
router.include_router(agents_router)
router.include_router(skills_router)
router.include_router(models_router)
