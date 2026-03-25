"""Sorting helpers for provider/model manager listings."""

from __future__ import annotations

from typing import Any


def sort_model_rows(result: list[dict[str, Any]], sort_by: str) -> None:
    """Sort model rows in-place by a known sort key."""
    if sort_by == "cost":
        result.sort(key=lambda x: x.get("total_cost_per_1m") or x.get("cost_per_1m") or float("inf"))
    elif sort_by == "context":
        result.sort(key=lambda x: x.get("context_limit") or 0, reverse=True)
    elif sort_by in {"speed", "tps"}:
        result.sort(key=lambda x: x.get("tps") or 0, reverse=True)
    elif sort_by == "composite_score":
        result.sort(key=lambda x: x.get("composite_score") or 0, reverse=True)
