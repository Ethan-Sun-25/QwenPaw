# -*- coding: utf-8 -*-
"""
Data access layer — read-only access to WORKING_DIR.

All functions return empty values on missing files or parse errors;
no exceptions propagate to the caller.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .config import get_working_dir, SENSITIVE_KEYS

logger = logging.getLogger("dashboard")

# ── Session mtime index ──────────────────────────────────────
_session_mtime_cache: Dict[str, float] = {}
_session_data_cache: Dict[str, dict] = {}


# ═══════════════════════════════════════════════════════════════
# 1. token_usage.json
# ═══════════════════════════════════════════════════════════════


def load_token_usage() -> dict:
    """Load token_usage.json → {date: {model_key: {...}}}."""
    path = get_working_dir() / "token_usage.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("Failed to load token_usage.json: %s", e)
        return {}


# ═══════════════════════════════════════════════════════════════
# 2. sessions/ directory
# ═══════════════════════════════════════════════════════════════


def _sessions_dir() -> Path:
    return get_working_dir() / "sessions"


def list_session_files() -> List[str]:
    """List .json filenames under sessions/."""
    d = _sessions_dir()
    if not d.is_dir():
        return []
    try:
        return [f for f in os.listdir(d) if f.endswith(".json")]
    except OSError as e:
        logger.warning("Failed to list sessions dir: %s", e)
        return []


def load_session(filename: str) -> Optional[dict]:
    """Load a single session file with mtime caching."""
    path = _sessions_dir() / filename
    if not path.exists():
        return None
    try:
        mtime = path.stat().st_mtime
        if (
            filename in _session_mtime_cache
            and _session_mtime_cache[filename] == mtime
        ):
            return _session_data_cache.get(filename)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _session_mtime_cache[filename] = mtime
        _session_data_cache[filename] = data
        return data
    except Exception as e:
        logger.warning("Failed to load session %s: %s", filename, e)
        return None


def iter_sessions() -> Iterator[Tuple[str, dict]]:
    """Lazily iterate all sessions → (filename, session_dict)."""
    for fname in list_session_files():
        data = load_session(fname)
        if data is not None:
            yield fname, data


def count_messages_in_session(session: dict) -> int:
    """Count messages: len(agent.memory.content) * 2."""
    try:
        content = (
            session.get("agent", {})
            .get("memory", {})
            .get("content", [])
        )
        if isinstance(content, list):
            return len(content) * 2
    except Exception:
        pass
    return 0


def count_tool_calls_in_session(session: dict) -> int:
    """Count tool_call type messages in a session."""
    count = 0
    try:
        content = (
            session.get("agent", {})
            .get("memory", {})
            .get("content", [])
        )
        if not isinstance(content, list):
            return 0
        for pair in content:
            if not isinstance(pair, list):
                continue
            for msg in pair:
                if not isinstance(msg, dict):
                    continue
                msg_content = msg.get("content", [])
                if isinstance(msg_content, list):
                    for item in msg_content:
                        if (
                            isinstance(item, dict)
                            and item.get("type") == "tool_call"
                        ):
                            count += 1
    except Exception:
        pass
    return count


def get_agent_name_from_session(session: dict) -> str:
    """Extract Agent name from session dict."""
    try:
        return (
            session.get("agent", {}).get("name", "") or ""
        )
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════
# 3. qwenpaw.log
# ═══════════════════════════════════════════════════════════════


def _log_path() -> Path:
    return get_working_dir() / "qwenpaw.log"


def read_all_log_lines() -> List[str]:
    """Read all log lines."""
    path = _log_path()
    if not path.exists():
        return []
    try:
        with open(
            path, "r", encoding="utf-8", errors="replace"
        ) as f:
            return f.readlines()
    except Exception as e:
        logger.warning("Failed to read log: %s", e)
        return []


def get_first_log_timestamp() -> Optional[datetime]:
    """Get timestamp of first log line (for uptime calc)."""
    path = _log_path()
    if not path.exists():
        return None
    try:
        with open(
            path, "r", encoding="utf-8", errors="replace"
        ) as f:
            first_line = f.readline()
        if len(first_line) >= 19:
            return datetime.strptime(
                first_line[:19], "%Y-%m-%d %H:%M:%S"
            )
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════
# 4. config.json
# ═══════════════════════════════════════════════════════════════


def load_config_raw() -> dict:
    """Load raw config.json (internal use)."""
    path = get_working_dir() / "config.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to load config.json: %s", e)
        return {}


def _sanitize(obj: Any) -> Any:
    """Recursively sanitize sensitive keys."""
    if isinstance(obj, dict):
        return {
            k: (
                "***"
                if k in SENSITIVE_KEYS
                and isinstance(v, str)
                and v
                else _sanitize(v)
            )
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_sanitize(item) for item in obj]
    return obj


# ═══════════════════════════════════════════════════════════════
# 5. Helpers: builtin tools, MCP, agent profiles
# ═══════════════════════════════════════════════════════════════


def get_builtin_tools(config: Optional[dict] = None) -> List[str]:
    """Get builtin tool names list."""
    cfg = config or load_config_raw()
    tools = cfg.get("tools", {}).get("builtin_tools", {})
    if isinstance(tools, dict):
        return list(tools.keys())
    return []


def get_mcp_clients(config: Optional[dict] = None) -> dict:
    """Get MCP clients configuration."""
    cfg = config or load_config_raw()
    return cfg.get("mcp", {}).get("clients", {})


def get_enabled_mcp_count(
    config: Optional[dict] = None,
) -> int:
    """Count enabled MCP connections."""
    clients = get_mcp_clients(config)
    return sum(
        1
        for c in clients.values()
        if isinstance(c, dict) and c.get("enabled")
    )


def get_agent_profiles(
    config: Optional[dict] = None,
) -> dict:
    """Get agent profiles dict."""
    cfg = config or load_config_raw()
    return cfg.get("agents", {}).get("profiles", {})


def get_custom_skills_count() -> int:
    """Count custom skills."""
    d = get_working_dir() / "customized_skills"
    if not d.is_dir():
        return 0
    try:
        return len(
            [f for f in os.listdir(d) if not f.startswith(".")]
        )
    except OSError:
        return 0
