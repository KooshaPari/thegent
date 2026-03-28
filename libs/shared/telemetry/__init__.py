"""
Phenotype Ecosystem - Shared Telemetry Library

Canonical telemetry primitives for distributed tracing and observability.
"""

# Tracing
class TraceContext:
    """Distributed trace context propagation."""
    
    def __init__(self, trace_id: str, span_id: str, parent_span_id: str | None = None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
    
    @classmethod
    def new(cls) -> "TraceContext":
        """Create a new trace context with generated IDs."""
        import uuid
        return cls(
            trace_id=str(uuid.uuid4()).replace("-", "")[:16],
            span_id=str(uuid.uuid4()).replace("-", "")[:8]
        )
    
    def with_child(self) -> "TraceContext":
        """Create a child span context."""
        return self.__class__(
            trace_id=self.trace_id,
            span_id=str(uuid.uuid4()).replace("-", "")[:8],
            parent_span_id=self.span_id
        )
    
    def to_headers(self) -> dict[str, str]:
        """Convert to propagation headers (W3C TraceContext format)."""
        return {
            "traceparent": f"00-{self.trace_id}-{self.span_id}{f'-{self.parent_span_id}' if self.parent_span_id else '00'}",
        }
    
    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> "TraceContext | None":
        """Parse from propagation headers."""
        traceparent = headers.get("traceparent", "")
        if not traceparent.startswith("00-"):
            return None
        parts = traceparent.split("-")
        if len(parts) < 3:
            return None
        return cls(
            trace_id=parts[1],
            span_id=parts[2][:8],
            parent_span_id=parts[2][9:] if len(parts[2]) > 9 else None
        )


# Metrics
class MetricsCollector:
    """Shared metrics collection with Prometheus-compatible format."""
    
    def __init__(self, prefix: str = "phenotype"):
        self.prefix = prefix
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
    
    def counter(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment a counter metric."""
        key = self._make_key(name, labels)
        self._counters[key] = self._counters.get(key, 0) + value
    
    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set a gauge metric."""
        key = self._make_key(name, labels)
        self._gauges[key] = value
    
    def histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record a histogram observation."""
        key = self._make_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
    
    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Create a metric key with labels."""
        if not labels:
            return f"{self.prefix}_{name}"
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{self.prefix}_{name}{{{label_str}}}"
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        for key, value in sorted(self._counters.items()):
            lines.append(f"{key} {value}")
        for key, value in sorted(self._gauges.items()):
            lines.append(f"{key} {value}")
        for key, values in sorted(self._histograms.items()):
            for v in values:
                lines.append(f"{key} {v}")
        return "\n".join(lines) + "\n"


# Logging with trace correlation
class TracingLogger:
    """Logger with automatic trace context correlation."""
    
    def __init__(self, name: str, collector: MetricsCollector | None = None):
        self.name = name
        self.collector = collector or MetricsCollector()
        self._context: TraceContext | None = None
    
    def set_context(self, context: TraceContext | None) -> None:
        """Set the current trace context for correlation."""
        self._context = context
    
    def info(self, message: str, **kwargs) -> None:
        """Log info with trace correlation."""
        self._log("INFO", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error with trace correlation."""
        self._log("ERROR", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning with trace correlation."""
        self._log("WARNING", message, **kwargs)
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """Internal log implementation."""
        import datetime
        timestamp = datetime.datetime.utcnow().isoformat()
        trace_info = ""
        if self._context:
            trace_info = f" [trace_id={self._context.trace_id} span_id={self._context.span_id}]"
        print(f"{timestamp} {level}{trace_info} {self.name}: {message}")
        if kwargs:
            print(f"  Extra: {kwargs}")
        if level == "ERROR":
            self.collector.counter("log_errors_total", labels={"logger": self.name, "level": "error"})


# Health checks
class HealthCheck:
    """Standardized health check implementation."""
    
    def __init__(self, name: str):
        self.name = name
        self._checks: dict[str, bool] = {}
    
    def register(self, component: str, healthy: bool) -> None:
        """Register a component health status."""
        self._checks[component] = healthy
    
    def is_healthy(self) -> bool:
        """Return overall health status."""
        return all(self._checks.values()) if self._checks else True
    
    def report(self) -> dict:
        """Return detailed health report."""
        return {
            "healthy": self.is_healthy(),
            "checks": self._checks.copy()
        }


# Export public interface
__all__ = [
    "TraceContext",
    "MetricsCollector", 
    "TracingLogger",
    "HealthCheck",
]
