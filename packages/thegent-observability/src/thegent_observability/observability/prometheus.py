"""GW-34: Prometheus /metrics endpoint for LLM gateway observability.

Exposes token counts, latency, cost, error rates, and cache hits in
Prometheus text format (version 0.0.4).

Uses a simple custom text-format writer that is always available without
any external dependency. prometheus_client is NOT required.

# @trace FR-OBS-034
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, ClassVar

METRIC_HELP: dict[str, tuple[str, str]] = {
    "thegent_requests_total": ("counter", "Total LLM gateway requests"),
    "thegent_tokens_total": ("counter", "Total LLM tokens processed"),
    "thegent_request_duration_seconds": ("histogram", "LLM request duration in seconds"),
    "thegent_cost_usd_total": ("counter", "Total LLM cost in USD"),
    "thegent_cache_hits_total": ("counter", "Total cache hits"),
    "thegent_cache_misses_total": ("counter", "Total cache misses"),
    "thegent_circuit_breaker_open": ("gauge", "Circuit breaker state (1=open, 0=closed)"),
    "thegent_errors_total": ("counter", "Total LLM gateway errors"),
    "thegent_autosync_cycles_total": ("counter", "Total autosync cycles"),
    "thegent_autosync_items_total": ("counter", "Total autosync items observed"),
    "thegent_autosync_connector_operations_total": ("counter", "Total autosync connector operations"),
    "thegent_autosync_connector_operation_duration_seconds": (
        "histogram",
        "Autosync connector operation duration in seconds",
    ),
    "thegent_board_sync_cycles_total": ("counter", "Total board sync cycles by source and status"),
    "thegent_board_sync_cycle_duration_seconds": ("histogram", "Board sync cycle duration in seconds"),
    "thegent_autosync_cycle_outcomes_total": ("counter", "Total autosync cycles by outcome"),
    "thegent_autosync_cycle_duration_seconds": ("histogram", "Autosync cycle duration in seconds"),
    "thegent_autosync_circuit_open_total": ("counter", "Autosync operations blocked by open connector circuits"),
    "thegent_autosync_cycle_health": ("gauge", "Autosync cycle health (1=ok, 0=degraded)"),
}


def _labels_to_str(labels: dict[str, str]) -> str:
    """Render a labels dict to Prometheus label string, sorted alphabetically.

    Example: {"model": "gpt-4o", "provider": "openai"} -> 'model="gpt-4o",provider="openai"'
    """
    if not labels:
        return ""
    parts = [f'{k}="{v}"' for k, v in sorted(labels.items())]
    return ",".join(parts)


def _metric_line(name: str, labels: dict[str, str], value: float) -> str:
    """Render a single metric line in Prometheus text format."""
    label_str = _labels_to_str(labels)
    if label_str:
        return f"{name}{{{label_str}}} {value:g}"
    return f"{name} {value:g}"


class MetricsCollector:
    """Thread-safe collector for LLM gateway Prometheus metrics.

    Metrics:
        thegent_requests_total{model,provider,status} — counter
        thegent_tokens_total{model,provider,type} — counter (type: prompt|completion)
        thegent_request_duration_seconds{model,provider} — histogram
        thegent_cost_usd_total{model,provider} — counter
        thegent_cache_hits_total{cache_type} — counter (cache_type: exact|semantic)
        thegent_cache_misses_total{cache_type} — counter
        thegent_circuit_breaker_open{provider} — gauge (1=open, 0=closed/half-open)
        thegent_errors_total{model,provider,error_type} — counter
    """

    HISTOGRAM_BUCKETS: ClassVar[list[float]] = [
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
        float("inf"),
    ]

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # Each metric is a dict[frozenset[tuple], numeric_value]
        # where the frozenset is the label set
        self._counters: dict[str, dict[frozenset, float]] = {}
        self._gauges: dict[str, dict[frozenset, float]] = {}
        # Histograms store raw observations as a list[float] per label set
        self._histograms: dict[str, dict[frozenset, list[float]]] = {}

    def _label_key(self, labels: dict[str, str]) -> frozenset:
        """Convert a labels dict to a frozenset key for storage."""
        return frozenset(labels.items())

    def _key_to_dict(self, key: frozenset) -> dict[str, str]:
        """Convert a frozenset key back to a sorted labels dict."""
        return dict(sorted(key))

    def inc(self, name: str, labels: dict[str, str], value: float = 1.0) -> None:
        """Increment a counter."""
        key = self._label_key(labels)
        with self._lock:
            bucket = self._counters.setdefault(name, {})
            bucket[key] = bucket.get(key, 0.0) + value

    def set_gauge(self, name: str, labels: dict[str, str], value: float) -> None:
        """Set a gauge value."""
        key = self._label_key(labels)
        with self._lock:
            bucket = self._gauges.setdefault(name, {})
            bucket[key] = value

    def observe(self, name: str, labels: dict[str, str], value: float) -> None:
        """Record a histogram observation."""
        key = self._label_key(labels)
        with self._lock:
            bucket = self._histograms.setdefault(name, {})
            bucket.setdefault(key, []).append(value)

    def record_request(
        self,
        model: str,
        provider: str,
        status: str,
        duration_sec: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost_usd: float = 0.0,
        error_type: str = "",
    ) -> None:
        """Record all metrics for a completed LLM request.

        Increments:
          thegent_requests_total{model, provider, status}
          thegent_tokens_total{model, provider, type="prompt"} += prompt_tokens
          thegent_tokens_total{model, provider, type="completion"} += completion_tokens
          thegent_request_duration_seconds{model, provider} histogram
          thegent_cost_usd_total{model, provider} += cost_usd
          thegent_errors_total{model, provider, error_type} if status == "error"
        """
        base_labels = {"model": model, "provider": provider}

        self.inc("thegent_requests_total", {**base_labels, "status": status})

        if prompt_tokens:
            self.inc(
                "thegent_tokens_total",
                {**base_labels, "type": "prompt"},
                float(prompt_tokens),
            )
        if completion_tokens:
            self.inc(
                "thegent_tokens_total",
                {**base_labels, "type": "completion"},
                float(completion_tokens),
            )

        self.observe("thegent_request_duration_seconds", base_labels, duration_sec)

        if cost_usd:
            self.inc("thegent_cost_usd_total", base_labels, cost_usd)

        if status == "error" and error_type:
            self.inc(
                "thegent_errors_total",
                {**base_labels, "error_type": error_type},
            )

    def record_cache_hit(self, cache_type: str = "exact") -> None:
        """Record a cache hit (thegent_cache_hits_total{cache_type})."""
        self.inc("thegent_cache_hits_total", {"cache_type": cache_type})

    def record_cache_miss(self, cache_type: str = "exact") -> None:
        """Record a cache miss (thegent_cache_misses_total{cache_type})."""
        self.inc("thegent_cache_misses_total", {"cache_type": cache_type})

    def set_circuit_breaker(self, provider: str, is_open: bool) -> None:
        """Set the circuit breaker gauge for a provider (1=open, 0=closed)."""
        self.set_gauge(
            "thegent_circuit_breaker_open",
            {"provider": provider},
            1.0 if is_open else 0.0,
        )

    def record_autosync_cycle(self, *, items_count: int, ignored_count: int, had_error: bool) -> None:
        """Record one autosync cycle aggregate."""
        self.inc("thegent_autosync_cycles_total", {})
        self.inc("thegent_autosync_items_total", {"kind": "processed"}, float(items_count))
        if ignored_count:
            self.inc("thegent_autosync_items_total", {"kind": "ignored"}, float(ignored_count))
        self.set_gauge("thegent_autosync_cycle_health", {}, 0.0 if had_error else 1.0)

    def record_autosync_connector_operation(
        self,
        *,
        connector: str,
        direction: str,
        result: str,
        duration_seconds: float,
    ) -> None:
        """Record one autosync connector operation."""
        labels = {
            "connector": connector,
            "direction": direction,
            "result": result,
        }
        self.inc("thegent_autosync_connector_operations_total", labels)
        self.observe(
            "thegent_autosync_connector_operation_duration_seconds",
            {"connector": connector, "direction": direction},
            duration_seconds,
        )

    def record_autosync_circuit_open(self, *, connector: str, direction: str) -> None:
        """Record a connector operation blocked by an open circuit."""
        self.inc(
            "thegent_autosync_circuit_open_total",
            {"connector": connector, "direction": direction},
        )

    def record_board_sync_cycle(self, *, source: str, status: str, duration_seconds: float) -> None:
        """Record one board sync cycle and duration."""
        self.inc(
            "thegent_board_sync_cycles_total",
            {"source": source, "status": status},
        )
        self.observe("thegent_board_sync_cycle_duration_seconds", {"source": source}, duration_seconds)

    def record_autosync_cycle_result(self, *, status: str, duration_seconds: float) -> None:
        """Record one autosync cycle outcome and duration."""
        self.inc("thegent_autosync_cycle_outcomes_total", {"status": status})
        self.observe("thegent_autosync_cycle_duration_seconds", {"status": status}, duration_seconds)

    def render_text(self) -> str:
        """Render all metrics in Prometheus text format 0.0.4.

        Returns a string with HELP/TYPE headers followed by metric lines.
        Counters and gauges emit one line per label set.
        Histograms emit _bucket, _count, and _sum lines per label set.
        """
        with self._lock:
            # Snapshot all data under the lock to avoid races during rendering
            counters_snap = {n: dict(v) for n, v in self._counters.items()}
            gauges_snap = {n: dict(v) for n, v in self._gauges.items()}
            histograms_snap = {n: {k: list(obs) for k, obs in v.items()} for n, v in self._histograms.items()}

        lines: list[str] = []

        def _help_type(name: str) -> None:
            """Emit HELP and TYPE lines for a metric if it has known metadata."""
            if name in METRIC_HELP:
                metric_type, description = METRIC_HELP[name]
                lines.append(f"# HELP {name} {description}")
                lines.append(f"# TYPE {name} {metric_type}")

        # --- Counters ---
        for name in sorted(counters_snap):
            _help_type(name)
            for key in sorted(counters_snap[name], key=lambda k: sorted(k)):
                label_dict = self._key_to_dict(key)
                value = counters_snap[name][key]
                lines.append(_metric_line(name, label_dict, value))

        # --- Gauges ---
        for name in sorted(gauges_snap):
            _help_type(name)
            for key in sorted(gauges_snap[name], key=lambda k: sorted(k)):
                label_dict = self._key_to_dict(key)
                value = gauges_snap[name][key]
                lines.append(_metric_line(name, label_dict, value))

        # --- Histograms ---
        for name in sorted(histograms_snap):
            _help_type(name)
            for key in sorted(histograms_snap[name], key=lambda k: sorted(k)):
                observations = histograms_snap[name][key]
                label_dict = self._key_to_dict(key)
                label_str = _labels_to_str(label_dict)

                count = len(observations)
                total = sum(observations)

                # Emit one _bucket line per threshold
                for le in self.HISTOGRAM_BUCKETS:
                    if le == float("inf"):
                        le_str = "+Inf"
                        cumulative = count
                    else:
                        cumulative = sum(1 for v in observations if v <= le)
                        le_str = f"{le:g}"

                    if label_str:
                        bucket_labels = f'{label_str},le="{le_str}"'
                    else:
                        bucket_labels = f'le="{le_str}"'
                    lines.append(f"{name}_bucket{{{bucket_labels}}} {cumulative}")

                # _count and _sum
                if label_str:
                    lines.append(f"{name}_count{{{label_str}}} {count}")
                    lines.append(f"{name}_sum{{{label_str}}} {total:g}")
                else:
                    lines.append(f"{name}_count {count}")
                    lines.append(f"{name}_sum {total:g}")

        return "\n".join(lines) + ("\n" if lines else "")

    def export_text_file(self, output_path: Path) -> None:
        """Write rendered Prometheus text to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.render_text(), encoding="utf-8")


# ---------------------------------------------------------------------------
# Singleton helpers
# ---------------------------------------------------------------------------

_collector: MetricsCollector | None = None
_collector_lock = threading.Lock()


def get_metrics_collector() -> MetricsCollector:
    """Return the process-global MetricsCollector singleton."""
    global _collector
    if _collector is None:
        with _collector_lock:
            if _collector is None:
                _collector = MetricsCollector()
    return _collector


def reset_metrics_collector() -> None:
    """Reset the singleton (for testing only)."""
    global _collector
    with _collector_lock:
        _collector = None


# ---------------------------------------------------------------------------
# ASGI endpoint
# ---------------------------------------------------------------------------


async def metrics_endpoint(_request: Any) -> Any:
    """ASGI-compatible /metrics endpoint handler.

    Returns Prometheus text format with Content-Type: text/plain; version=0.0.4; charset=utf-8
    """
    from starlette.responses import Response

    collector = get_metrics_collector()
    text = collector.render_text()
    return Response(
        content=text,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
