# -*- coding: utf-8 -*-
"""Pydantic v2 response models — matches API-CONTRACT.md."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


# ── Common ───────────────────────────────────────────────────


class Period(BaseModel):
    start_date: str = ""
    end_date: str = ""
    range_type: str = "today"


class ErrorResponse(BaseModel):
    error: str = ""
    code: str = ""
    message: str = ""
    details: dict = Field(default_factory=dict)


# ── 3.1 Health ───────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: str = ""
    message: str = "Dashboard API healthy"


# ── 3.2 Overview ─────────────────────────────────────────────


class OverviewKpis(BaseModel):
    total_sessions: int = 0
    total_messages: int = 0
    llm_calls: int = 0
    tool_calls: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    budget_used_pct: float = 0.0
    error_rate: float = 0.0
    avg_latency_ms: int = 0
    active_agents: int = 0
    mcp_connections: int = 0
    system_uptime_seconds: int = 0


class OverviewTrends(BaseModel):
    total_sessions_trend: float = 0.0
    total_tokens_trend: float = 0.0
    error_rate_trend: float = 0.0


class OverviewResponse(BaseModel):
    period: Period = Field(default_factory=Period)
    kpis: OverviewKpis = Field(default_factory=OverviewKpis)
    trends: OverviewTrends = Field(default_factory=OverviewTrends)


# ── 3.3 Tokens ───────────────────────────────────────────────


class TokensSummary(BaseModel):
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0


class TimelineEntry(BaseModel):
    date: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    llm_calls: int = 0


class ByModelEntry(BaseModel):
    provider_id: str = ""
    model_name: str = ""
    model_key: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    call_count: int = 0
    pct_of_total: float = 0.0
    estimated_cost: float = 0.0


class TokensResponse(BaseModel):
    period: Period = Field(default_factory=Period)
    summary: TokensSummary = Field(default_factory=TokensSummary)
    timeline: List[TimelineEntry] = Field(default_factory=list)
    by_model: List[ByModelEntry] = Field(default_factory=list)


# ── 3.4 Agents ───────────────────────────────────────────────


class AgentEntry(BaseModel):
    agent_id: str = ""
    agent_name: str = ""
    sessions: int = 0
    messages: int = 0
    llm_calls: int = 0
    tokens: int = 0
    avg_tokens_per_session: int = 0


class ByChannelEntry(BaseModel):
    channel_name: str = ""
    sessions: int = 0
    messages: int = 0
    llm_calls: int = 0


class AgentsSummary(BaseModel):
    total_agents: int = 0
    total_sessions: int = 0
    total_messages: int = 0
    total_llm_calls: int = 0


class AgentsStatsResponse(BaseModel):
    period: Period = Field(default_factory=Period)
    agents: List[AgentEntry] = Field(default_factory=list)
    by_channel: List[ByChannelEntry] = Field(default_factory=list)
    summary: AgentsSummary = Field(default_factory=AgentsSummary)


# ── 3.5 Skills ───────────────────────────────────────────────


class SkillsByType(BaseModel):
    builtin: int = 0
    mcp: int = 0
    custom: int = 0


class SkillsSummary(BaseModel):
    total_installed: int = 0
    total_by_type: SkillsByType = Field(
        default_factory=SkillsByType
    )


class SkillCallEntry(BaseModel):
    skill_name: str = ""
    skill_type: str = "builtin"
    call_count: int = 0
    error_count: int = 0
    error_rate: float = 0.0
    avg_duration_ms: int = 0


class SkillsStatsResponse(BaseModel):
    period: Period = Field(default_factory=Period)
    summary: SkillsSummary = Field(default_factory=SkillsSummary)
    top_calls: List[SkillCallEntry] = Field(default_factory=list)
    by_type: SkillsByType = Field(default_factory=SkillsByType)


# ── 3.6 Models ───────────────────────────────────────────────


class ModelsSummary(BaseModel):
    total_providers: int = 0
    active_models: int = 0
    total_calls: int = 0
    total_tokens: int = 0


class ModelEntry(BaseModel):
    provider_id: str = ""
    model_name: str = ""
    model_key: str = ""
    call_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    avg_latency_ms: int = 0
    error_count: int = 0
    success_rate: float = 100.0
    pct_of_calls: float = 0.0


class ModelsStatsResponse(BaseModel):
    period: Period = Field(default_factory=Period)
    summary: ModelsSummary = Field(default_factory=ModelsSummary)
    models: List[ModelEntry] = Field(default_factory=list)
