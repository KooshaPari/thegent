"""Package: thegent.phench - Bridge to phench core package."""
from __future__ import annotations

import sys
from pathlib import Path

# Navigate from thegent/phench/__init__.py -> repos/phench/src/phench
init_path = Path(__file__).resolve()
repo_root = init_path.parents[5]
phench_src = repo_root / "phench" / "src"

if str(phench_src) not in sys.path:
    sys.path.insert(0, str(phench_src))

from phench import service
from phench import models

# Re-export everything from service and models
globals().update(vars(service))
globals().update(vars(models))
