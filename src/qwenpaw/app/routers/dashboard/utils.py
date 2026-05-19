# -*- coding: utf-8 -*-
"""Utility helpers: TTL cache, date range parsing, safe math."""

from __future__ import annotations

import functools
import logging
from datetime import date, datetime, timedelta, timezone
from typing import Tuple

from cachetools import TTLCache

logger = logging.getLogger("dashboard")

# ── Global cache pool ────────────────────────────────────────
_caches: dict = {}


def cached_ttl(ttl: int, maxsize: int = 128):
    """TTL cache decorator (cachetools.TTLCache)."""

    def decorator(fn):
        cache = TTLCache(maxsize=maxsize, ttl=ttl)
        _caches[fn.__qualname__] = cache

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = (
                fn.__qualname__,
                args,
                tuple(sorted(kwargs.items())),
            )
            try:
                return cache[key]
            except KeyError:
                pass
            result = fn(*args, **kwargs)
            try:
                cache[key] = result
            except ValueError:
                pass
            return result

        wrapper.cache = cache
        return wrapper

    return decorator


# ── Date range helpers ───────────────────────────────────────


def parse_range(
    range_: str = "today",
    start: str | None = None,
    end: str | None = None,
) -> Tuple[date, date, str]:
    """Parse range/start/end into (start_date, end_date, range_type)."""
    today = date.today()
    range_ = (range_ or "today").lower()

    if range_ == "custom" and start and end:
        try:
            sd = date.fromisoformat(start[:10])
            ed = date.fromisoformat(end[:10])
        except ValueError:
            sd, ed = today, today
        if (ed - sd).days > 90 or sd > ed:
            sd, ed = today - timedelta(days=89), today
        return sd, ed, "custom"

    if range_ == "7d":
        return today - timedelta(days=6), today, "7d"
    if range_ == "30d":
        return today - timedelta(days=29), today, "30d"

    return today, today, "today"


def date_in_range(d: date, start: date, end: date) -> bool:
    """Check if date is within [start, end]."""
    return start <= d <= end


def now_iso() -> str:
    """Current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    """Safe division, returns default on zero denominator."""
    return a / b if b else default


def extract_date_from_filename(filename: str) -> date | None:
    """Extract date from session filename '{agent}_{ts_ms}.json'."""
    try:
        stem = filename.replace(".json", "")
        ts_str = stem.rsplit("_", 1)[-1]
        ts = int(ts_str) / 1000.0
        return datetime.fromtimestamp(ts).date()
    except (ValueError, IndexError, OSError):
        return None


def extract_agent_id_from_filename(filename: str) -> str:
    """Extract agent_id prefix from session filename."""
    stem = filename.replace(".json", "")
    parts = stem.rsplit("_", 1)
    return parts[0] if len(parts) == 2 else stem
