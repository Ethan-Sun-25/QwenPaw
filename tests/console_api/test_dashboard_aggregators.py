# -*- coding: utf-8 -*-
"""
Dashboard aggregators unit tests — mock data, no real ~/.qwenpaw.

8 test cases verifying KPI aggregation formulas.
Parent packages are stubbed by conftest.py so heavy deps are never loaded.
"""

from datetime import date, datetime, timedelta
from unittest.mock import patch

from qwenpaw.app.routers.dashboard import (  # noqa: E402
    aggregators,
    data_sources as ds,
)
from qwenpaw.app.routers.dashboard.utils import parse_range

# ── Mock data ────────────────────────────────────────────────

TODAY = date.today().isoformat()

MOCK_TOKEN_USAGE = {
    TODAY: {
        "dashscope:qwen3.6-plus": {
            "provider_id": "dashscope",
            "model_name": "qwen3.6-plus",
            "prompt_tokens": 10000,
            "completion_tokens": 500,
            "call_count": 3,
        },
        "openai:gpt-4o": {
            "provider_id": "openai",
            "model_name": "gpt-4o",
            "prompt_tokens": 5000,
            "completion_tokens": 200,
            "call_count": 2,
        },
    }
}

_today_ts = int(datetime.now().timestamp() * 1000)
MOCK_SESSION_FILES = [
    "default_%d.json" % _today_ts,
    "default_%d.json" % (_today_ts + 1000),
    "agent2_%d.json" % (_today_ts + 2000),
]

MOCK_SESSION_DATA = {
    "agent": {
        "name": "TestAgent",
        "memory": {
            "content": [
                [
                    {
                        "id": "1",
                        "name": "user",
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "hi"}
                        ],
                    },
                    {
                        "id": "2",
                        "name": "assistant",
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "hello"}
                        ],
                    },
                ],
                [
                    {
                        "id": "3",
                        "name": "user",
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "run"}
                        ],
                    },
                    {
                        "id": "4",
                        "name": "assistant",
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_call",
                                "name": "execute_shell_command",
                                "id": "tc1",
                            }
                        ],
                    },
                ],
            ]
        },
    }
}

MOCK_CONFIG = {
    "channels": {
        "console": {"enabled": True},
        "dingtalk": {"enabled": True},
    },
    "mcp": {
        "clients": {
            "tavily": {"enabled": False},
            "search": {"enabled": True},
        }
    },
    "tools": {
        "builtin_tools": {
            "execute_shell_command": {},
            "read_file": {},
            "write_file": {},
        }
    },
    "agents": {"profiles": {"default": {}, "agent2": {}}},
}

MOCK_LOG_LINES = [
    TODAY
    + " 10:00:00 | INFO | runner.py:353"
    + " | Handle agent query: ...\n",
    TODAY
    + " 10:00:10 | INFO | console.py:420"
    + " | console stream done: ...\n",
    TODAY
    + " 10:01:00 | INFO | runner.py:353"
    + " | Handle agent query: ...\n",
    TODAY
    + " 10:01:05 | ERROR | channel.py:492"
    + " | failed to start channels=dingtalk\n",
    TODAY
    + " 10:01:08 | INFO | console.py:420"
    + " | console stream done: ...\n",
    TODAY
    + " 10:02:00 | INFO | console.py:329"
    + " | Usage for session 123\n",
]


# ── Patch helper ─────────────────────────────────────────────


def _clear_caches():
    """Clear all TTL caches on aggregator functions."""
    for fn in [
        aggregators.overview_metrics,
        aggregators.tokens_timeseries,
        aggregators.models_stats,
        aggregators.agents_stats,
        aggregators.skills_stats,
        aggregators._log_stats,
    ]:
        if hasattr(fn, "cache"):
            fn.cache.clear()


