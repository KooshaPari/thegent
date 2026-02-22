"""Pytest configuration and fixtures for thegent tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ensure src/ takes priority over scripts/ and tests/ in sys.path.
# Some test files (test_path_utils.py, test_batch_file_ops.py) insert scripts/ at
# sys.path[0], which causes scripts/research_engine.py to shadow src/research_engine/.
# Pre-loading the correct package here locks it into sys.modules before any path
# mutation can intercept it.
_src = str(Path(__file__).parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import importlib as _importlib  # noqa: E402
import importlib.util as _importlib_util  # noqa: E402

def _preload_src_package(name: str) -> None:
    """Load a package from src/ into sys.modules before any sys.path mutation."""
    if name in sys.modules:
        return
    pkg_path = Path(__file__).parent.parent / "src" / name / "__init__.py"
    if not pkg_path.exists():
        return
    spec = _importlib_util.spec_from_file_location(name, pkg_path)
    if spec is None or spec.loader is None:
        return
    mod = _importlib_util.module_from_spec(spec)
    mod.__path__ = [str(pkg_path.parent)]  # type: ignore[attr-defined]
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]

_preload_src_package("research_engine")

# Mock the thegent_fs module before any imports
sys.modules['thegent_fs'] = MagicMock()
