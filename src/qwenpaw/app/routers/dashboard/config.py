# -*- coding: utf-8 -*-
"""
Dashboard configuration constants.

Paths use QwenPaw's WORKING_DIR (priority: env > ~/.copaw > ~/.qwenpaw).
"""

import json
import os
from pathlib import Path
from typing import Dict


def get_working_dir() -> Path:
    """Lazy accessor for WORKING_DIR to avoid heavy import chain."""
    from qwenpaw.constant import WORKING_DIR
    return WORKING_DIR


# ── Cache TTL (seconds) ─────────────────────────────────────
CACHE_TTL_OVERVIEW = 60
CACHE_TTL_TOKENS = 60
CACHE_TTL_AGENTS = 60
CACHE_TTL_SKILLS = 60
CACHE_TTL_MODELS = 60
CACHE_TTL_LOG = 300
CACHE_TTL_HEALTH = 5

# ── Budget ───────────────────────────────────────────────────
DEFAULT_MONTHLY_BUDGET_CNY = 5.0  # MVP fixed 5 CNY/month

# ── FX rate ──────────────────────────────────────────────────
USD_TO_CNY = 7.2

# ── Sensitive keys (sanitize) ────────────────────────────────
SENSITIVE_KEYS = frozenset({
    "client_id", "client_secret", "bot_token", "api_key",
    "access_token", "app_secret", "encrypt_key",
    "verification_token", "http_proxy_auth",
})

# ── Model prices ─────────────────────────────────────────────
MODEL_PRICES_PATH = Path(
    os.environ.get(
        "MODEL_PRICES_PATH",
        str(Path(__file__).resolve().parent / "model_prices.json"),
    )
)


def load_model_prices() -> Dict[str, Dict]:
    """Load model price table, normalise to CNY/token."""
    if not MODEL_PRICES_PATH.exists():
        return {}
    try:
        with open(MODEL_PRICES_PATH, "r", encoding="utf-8") as f:
            raw: Dict = json.load(f)
    except Exception:
        return {}

    prices: Dict[str, Dict] = {}
    for model_key, info in raw.items():
        unit_per = info.get("unit_per", 1000)
        currency = info.get("currency", "CNY")
        rate = USD_TO_CNY if currency == "USD" else 1.0
        prices[model_key] = {
            "input": info["input"] / unit_per * rate,
            "output": info["output"] / unit_per * rate,
        }
    return prices


MODEL_PRICES: Dict[str, Dict] = load_model_prices()
