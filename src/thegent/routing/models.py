"""Routing model compatibility types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TaskMetadata:
    """Minimal task metadata used by agent runners."""

    execution_path: str | None = None
    provider: str | None = None
    model: str | None = None
