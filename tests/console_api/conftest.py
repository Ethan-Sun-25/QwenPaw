# -*- coding: utf-8 -*-
"""
conftest.py for console_api tests.

Stubs heavy parent packages so that importing
qwenpaw.app.routers.dashboard.* does NOT trigger the real
qwenpaw.app.routers.__init__.py (which pulls in agentscope etc.).
"""

import sys
import types
from pathlib import Path

# ── 1. Add src/ to sys.path ────────────────────────────────────
_SRC = Path(__file__).resolve().parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ── 2. Stub parent packages with correct __path__ ─────────────
# This allows Python to find child packages (dashboard/) without
# executing the heavy __init__.py files.
_PKG_STUBS = {
    "qwenpaw": str(_SRC / "qwenpaw"),
    "qwenpaw.app": str(_SRC / "qwenpaw" / "app"),
    "qwenpaw.app.routers": str(
        _SRC / "qwenpaw" / "app" / "routers"
    ),
}

for pkg_name, pkg_path in _PKG_STUBS.items():
    if pkg_name not in sys.modules:
        mod = types.ModuleType(pkg_name)
        mod.__package__ = pkg_name
        mod.__path__ = [pkg_path]
        mod.__file__ = pkg_path + "/__init__.py"
        sys.modules[pkg_name] = mod

# ── 3. Stub qwenpaw.constant (lazy-import target) ─────────────
# dashboard.config.get_working_dir() does:
#     from qwenpaw.constant import WORKING_DIR
# We provide a fake so tests never touch the real filesystem.
if "qwenpaw.constant" not in sys.modules:
    _const = types.ModuleType("qwenpaw.constant")
    _const.WORKING_DIR = Path("/tmp/qwenpaw_test")
    sys.modules["qwenpaw.constant"] = _const
