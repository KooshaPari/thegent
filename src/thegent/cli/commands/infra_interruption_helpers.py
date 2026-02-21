"""Helpers for interruption command parsing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_recent_interruptions(path: Path, limit: int) -> list[dict[str, Any]]:
    """Load interruption log entries and return newest-first limited rows."""
    items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return sorted(items, key=lambda item: item.get("timestamp", ""), reverse=True)[:limit]
