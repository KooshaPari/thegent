"""Stub module."""

from typing import Any


class ResultAggregator:
    """Aggregates results from multiple sources."""

    def __init__(self) -> None:
        self.results: list[Any] = []

    def add(self, result: Any) -> None:
        """Add a result."""
        self.results.append(result)

    def aggregate(self) -> dict[str, Any]:
        """Aggregate all results."""
        return {"count": len(self.results), "results": self.results}


__all__ = ["ResultAggregator"]
