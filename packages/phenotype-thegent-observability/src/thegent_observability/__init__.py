"""thegent-observability: Telemetry, metrics, monitoring, and tracing for thegent.

This package contains observability infrastructure migrated from the thegent monolith:
- telemetry/      : Telemetry collection (stub/init module)
- metrics/        : Metrics collector
- monitoring/     : Health checks
- observability/  : Analytics, async logging, egress, explainability, OTel, Prometheus
- trace/          : Deterministic replay tracing (TraceRecorder, schema, integration)
- logging_utils/  : Log formatters
"""

# Re-exports will be enabled after import paths are rewritten.
# For now, import submodules directly:
#   from thegent_observability.trace import TraceRecorder
