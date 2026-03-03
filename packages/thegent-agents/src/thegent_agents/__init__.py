"""thegent-agents package public surface."""

from __future__ import annotations

from typing import Any

AGENT_LABELS: dict[str, str] = {"cursor-agent": "cursor", "cursor-api": "cursor-api"}


def __getattr__(name: str) -> Any:
    if name in {"list_agent_names", "list_droid_names", "resolve_agent"}:
        from thegent.agents.registry import (
            list_agent_names,
            list_droid_names,
            resolve_agent,
        )

        mapping = {
            "list_agent_names": list_agent_names,
            "list_droid_names": list_droid_names,
            "resolve_agent": resolve_agent,
        }
        return mapping[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["AGENT_LABELS", "list_agent_names", "list_droid_names", "resolve_agent"]
