"""Pytest configuration and fixtures for thegent tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ensure src/ takes priority over scripts/ and tests/ in sys.path.
_thegent_repo = Path(__file__).resolve().parent.parent
_src = str(_thegent_repo / "src")
_repos_root = _thegent_repo.parent.parent  # repos/ is parent of platforms/

_monorepo_shadow_src = _repos_root / "src"

if _monorepo_shadow_src.is_dir() and (_monorepo_shadow_src / "thegent").exists():
    _shadow_resolved = _monorepo_shadow_src.resolve()
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != _shadow_resolved]
    _shadow_pkg = (_monorepo_shadow_src / "thegent").resolve()
    for _name in list(sys.modules):
        _mod = sys.modules.get(_name)
        _mf = getattr(_mod, "__file__", None) if _mod else None
        if not _mf:
            continue
        try:
            if Path(_mf).resolve().is_relative_to(_shadow_pkg):
                sys.modules.pop(_name, None)
        except (OSError, ValueError):
            continue

if _src not in sys.path:
    sys.path.insert(0, _src)

import importlib.util


def _preload_src_package(name: str) -> None:
    """Load a package from src/ into sys.modules before any sys.path mutation."""
    if name in sys.modules:
        return
    pkg_path = Path(__file__).parent.parent / "src" / name / "__init__.py"
    if not pkg_path.exists():
        return
    spec = importlib.util.spec_from_file_location(name, pkg_path)
    if spec is None or spec.loader is None:
        return
    mod = importlib.util.module_from_spec(spec)
    mod.__path__ = [str(pkg_path.parent)]
    sys.modules[name] = mod
    spec.loader.exec_module(mod)


_preload_src_package("research_engine")
_preload_src_package("agent_roles")

# Mock the thegent_fs module before any imports
sys.modules["thegent_fs"] = MagicMock()

# Pre-load phench package and set up thegent.phench aliases
_phench_path = _repos_root / "phench"
if _phench_path.is_dir():
    _phench_init = _phench_path / "__init__.py"
    if _phench_init.exists():
        spec = importlib.util.spec_from_file_location("phench", _phench_init)
        if spec and spec.loader:
            _phench_mod = importlib.util.module_from_spec(spec)
            sys.modules["phench"] = _phench_mod
            spec.loader.exec_module(_phench_mod)

            # Set up thegent.phench as an alias to phench
            # This allows tests to import from thegent.phench.service
            if "phench.service" in sys.modules:
                sys.modules["thegent.phench"] = sys.modules["phench"]
                sys.modules["thegent.phench.service"] = sys.modules["phench.service"]
                sys.modules["thegent.phench.models"] = sys.modules.get("phench.models")
                sys.modules["thegent.phench.store"] = sys.modules.get("phench.store")
