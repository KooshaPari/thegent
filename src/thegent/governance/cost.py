"""Cost governance scaffolding (G-GP-06).

CostEstimator and CostAggregator for per-run cost tracking.
See docs/governance/COST_GOVERNANCE_DESIGN.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Default $ per 1k tokens (input, output) - placeholder values
_DEFAULT_PRICING: dict[str, tuple[float, float]] = {
    "claude-sonnet-4": (0.003, 0.015),
    "gemini-3-flash": (0.0001, 0.0004),
    "gemini-2.0-flash": (0.0001, 0.0004),
}


@dataclass
class CostEstimator:
    """Estimate run cost from metadata. G-GP-06 Phase 2."""

    pricing: dict[str, tuple[float, float]] = field(default_factory=lambda: dict(_DEFAULT_PRICING))

    def estimate(
        self,
        model: str | None = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        prompt_length: int = 0,
    ) -> float:
        """Estimate cost in USD. Uses pricing table or heuristic fallback."""
        if model and model in self.pricing:
            inp, out = self.pricing[model]
            return (tokens_in / 1000.0) * inp + (tokens_out / 1000.0) * out
        # Fallback heuristic: prompt * 1.3 + 500 for output
        est_in = prompt_length * 1.3 if prompt_length else 500
        est_out = 500
        return (est_in / 1000.0) * 0.001 + (est_out / 1000.0) * 0.002  # placeholder $/1k


@dataclass
class CostAggregator:
    """Daily cost rollup by owner. G-GP-06 Phase 4."""

    session_dir: Path

    def daily_total(self, owner: str) -> float:
        """Sum cost_usd for owner's runs today. Returns 0.0 if no cost tracking."""
        # Scaffolding: read from run_registry.jsonl finish events with cost_usd
        registry_path = self.session_dir / "run_registry.jsonl"
        if not registry_path.exists():
            return 0.0
        today = datetime.now(UTC).date().isoformat()
        total = 0.0
        try:
            with registry_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("event") == "finish" and data.get("cost_usd") is not None:
                            ts = data.get("ended_at_utc", data.get("timestamp", ""))[:10]
                            if ts == today:
                                total += float(data["cost_usd"])
                    except Exception:
                        continue
        except Exception:
            pass
        return total

    def get_mtd_total(self) -> float:
        """Sum cost_usd for all runs this month. G-GP-06 Phase 4."""
        registry_path = self.session_dir / "run_registry.jsonl"
        if not registry_path.exists():
            return 0.0

        now = datetime.now(UTC)
        current_month = f"{now.year}-{now.month:02d}"
        total = 0.0
        try:
            with registry_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("event") == "finish" and data.get("cost_usd") is not None:
                            ts = data.get("ended_at_utc", data.get("timestamp", ""))
                            if ts and ts.startswith(current_month):
                                total += float(data["cost_usd"])
                    except Exception:
                        continue
        except Exception:
            pass
        return total