class _PatchCtx:
    """Context manager that patches data_sources functions."""

    def __init__(self):
        self.patches = [
            patch.object(
                ds, "load_token_usage",
                return_value=MOCK_TOKEN_USAGE,
            ),
            patch.object(
                ds, "list_session_files",
                return_value=MOCK_SESSION_FILES,
            ),
            patch.object(
                ds, "load_session",
                return_value=MOCK_SESSION_DATA,
            ),
            patch.object(
                ds, "load_config_raw",
                return_value=MOCK_CONFIG,
            ),
            patch.object(
                ds, "read_all_log_lines",
                return_value=MOCK_LOG_LINES,
            ),
            patch.object(
                ds, "get_first_log_timestamp",
                return_value=(
                    datetime.now() - timedelta(hours=2)
                ),
            ),
        ]
        self.mocks = []

    def __enter__(self):
        self.mocks = [p.start() for p in self.patches]
        _clear_caches()
        return self.mocks

    def __exit__(self, *args):
        for p in self.patches:
            p.stop()


# ── Test 1: K05 total tokens ────────────────────────────────


def test_k05_total_tokens():
    """K05: total_tokens = sum(prompt) + sum(completion) = 15700"""
    with _PatchCtx():
        resp = aggregators.overview_metrics(range_="today")
        assert resp.kpis.total_tokens == 15700, (
            "Expected 15700, got %d" % resp.kpis.total_tokens
        )


# ── Test 2: K03 LLM calls ───────────────────────────────────


def test_k03_llm_calls():
    """K03: llm_calls = sum(call_count) = 3 + 2 = 5"""
    with _PatchCtx():
        resp = aggregators.overview_metrics(range_="today")
        assert resp.kpis.llm_calls == 5, (
            "Expected 5, got %d" % resp.kpis.llm_calls
        )


# ── Test 3: K01 total sessions ──────────────────────────────


def test_k01_total_sessions():
    """K01: total_sessions = 3"""
    with _PatchCtx():
        resp = aggregators.overview_metrics(range_="today")
        assert resp.kpis.total_sessions == 3, (
            "Expected 3, got %d" % resp.kpis.total_sessions
        )


# ── Test 4: K02 total messages ──────────────────────────────


def test_k02_total_messages():
    """K02: total_messages = len(content)*2 * 3 sessions = 12"""
    with _PatchCtx():
        resp = aggregators.overview_metrics(range_="today")
        assert resp.kpis.total_messages == 12, (
            "Expected 12, got %d" % resp.kpis.total_messages
        )


# ── Test 5: Tokens timeseries summary ───────────────────────


def test_tokens_timeseries_summary():
    """tokens_timeseries summary totals"""
    with _PatchCtx():
        resp = aggregators.tokens_timeseries(range_="today")
        assert resp.summary.total_prompt_tokens == 15000
        assert resp.summary.total_completion_tokens == 700
        assert resp.summary.total_tokens == 15700


# ── Test 6: Models stats ────────────────────────────────────


def test_models_stats_count():
    """models_stats: 2 models, 5 total calls"""
    with _PatchCtx():
        resp = aggregators.models_stats(range_="today")
        assert resp.summary.active_models == 2
        assert resp.summary.total_calls == 5
        assert resp.summary.total_tokens == 15700


# ── Test 7: Period format ────────────────────────────────────


def test_period_format():
    """period contains correct range_type and dates"""
    with _PatchCtx():
        resp = aggregators.overview_metrics(range_="today")
        assert resp.period.range_type == "today"
        assert resp.period.start_date == TODAY
        assert resp.period.end_date == TODAY


# ── Test 8: parse_range utility ──────────────────────────────


def test_parse_range():
    """Date range parsing."""
    sd, ed, rt = parse_range("today")
    assert rt == "today"
    assert sd == ed == date.today()

    sd, ed, rt = parse_range("7d")
    assert rt == "7d"
    assert (ed - sd).days == 6

    sd, ed, rt = parse_range("30d")
    assert rt == "30d"
    assert (ed - sd).days == 29
