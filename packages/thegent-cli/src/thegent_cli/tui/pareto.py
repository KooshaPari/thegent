"""Pareto TUI Session — WL-031.

Provides `ParetoTuiSession`: a data-access layer that supplies the Pareto
Frontier TUI panel with live routing audit data.

The session reads from the JSONL audit file written by the Rust AuditLogger
(`~/.thegent/routing_audit.jsonl`) via the Python bridge in
`thegent.routing.route_executor`.

Fail-fast: every public method raises on malformed data; no silent fallbacks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from thegent.utils.routing_impl.route_executor import (
    RouterStatus,
    RoutingOrchestratorBridge,
)

# @trace WL-031

_DEFAULT_AUDIT_PATH = Path.home() / ".thegent" / "routing_audit.jsonl"


def _parse_jsonl_lines(
    lines: list[str], line_offset: int = 0, strict: bool = True
) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse a list of non-empty JSON strings into dicts.

    Raises:
        ValueError: on the first line that fails JSON decoding.
    """
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for i, line in enumerate(lines):
        lineno = line_offset + i + 1
        try:
            parsed = _decode_json_line(line, lineno=lineno)
            records.append(parsed)
        except ValueError:
            if strict:
                raise
            errors.append(f"line {lineno}")
    return records, errors


def _decode_json_line(line: str, lineno: int) -> dict[str, Any]:
    """Decode a single JSON line.  Raises ValueError on parse failure."""
    try:
        return json.loads(line)  # type: ignore[no-any-return]
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed JSON in audit file at line {lineno}: {exc}") from exc


class ParetoTuiSession:
    """Live data session for the Pareto Frontier TUI panel.

    Reads routing audit records and aggregates provider / cost / latency
    data for visualisation.

    Args:
        audit_path: Path to ``routing_audit.jsonl``.  Defaults to
            ``~/.thegent/routing_audit.jsonl``.

    Raises:
        FileNotFoundError: if `audit_path` is supplied explicitly and does
            not exist at construction time (strict mode).  The default path
            is allowed to be absent (empty audit state).
    """

    def __init__(self, audit_path: Path | None = None) -> None:
        if audit_path is not None:
            self._audit_path: Path = audit_path
            if not self._audit_path.exists():
                raise FileNotFoundError(f"Audit file not found: {self._audit_path}")
        else:
            self._audit_path = _DEFAULT_AUDIT_PATH
        self._bridge = RoutingOrchestratorBridge()

    @property
    def audit_path(self) -> Path:
        """The configured audit file path."""
        return self._audit_path

    def get_status(self, strict: bool = True) -> RouterStatus | None:
        """Return current `RouterStatus` derived from the latest audit entry.

        Reads the most recent audit record, synthesises a single-agent routing
        state, and returns the aggregated `RouterStatus`.

        Returns ``None`` when the audit file is absent or empty.

        Raises:
            ValueError: if the audit file is present but its latest entry
                cannot be decoded as JSON.
        """
        records = self.get_audit_history(limit=1, strict=strict)
        if not records:
            return None

        latest = records[0]
        provider: str = latest.get("provider", "unknown")
        model: str = latest.get("model", "unknown")

        # Map provider → routing mode for the bridge.
        mode = "TheGent" if provider == "thegent" else "Lifecycle"

        from thegent.utils.routing_impl.route_executor import RoutingDecision

        decision = RoutingDecision(
            mode=mode,
            risk_score=0.0,
            rationale=f"audit-derived: provider={provider} model={model}",
        )
        self._bridge.record_decision("tui-session", decision)
        return self._bridge.status()

    def get_audit_history(self, limit: int = 10, strict: bool = True) -> list[dict[str, Any]]:
        """Return the last `limit` routing audit records (chronological order).

        Reads directly from the JSONL file via `read_routing_audit`.

        Raises:
            ValueError: if the file exists but a line cannot be parsed as JSON.
        """
        if not self._audit_path.exists():
            return []

        raw_lines = self._audit_path.read_text(encoding="utf-8").splitlines()
        recent_lines = [ln.strip() for ln in raw_lines[-limit:] if ln.strip()]
        offset = len(raw_lines) - len(recent_lines)
        records, _errors = _parse_jsonl_lines(recent_lines, line_offset=offset, strict=strict)
        return records

    def get_pareto_data(self, strict: bool = True) -> dict[str, Any]:
        """Return aggregated Pareto data for the TUI panel.

        Shape::

            {
                "providers": [
                    {"name": str, "avg_cost_usd": float, "avg_latency_ms": float, "count": int},
                    ...
                ],
                "current": {
                    "provider": str,
                    "model": str,
                    "latency_ms": int,
                    "cost_usd": float,
                } | None,
                "history": [<raw audit record dicts>, ...],
            }

        Returns ``{"providers": [], "current": None, "history": []}`` when
        there are no audit records.

        Raises:
            ValueError: propagated from `get_audit_history` on malformed data.
        """
        raw_lines: list[str] = []
        parse_errors: list[str] = []
        if self._audit_path.exists():
            raw_lines = self._audit_path.read_text(encoding="utf-8").splitlines()
        recent_lines = [ln.strip() for ln in raw_lines[-10:] if ln.strip()]
        offset = len(raw_lines) - len(recent_lines)
        history, parse_errors = _parse_jsonl_lines(recent_lines, line_offset=offset, strict=strict)

        if not history:
            return {"providers": [], "current": None, "history": [], "parse_errors": parse_errors}

        # Aggregate per-provider statistics.
        provider_stats: dict[str, dict[str, Any]] = {}
        for rec in history:
            name: str = rec.get("provider", "unknown")
            cost: float = float(rec.get("cost", 0.0))
            latency: int = int(rec.get("latency_ms", 0))
            if name not in provider_stats:
                provider_stats[name] = {"total_cost": 0.0, "total_latency": 0, "count": 0}
            provider_stats[name]["total_cost"] += cost
            provider_stats[name]["total_latency"] += latency
            provider_stats[name]["count"] += 1

        providers = [
            {
                "name": name,
                "avg_cost_usd": stats["total_cost"] / stats["count"],
                "avg_latency_ms": stats["total_latency"] / stats["count"],
                "count": stats["count"],
            }
            for name, stats in sorted(provider_stats.items())
        ]

        latest = history[-1]
        current = {
            "provider": latest.get("provider", "unknown"),
            "model": latest.get("model", "unknown"),
            "latency_ms": int(latest.get("latency_ms", 0)),
            "cost_usd": float(latest.get("cost", 0.0)),
        }

        return {
            "providers": providers,
            "current": current,
            "history": history,
            "parse_errors": parse_errors,
        }
