"""Contract telemetry and drift detection for agent outputs.

Tracks normalization performance, fallback frequency, and detects structural
or semantic drift in agent outputs. Emits schema.drift.structural and
schema.drift.semantic events per G-RV-07.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

# Drift event types for alerting (G-RV-07)
EVENT_NORMALIZATION = "normalization"
EVENT_SCHEMA_DRIFT_STRUCTURAL = "schema.drift.structural"
EVENT_SCHEMA_DRIFT_SEMANTIC = "schema.drift.semantic"


class ContractTelemetry:
    """Tracks contract normalization events and drift."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.telemetry_path = session_dir / "contract_telemetry.jsonl"

    def record_normalization(
        self,
        run_id: str,
        provider: str,
        contract: str,
        confidence: float,
        success: bool,
        errors: list[str] | None = None,
        event_type: str = EVENT_NORMALIZATION,
    ) -> None:
        """Record a normalization event. Use event_type for drift classification."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "run_id": run_id,
            "provider": provider,
            "contract": contract,
            "confidence": confidence,
            "success": success,
            "errors": errors or [],
        }
        with self.telemetry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def emit_drift_event(
        self,
        run_id: str,
        provider: str,
        contract: str,
        drift_type: Literal["structural", "semantic"],
        details: dict[str, Any] | None = None,
    ) -> None:
        """Emit a schema drift event for alerting (G-RV-07)."""
        event_type = EVENT_SCHEMA_DRIFT_STRUCTURAL if drift_type == "structural" else EVENT_SCHEMA_DRIFT_SEMANTIC
        self.session_dir.mkdir(parents=True, exist_ok=True)
        drift_event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "run_id": run_id,
            "provider": provider,
            "contract": contract,
            "drift_type": drift_type,
            "details": details or {},
        }
        with self.telemetry_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(drift_event) + "\n")

    def get_drift_budget_status(
        self,
        structural_budget_pct: float = 5.0,
        semantic_budget_pct: float = 10.0,
        limit: int = 500,
    ) -> dict[str, Any]:
        """Check if drift rates exceed alert budgets (G-RV-07)."""
        if not self.telemetry_path.exists():
            return {
                "within_budget": True,
                "structural_rate_pct": 0.0,
                "semantic_rate_pct": 0.0,
                "structural_budget_pct": structural_budget_pct,
                "semantic_budget_pct": semantic_budget_pct,
            }
        events = []
        with self.telemetry_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        recent = events[-limit:]
        total = len(recent)
        structural_count = sum(1 for e in recent if e.get("event_type") == EVENT_SCHEMA_DRIFT_STRUCTURAL)
        semantic_count = sum(1 for e in recent if e.get("event_type") == EVENT_SCHEMA_DRIFT_SEMANTIC)
        structural_rate = (structural_count / total * 100.0) if total else 0.0
        semantic_rate = (semantic_count / total * 100.0) if total else 0.0
        within = structural_rate <= structural_budget_pct and semantic_rate <= semantic_budget_pct
        return {
            "within_budget": within,
            "structural_rate_pct": round(structural_rate, 2),
            "semantic_rate_pct": round(semantic_rate, 2),
            "structural_budget_pct": structural_budget_pct,
            "semantic_budget_pct": semantic_budget_pct,
        }

    def get_stats(self, limit: int = 100, provider: str | None = None) -> dict[str, Any]:
        """Calculate statistics on recent normalization events."""
        if not self.telemetry_path.exists():
            return {"total": 0, "success_rate": 0.0, "fallback_rate": 0.0, "avg_confidence": 0.0}

        events = []
        with self.telemetry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if provider and data.get("provider") != provider:
                        continue
                    events.append(data)
                except Exception:
                    continue

        recent = events[-limit:]
        if not recent:
            return {"total": 0, "success_rate": 0.0, "fallback_rate": 0.0, "avg_confidence": 0.0}

        total = len(recent)
        successes = sum(1 for e in recent if e.get("success"))
        fallbacks = sum(1 for e in recent if e.get("contract") == "fallback-plain")
        avg_conf = sum(float(e.get("confidence", 0.0)) for e in recent) / total

        return {
            "total": total,
            "success_rate": successes / total,
            "fallback_rate": fallbacks / total,
            "avg_confidence": avg_conf,
            "by_provider": self._group_by(recent, "provider"),
        }

    def _group_by(self, events: list[dict], key: str) -> dict[str, Any]:
        groups: dict[str, list[float]] = {}
        for e in events:
            val = e.get(key, "unknown")
            conf = e.get("confidence", 0.0)
            if val not in groups:
                groups[val] = []
            groups[val].append(conf)

        return {k: sum(v) / len(v) for k, v in groups.items()}

    def get_fallback_kpis(
        self,
        limit: int = 500,
        structural_budget_pct: float = 5.0,
        semantic_budget_pct: float = 10.0,
        provider: str | None = None,
    ) -> dict[str, Any]:
        """Return fallback KPIs for dashboard/alerting (G-CA-02 B3).

        Args:
            provider: Optional provider filter for KPI windows.
        """
        if not self.telemetry_path.exists():
            return {
                "total": 0,
                "fallback_rate": 0.0,
                "success_rate": 0.0,
                "avg_confidence": 0.0,
                "by_provider": {},
                "structural_drift_pct": 0.0,
                "semantic_drift_pct": 0.0,
            }

        events = []
        with self.telemetry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue
        recent = events[-limit:]

        provider_filter = (provider or "").strip().lower()
        if provider_filter:
            recent = [event for event in recent if str(event.get("provider", "")).strip().lower() == provider_filter]

        total = len(recent)
        fallbacks = sum(1 for e in recent if e.get("contract") == "fallback-plain")
        successes = sum(1 for e in recent if e.get("success"))
        avg_conf = sum(float(e.get("confidence", 0.0)) for e in recent) / total if total else 0.0

        by_provider: dict[str, dict[str, float]] = {}
        for e in recent:
            p = e.get("provider", "unknown")
            if p not in by_provider:
                by_provider[p] = {"total": 0, "fallbacks": 0, "successes": 0, "conf_sum": 0.0}
            by_provider[p]["total"] += 1
            if e.get("contract") == "fallback-plain":
                by_provider[p]["fallbacks"] += 1
            if e.get("success"):
                by_provider[p]["successes"] += 1
            by_provider[p]["conf_sum"] += float(e.get("confidence", 0.0))
        for p, v in by_provider.items():
            t = v["total"]
            by_provider[p] = {
                "fallback_rate": v["fallbacks"] / t if t else 0.0,
                "success_rate": v["successes"] / t if t else 0.0,
                "avg_confidence": v["conf_sum"] / t if t else 0.0,
                "total": t,
            }

        budget = self.get_drift_budget_status(structural_budget_pct, semantic_budget_pct, limit)

        return {
            "total": total,
            "fallback_rate": fallbacks / total if total else 0.0,
            "success_rate": successes / total if total else 0.0,
            "avg_confidence": avg_conf,
            "by_provider": by_provider,
            "structural_drift_pct": budget["structural_rate_pct"],
            "semantic_drift_pct": budget["semantic_rate_pct"],
        }

    def detect_drift(self, window_size: int = 50, drift_threshold: float = 0.15) -> list[str]:
        """Detect significant drift in contract performance by comparing recent to historical.

        Analyzes fallback rate and confidence score drops.
        """
        if not self.telemetry_path.exists():
            return []

        all_events = []
        with self.telemetry_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    all_events.append(json.loads(line))
                except Exception:
                    continue

        if len(all_events) < window_size * 2:
            return []

        recent = all_events[-window_size:]
        historical = all_events[:-window_size][-window_size * 2 :]  # middle slice

        def get_metrics(evs):
            tot = len(evs)
            fb = sum(1 for e in evs if e.get("contract") == "fallback-plain") / tot
            cf = sum(float(e.get("confidence", 0.0)) for e in evs) / tot
            return fb, cf

        r_fb, r_cf = get_metrics(recent)
        h_fb, h_cf = get_metrics(historical)

        issues = []
        if r_fb > h_fb + drift_threshold:
            issues.append(f"Significant increase in fallback rate: {h_fb:.1%} -> {r_fb:.1%}")
        if r_cf < h_cf - drift_threshold:
            issues.append(f"Significant drop in normalization confidence: {h_cf:.2f} -> {r_cf:.2f}")

        # Provider-specific drift
        providers = {e.get("provider") for e in recent}
        for p in providers:
            r_p = [e for e in recent if e.get("provider") == p]
            h_p = [e for e in all_events[:-window_size] if e.get("provider") == p]
            if len(r_p) >= 5 and len(h_p) >= 10:
                rp_fb, rp_cf = get_metrics(r_p)
                hp_fb, hp_cf = get_metrics(h_p)
                if rp_fb > hp_fb + drift_threshold * 1.5:
                    issues.append(f"Provider {p} fallback rate regressed: {hp_fb:.1%} -> {rp_fb:.1%}")
                if rp_cf < hp_cf - drift_threshold * 1.5:
                    issues.append(f"Provider {p} confidence regressed: {hp_cf:.2f} -> {rp_cf:.2f}")

        return issues

    def get_trend_analysis(self, window_size: int = 50) -> dict[str, Any]:
        """WP-7009: Detailed trend analysis for contract health."""
        drift_issues = self.detect_drift(window_size=window_size)
        kpis = self.get_fallback_kpis(limit=window_size * 2)

        return {
            "drift_issues": drift_issues,
            "status": "healthy" if not drift_issues else "degraded",
            "kpis": kpis,
            "recommendation": self._suggest_remediation(drift_issues),
        }

    def _suggest_remediation(self, issues: list[str]) -> str:
        """WP-7010: Remediation hooks for detected drift."""
        if not issues:
            return "No remediation needed."

        if any("fallback rate" in i for i in issues):
            return "Action: Update provider adapters or refresh parser schemas."
        if any("confidence" in i for i in issues):
            return "Action: Review semantic validation rules or provider prompt templates."

        return "Action: Investigate recent provider API changes."


def detect_drift(stats: dict[str, Any], threshold: float = 0.2) -> list[str]:
    """Legacy helper for simple drift detection."""
    issues = []
    if stats.get("fallback_rate", 0.0) > threshold:
        issues.append(f"High fallback rate detected: {stats['fallback_rate']:.1%}")
    return issues


def rank_providers_by_parser_quality(
    providers: list[str],
    telemetry: "ContractTelemetry",
    limit: int = 100,
) -> list[str]:
    """Order providers by parser quality: higher confidence, lower fallback rate first (G-CA-02 B2)."""
    if not providers:
        return []
    kpis = telemetry.get_fallback_kpis(limit=limit)
    by_provider = kpis.get("by_provider", {})

    def score(p: str) -> tuple[float, float]:
        v = by_provider.get(p, {})
        conf = v.get("avg_confidence", 0.5)
        fb = v.get("fallback_rate", 0.5)
        return (conf, -fb)  # higher confidence first, then lower fallback

    return sorted(providers, key=score, reverse=True)
