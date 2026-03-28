"""
Telemetry integration for services.
Provides structured logging, metrics, and distributed tracing.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any
import json


class LogLevel(str, Enum):
    """Standard log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Structured log entry."""
    level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    service: str = "unknown"
    component: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "service": self.service,
            "component": self.component,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            **self.extra,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class TelemetryService:
    """Base telemetry service for Phenotype services."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._logs: list[LogEntry] = []

    def log(self, level: LogLevel, message: str, **kwargs):
        """Log a message at the specified level."""
        entry = LogEntry(
            level=level,
            message=message,
            service=self.service_name,
            extra=kwargs,
        )
        self._logs.append(entry)
        print(entry.to_json())

    def debug(self, message: str, **kwargs):
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        self.log(LogLevel.CRITICAL, message, **kwargs)


# Telemetry integration patterns:
#
# 1. Structured Logging
#    - Always log with structured fields (JSON)
#    - Include trace_id and span_id for correlation
#    - Use standard log levels
#
# 2. Metrics
#    - Counter: track occurrences (errors, requests)
#    - Gauge: track current values (queue depth, connections)
#    - Histogram: track distributions (latency, response size)
#
# 3. Distributed Tracing
#    - Generate trace_id on request entry
#    - Propagate trace_id to all downstream calls
#    - Record spans for each operation
