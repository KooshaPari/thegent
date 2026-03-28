"""Facade to load thegent phench CLI from the source tree in tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_phench_module():
    repo_root = Path(__file__).resolve().parents[6]
    source_path = repo_root / "src" / "thegent" / "cli" / "apps" / "phench.py"
    apps_dir = source_path.parent
    spec = importlib.util.spec_from_file_location(
        "thegent.cli.apps.phench",
        source_path,
        submodule_search_locations=[str(apps_dir)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load thegent phench CLI module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_real_module = _load_phench_module()
globals().update({name: value for name, value in _real_module.__dict__.items() if not name.startswith("__")})
