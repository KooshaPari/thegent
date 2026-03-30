"""Phench service bridge."""
from __future__ import annotations

import sys
from pathlib import Path

# Add phench/src to sys.path if phench.service not already available
if "phench.service" not in sys.modules:
    # Use __file__ to find the correct path
    if "__file__" in globals() and Path(__file__).exists():
        _init_file = Path(__file__).resolve()
    else:
        # Fallback for when __file__ is not available
        _init_file = Path.cwd() / "src/thegent/phench/__init__.py"
    
    # Navigate from phench/__init__.py -> repos root
    # src/thegent/phench/__init__.py -> parents[0] = phench/
    # parents[1] = thegent/, parents[2] = src/, parents[3] = platforms/thegent/
    # parents[4] = platforms/, parents[5] = repos root
    _repos_root = _init_file.parents[5]
    _phench_src = _repos_root / "phench" / "src"
    
    if _phench_src.exists() and str(_phench_src) not in sys.path:
        sys.path.insert(0, str(_phench_src))

from phench import service, models, runner, store

globals().update(vars(service))
__all__ = list(vars(service).keys()) + ["models", "runner", "store", "service"]
