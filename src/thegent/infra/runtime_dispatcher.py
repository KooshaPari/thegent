"""Performance-optimized dispatcher for multi-runtime support.

This module handles the 'splitting' of code into optimal paths for:
1. PyPy (JIT-optimized pure Python)
2. CPython 3.13/3.14 (Native extensions and freethreading support)
3. Compiled backends (Rust, Go, Zig via FFI/Wasm)
"""

import logging
import sys
from collections.abc import Callable
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

# --- Runtime Identity ---
IS_PYPY = sys.implementation.name == "pypy"
PYTHON_VERSION = sys.version_info[:2]
HAS_FREETHREADING = getattr(sys, "_is_gil_enabled", lambda: True)() is False

class PerformanceModule:
    """Base class for performance-critical modules with multiple implementations."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._implementations: dict[str, Any] = {}
        self._selected: Any | None = None

    def register(self, runtime: str, impl: Any):
        self._implementations[runtime] = impl

    def get_impl(self) -> Any:
        if self._selected:
            return self._selected

        # Selection Logic
        # 1. Try Native Extension (Rust/C) first on CPython
        if not IS_PYPY:
            if "native" in self._implementations:
                self._selected = self._implementations["native"]
                return self._selected

        # 2. Try PyPy optimized logic
        if IS_PYPY and "pypy" in self._implementations:
            self._selected = self._implementations["pypy"]
            return self._selected

        # 3. Fallback to generic python
        self._selected = self._implementations.get("python")
        return self._selected

# --- Performance-Critical Dispatchers ---

# 1. JSON (Massive difference between orjson and pypy-json)
try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

def _pypy_json_dumps(obj: Any, **kwargs) -> str:
    import json
    return json.dumps(obj, **kwargs)

def _cpython_json_dumps(obj: Any, **kwargs) -> str:
    if HAS_ORJSON:
        return orjson.dumps(obj).decode("utf-8")
    import json
    return json.dumps(obj, **kwargs)

json_dispatcher = PerformanceModule("json")
json_dispatcher.register("pypy", _pypy_json_dumps)
json_dispatcher.register("native", _cpython_json_dumps)
json_dispatcher.register("python", _pypy_json_dumps)

# 2. Routing (The Core Logic)
# We want to use the Rust 'thegent_router' if available on CPython
try:
    import thegent_router
    HAS_RUST_ROUTER = True
except ImportError:
    HAS_RUST_ROUTER = False

def _python_route_logic(task: str, agents: list) -> Any:
    # Pure python JIT-friendly logic
    # This would be moved to a separate file in a real split
    pass

router_dispatcher = PerformanceModule("router")
if HAS_RUST_ROUTER:
    router_dispatcher.register("native", thegent_router.ParetoRouter())
router_dispatcher.register("pypy", _python_route_logic)
router_dispatcher.register("python", _python_route_logic)

# --- Global Access ---

def get_json_dumps() -> Callable:
    return json_dispatcher.get_impl()

def get_router() -> Any:
    return router_dispatcher.get_impl()

def get_runtime_status() -> dict[str, Any]:
    return {
        "implementation": sys.implementation.name,
        "version": f"{PYTHON_VERSION[0]}.{PYTHON_VERSION[1]}",
        "freethreading": HAS_FREETHREADING,
        "jit": IS_PYPY,
        "active_extensions": {
            "orjson": HAS_ORJSON,
            "rust_router": HAS_RUST_ROUTER,
        }
    }
