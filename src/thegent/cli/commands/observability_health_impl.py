"""Health payload constants and helpers — split from observability_impl (WL-124)."""

from __future__ import annotations

import hashlib
import orjson as json
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings
