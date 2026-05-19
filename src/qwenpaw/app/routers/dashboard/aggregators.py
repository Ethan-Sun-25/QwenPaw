# -*- coding: utf-8 -*-
"""
12 KPI aggregation (K01-K12).

Uses data_sources functions — never reads files directly.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from datetime import date, datetime
from typing import Dict, List, Tuple

from . import data_sources as ds
from .config import (
    CACHE_TTL_AGENTS,
    CACHE_TTL_LOG,
    CACHE_TTL_MODELS,
    CACHE_TTL_OVERVIEW,
    CACHE_TTL_SKILLS,
    CACHE_TTL_TOKENS,
    DEFAULT_MONTHLY_BUDGET_CNY,
    MODEL_PRICES,
)
from .schemas import (
    AgentEntry,
    AgentsStatsResponse,
    AgentsSummary,
    ByChannelEntry,
    ByModelEntry,
    ModelEntry,
    ModelsStatsResponse,
    ModelsSummary,
    OverviewKpis,
    OverviewResponse,
    OverviewTrends,
    Period,
    SkillCallEntry,
    SkillsByType,
    SkillsSummary,
    SkillsStatsResponse,
    TimelineEntry,
    TokensResponse,
    TokensSummary,
)
from .utils import (
    cached_ttl,
    date_in_range,
    extract_agent_id_from_filename,
    extract_date_from_filename,
    parse_range,
    safe_div,
)

logger = logging.getLogger("dashboard")


# ═══════════════════════════════════════════════════════════════
# Internal: Token aggregation
# ═══════════════════════════════════════════════════════════════


def _token_data_in_range(
    start: date, end: date,
) -> Dict[str, Dict[str, dict]]:
    """Return {date_str: {model_key: data}} within range."""
    raw = ds.load_token_usage()
    result: Dict[str, Dict[str, dict]] = {}
    for date_str, models in raw.items():
        try:
            d = date.fromisoformat(date_str)
        except ValueError:
            continue
        if date_in_range(d, start, end):
            result[date_str] = models
    return result


def _compute_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model_key: str,
) -> float:
    """Compute cost in CNY using model price table."""
    price = MODEL_PRICES.get(model_key)
    if not price:
        return 0.0
    return (
        prompt_tokens * price["input"]
        + completion_tokens * price["output"]
    )


# ═══════════════════════════════════════════════════════════════
# Internal: Session aggregation
# ═══════════════════════════════════════════════════════════════


def _sessions_in_range(
    start: date, end: date,
) -> List[Tuple[str, dict, date, str]]:
    """Return sessions in range: [(fname, dict, date, agent_id)]."""
    results = []
    for fname, session in ds.iter_sessions():
        d = extract_date_from_filename(fname)
        if d is None:
            continue
        if date_in_range(d, start, end):
            agent_id = extract_agent_id_from_filename(fname)
            results.append((fname, session, d, agent_id))
    return results


# ═══════════════════════════════════════════════════════════════
# Internal: Log parsing
# ═══════════════════════════════════════════════════════════════

_RE_ERROR = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\bERROR\b"
)
_RE_REQUEST = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
)
_RE_HANDLE_QUERY = re.compile(r"Handle agent query")
_RE_STREAM_DONE = re.compile(r"console stream done")
_RE_TIMESTAMP = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
)


@cached_ttl(CACHE_TTL_LOG)
def _log_stats() -> dict:
    """Parse log for error_count, request_count, latencies."""
    error_count = 0
    total_request_count = 0
    handle_times: List[datetime] = []
    done_times: List[datetime] = []

    lines = ds.read_all_log_lines()
    for line in lines:
        if _RE_ERROR.search(line):
            error_count += 1
        if _RE_REQUEST.search(line):
            total_request_count += 1
        m = _RE_TIMESTAMP.match(line)
        if m:
            try:
                ts = datetime.strptime(
                    m.group(1), "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                continue
            if _RE_HANDLE_QUERY.search(line):
                handle_times.append(ts)
            elif _RE_STREAM_DONE.search(line):
                done_times.append(ts)

    # Pair handle → done for latency
    latencies_ms: List[int] = []
    done_idx = 0
    for ht in handle_times:
        while (
            done_idx < len(done_times)
            and done_times[done_idx] <= ht
        ):
            done_idx += 1
        if done_idx < len(done_times):
            delta = (
                done_times[done_idx] - ht
            ).total_seconds() * 1000
            latencies_ms.append(int(delta))
            done_idx += 1

    avg_latency = (
        int(safe_div(sum(latencies_ms), len(latencies_ms)))
        if latencies_ms
        else 0
    )

    return {
        "error_count": error_count,
        "total_request_count": total_request_count,
        "avg_latency_ms": avg_latency,
    }


# ═══════════════════════════════════════════════════════════════
# Public: overview_metrics
# ═══════════════════════════════════════════════════════════════


@cached_ttl(CACHE_TTL_OVERVIEW)
def overview_metrics(
    range_: str = "today",
    start: str = None,
    end: str = None,
) -> OverviewResponse:
    """Compute 12 KPI overview."""
    sd, ed, rt = parse_range(range_, start, end)
    period = Period(
        start_date=sd.isoformat(),
        end_date=ed.isoformat(),
        range_type=rt,
    )

    # K01, K02, K04, K10
    sessions = _sessions_in_range(sd, ed)
    total_sessions = len(sessions)
    total_messages = sum(
        ds.count_messages_in_session(s) for _, s, _, _ in sessions
    )
    tool_calls = sum(
        ds.count_tool_calls_in_session(s)
        for _, s, _, _ in sessions
    )
    active_agents_set = set()
    config = ds.load_config_raw()
    profiles = ds.get_agent_profiles(config)
    for _, _, _, aid in sessions:
        if not profiles or aid in profiles:
            active_agents_set.add(aid)
    active_agents = len(active_agents_set)

    # K03, K05, K06, K07
    token_data = _token_data_in_range(sd, ed)
    total_prompt = 0
    total_completion = 0
    llm_calls = 0
    estimated_cost = 0.0
    for _date_str, models in token_data.items():
        for model_key, mdata in models.items():
            pt = mdata.get("prompt_tokens", 0)
            ct = mdata.get("completion_tokens", 0)
            cc = mdata.get("call_count", 0)
            total_prompt += pt
            total_completion += ct
            llm_calls += cc
            estimated_cost += _compute_cost(pt, ct, model_key)

    total_tokens = total_prompt + total_completion
    estimated_cost = round(estimated_cost, 2)
    budget_used_pct = round(
        min(
            (estimated_cost / DEFAULT_MONTHLY_BUDGET_CNY) * 100,
            100,
        ),
        1,
    )

    # K08, K09
    log_s = _log_stats()
    error_rate = round(
        min(
            safe_div(
                log_s["error_count"], log_s["total_request_count"]
            )
            * 100,
            100.0,
        ),
        1,
    )
    avg_latency_ms = log_s["avg_latency_ms"]

    # K11
    mcp_connections = ds.get_enabled_mcp_count(config)

    # K12
    first_ts = ds.get_first_log_timestamp()
    if first_ts:
        uptime = int(
            (datetime.now() - first_ts).total_seconds()
        )
    else:
        uptime = 0

    kpis = OverviewKpis(
        total_sessions=total_sessions,
        total_messages=total_messages,
        llm_calls=llm_calls,
        tool_calls=tool_calls,
        total_tokens=total_tokens,
        estimated_cost=estimated_cost,
        budget_used_pct=budget_used_pct,
        error_rate=error_rate,
        avg_latency_ms=avg_latency_ms,
        active_agents=active_agents,
        mcp_connections=mcp_connections,
        system_uptime_seconds=uptime,
    )

    trends = OverviewTrends()

    return OverviewResponse(
        period=period, kpis=kpis, trends=trends
    )


# ═══════════════════════════════════════════════════════════════
# Public: tokens_timeseries
# ═══════════════════════════════════════════════════════════════


@cached_ttl(CACHE_TTL_TOKENS)
def tokens_timeseries(
    range_: str = "today",
    group_by: str = "day",
    start: str = None,
    end: str = None,
) -> TokensResponse:
    """Token consumption time series and by-model breakdown."""
    sd, ed, rt = parse_range(range_, start, end)
    period = Period(
        start_date=sd.isoformat(),
        end_date=ed.isoformat(),
        range_type=rt,
    )

    token_data = _token_data_in_range(sd, ed)

    total_prompt = 0
    total_completion = 0
    total_cost = 0.0
    day_agg: Dict[str, dict] = defaultdict(
        lambda: {"prompt": 0, "completion": 0, "calls": 0}
    )
    model_agg: Dict[str, dict] = defaultdict(
        lambda: {
            "prompt": 0,
            "completion": 0,
            "calls": 0,
            "cost": 0.0,
        }
    )

    for date_str, models in token_data.items():
        for model_key, mdata in models.items():
            pt = mdata.get("prompt_tokens", 0)
            ct = mdata.get("completion_tokens", 0)
            cc = mdata.get("call_count", 0)
            cost = _compute_cost(pt, ct, model_key)

            total_prompt += pt
            total_completion += ct
            total_cost += cost

            day_agg[date_str]["prompt"] += pt
            day_agg[date_str]["completion"] += ct
            day_agg[date_str]["calls"] += cc

            model_agg[model_key]["prompt"] += pt
            model_agg[model_key]["completion"] += ct
            model_agg[model_key]["calls"] += cc
            model_agg[model_key]["cost"] += cost

    total_tokens = total_prompt + total_completion

    summary = TokensSummary(
        total_prompt_tokens=total_prompt,
        total_completion_tokens=total_completion,
        total_tokens=total_tokens,
        total_cost=round(total_cost, 2),
    )

    timeline = sorted(
        [
            TimelineEntry(
                date=d,
                prompt_tokens=v["prompt"],
                completion_tokens=v["completion"],
                total_tokens=v["prompt"] + v["completion"],
                llm_calls=v["calls"],
            )
            for d, v in day_agg.items()
        ],
        key=lambda x: x.date,
    )

    by_model = []
    for mk, v in model_agg.items():
        parts = mk.split(":", 1)
        provider_id = parts[0] if len(parts) == 2 else ""
        model_name = parts[1] if len(parts) == 2 else mk
        mt = v["prompt"] + v["completion"]
        by_model.append(
            ByModelEntry(
                provider_id=provider_id,
                model_name=model_name,
                model_key=mk,
                prompt_tokens=v["prompt"],
                completion_tokens=v["completion"],
                total_tokens=mt,
                call_count=v["calls"],
                pct_of_total=round(
                    safe_div(mt, total_tokens) * 100, 1
                ),
                estimated_cost=round(v["cost"], 2),
            )
        )

    return TokensResponse(
        period=period,
        summary=summary,
        timeline=timeline,
        by_model=by_model,
    )


# ═══════════════════════════════════════════════════════════════
# Public: agents_stats
# ═══════════════════════════════════════════════════════════════


@cached_ttl(CACHE_TTL_AGENTS)
def agents_stats(
    range_: str = "today",
    agent_id: str = None,
    start: str = None,
    end: str = None,
) -> AgentsStatsResponse:
    """Agent-level statistics."""
    sd, ed, rt = parse_range(range_, start, end)
    period = Period(
        start_date=sd.isoformat(),
        end_date=ed.isoformat(),
        range_type=rt,
    )

    sessions = _sessions_in_range(sd, ed)
    if agent_id:
        sessions = [
            (f, s, d, a)
            for f, s, d, a in sessions
            if a == agent_id
        ]

    agent_agg: Dict[str, dict] = defaultdict(
        lambda: {"name": "", "sessions": 0, "messages": 0}
    )
    for _fname, session, _, aid in sessions:
        agent_agg[aid]["sessions"] += 1
        agent_agg[aid]["messages"] += (
            ds.count_messages_in_session(session)
        )
        name = ds.get_agent_name_from_session(session)
        if name:
            agent_agg[aid]["name"] = name

    # Token data (global — cannot split by agent)
    token_data = _token_data_in_range(sd, ed)
    total_tokens_all = 0
    total_llm_calls = 0
    for models in token_data.values():
        for mdata in models.values():
            total_tokens_all += (
                mdata.get("prompt_tokens", 0)
                + mdata.get("completion_tokens", 0)
            )
            total_llm_calls += mdata.get("call_count", 0)

    agents_list: List[AgentEntry] = []
    total_sessions = 0
    total_messages = 0
    all_session_count = len(sessions)
    for aid, v in agent_agg.items():
        s_count = v["sessions"]
        m_count = v["messages"]
        agent_tokens = (
            int(
                safe_div(s_count, all_session_count)
                * total_tokens_all
            )
            if all_session_count
            else 0
        )
        agent_llm = (
            int(
                safe_div(s_count, all_session_count)
                * total_llm_calls
            )
            if all_session_count
            else 0
        )

        agents_list.append(
            AgentEntry(
                agent_id=aid,
                agent_name=v["name"] or aid,
                sessions=s_count,
                messages=m_count,
                llm_calls=agent_llm,
                tokens=agent_tokens,
                avg_tokens_per_session=int(
                    safe_div(agent_tokens, s_count)
                ),
            )
        )
        total_sessions += s_count
        total_messages += m_count

    by_channel = (
        [
            ByChannelEntry(
                channel_name="console",
                sessions=total_sessions,
                messages=total_messages,
                llm_calls=total_llm_calls,
            )
        ]
        if total_sessions > 0
        else []
    )

    summary = AgentsSummary(
        total_agents=len(agents_list),
        total_sessions=total_sessions,
        total_messages=total_messages,
        total_llm_calls=total_llm_calls,
    )

    return AgentsStatsResponse(
        period=period,
        agents=agents_list,
        by_channel=by_channel,
        summary=summary,
    )


# ═══════════════════════════════════════════════════════════════
# Public: skills_stats
# ═══════════════════════════════════════════════════════════════


@cached_ttl(CACHE_TTL_SKILLS)
def skills_stats(
    range_: str = "today",
    top: int = 10,
    start: str = None,
    end: str = None,
) -> SkillsStatsResponse:
    """Skill call leaderboard and type distribution."""
    sd, ed, rt = parse_range(range_, start, end)
    period = Period(
        start_date=sd.isoformat(),
        end_date=ed.isoformat(),
        range_type=rt,
    )

    config = ds.load_config_raw()
    builtin_tools = ds.get_builtin_tools(config)
    mcp_clients = ds.get_mcp_clients(config)
    custom_count = ds.get_custom_skills_count()

    builtin_count = len(builtin_tools)
    mcp_count = len(mcp_clients)
    total_installed = builtin_count + mcp_count + custom_count

    by_type = SkillsByType(
        builtin=builtin_count,
        mcp=mcp_count,
        custom=custom_count,
    )
    summary = SkillsSummary(
        total_installed=total_installed, total_by_type=by_type
    )

    # Count tool_call frequency from sessions
    sessions = _sessions_in_range(sd, ed)
    skill_counts: Dict[str, int] = defaultdict(int)
    for _, session, _, _ in sessions:
        try:
            content = (
                session.get("agent", {})
                .get("memory", {})
                .get("content", [])
            )
            if not isinstance(content, list):
                continue
            for pair in content:
                if not isinstance(pair, list):
                    continue
                for msg in pair:
                    if not isinstance(msg, dict):
                        continue
                    mc = msg.get("content", [])
                    if isinstance(mc, list):
                        for item in mc:
                            if (
                                isinstance(item, dict)
                                and item.get("type")
                                == "tool_call"
                            ):
                                name = item.get(
                                    "name"
                                ) or item.get("id", "unknown")
                                skill_counts[name] += 1
        except Exception:
            continue

    top_calls: List[SkillCallEntry] = []
    for name, count in sorted(
        skill_counts.items(), key=lambda x: -x[1]
    )[:top]:
        skill_type = (
            "builtin" if name in builtin_tools else "custom"
        )
        top_calls.append(
            SkillCallEntry(
                skill_name=name,
                skill_type=skill_type,
                call_count=count,
                error_count=0,
                error_rate=0.0,
                avg_duration_ms=0,
            )
        )

    return SkillsStatsResponse(
        period=period,
        summary=summary,
        top_calls=top_calls,
        by_type=by_type,
    )


# ═══════════════════════════════════════════════════════════════
# Public: models_stats
# ═══════════════════════════════════════════════════════════════


@cached_ttl(CACHE_TTL_MODELS)
def models_stats(
    range_: str = "today",
    start: str = None,
    end: str = None,
) -> ModelsStatsResponse:
    """Model call distribution and performance."""
    sd, ed, rt = parse_range(range_, start, end)
    period = Period(
        start_date=sd.isoformat(),
        end_date=ed.isoformat(),
        range_type=rt,
    )

    token_data = _token_data_in_range(sd, ed)

    model_agg: Dict[str, dict] = defaultdict(
        lambda: {"prompt": 0, "completion": 0, "calls": 0}
    )
    for models in token_data.values():
        for model_key, mdata in models.items():
            model_agg[model_key]["prompt"] += mdata.get(
                "prompt_tokens", 0
            )
            model_agg[model_key]["completion"] += mdata.get(
                "completion_tokens", 0
            )
            model_agg[model_key]["calls"] += mdata.get(
                "call_count", 0
            )

    providers = set()
    total_calls = 0
    total_tokens = 0
    models_list: List[ModelEntry] = []

    for mk, v in model_agg.items():
        parts = mk.split(":", 1)
        pid = parts[0] if len(parts) == 2 else ""
        mn = parts[1] if len(parts) == 2 else mk
        providers.add(pid)
        mt = v["prompt"] + v["completion"]
        total_calls += v["calls"]
        total_tokens += mt
        models_list.append(
            ModelEntry(
                provider_id=pid,
                model_name=mn,
                model_key=mk,
                call_count=v["calls"],
                prompt_tokens=v["prompt"],
                completion_tokens=v["completion"],
                total_tokens=mt,
                avg_latency_ms=0,
                error_count=0,
                success_rate=100.0,
                pct_of_calls=0.0,
            )
        )

    for m in models_list:
        m.pct_of_calls = (
            round(safe_div(m.call_count, total_calls) * 100, 1)
            if total_calls
            else 0.0
        )

    summary = ModelsSummary(
        total_providers=len(providers),
        active_models=len(models_list),
        total_calls=total_calls,
        total_tokens=total_tokens,
    )

    return ModelsStatsResponse(
        period=period, summary=summary, models=models_list
    )
