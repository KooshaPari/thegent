# tests/research_engine/conftest.py
# Ensure src/research_engine takes priority over tests/research_engine in sys.modules.
# pytest prepend importmode inserts tests/ at sys.path[0] when collecting package
# directories with __init__.py, which would shadow src/research_engine.
# Pre-loading the correct package here prevents the shadow.
import importlib
import sys
from pathlib import Path

_src = str(Path(__file__).parent.parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

# Force-reload research_engine from src/ if tests/ version was cached
_mod = sys.modules.get("research_engine")
if _mod is not None and "tests" in str(getattr(_mod, "__file__", "")):
    del sys.modules["research_engine"]

import research_engine as _re  # noqa: E402

if "tests" in str(_re.__file__):
    # Still wrong location — force import from src/
    sys.modules.pop("research_engine", None)
    spec = importlib.util.spec_from_file_location(
        "research_engine",
        Path(_src) / "research_engine" / "__init__.py",
    )
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["research_engine"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
