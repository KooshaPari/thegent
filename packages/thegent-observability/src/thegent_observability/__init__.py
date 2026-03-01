"""thegent-observability: Telemetry, metrics, monitoring, and tracing for thegent.

This package contains observability infrastructure migrated from the thegent monolith:
- telemetry/      : Telemetry collection (stub/init module)
- metrics/        : Metrics collector
- monitoring/     : Health checks
- observability/  : Analytics, async logging, egress, explainability, OTel, Prometheus
- trace/          : Deterministic replay tracing (TraceRecorder, schema, integration)
- logging_utils/  : Log formatters
"""

from thegent_observability.trace import (
    DecisionRecord,
    ExecutionMetrics,
    RecorderConfig,
    RedactionConfig,
    SessionRecord,
    ToolCallRecord,
    TraceCleanup,
    TraceFile,
    TraceRecord,
    TraceRecorder,
    TraceRecordingContext,
    TracedAgentRunner,
    TruncationConfig,
    create_traced_agent_runner,
    estimate_trace_overhead,
)

__all__ = [
    # trace
    "DecisionRecord",
    "ExecutionMetrics",
    "RecorderConfig",
    "RedactionConfig",
    "SessionRecord",
    "ToolCallRecord",
    "TraceCleanup",
    "TraceFile",
    "TraceRecord",
    "TraceRecorder",
    "TraceRecordingContext",
    "TracedAgentRunner",
    "TruncationConfig",
    "create_traced_agent_runner",
    "estimate_trace_overhead",
]
