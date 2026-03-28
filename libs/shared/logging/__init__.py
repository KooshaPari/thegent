"""
Shared Logging Utilities
=======================

Centralized logging configuration for the Phenotype ecosystem.

Features:
- Structured logging with context
- Log level management
- Multiple output formats (JSON, console)
- Performance metrics logging
- Security event logging

Based on DRY principle - single logging configuration across all repos.

Architecture:
    - StructuredLogger: Main logger interface with context support
    - LogFormatter: Formats logs for different outputs
    - SecurityLogHandler: Specialized handler for security events

Usage:
    from libs.shared.logging import StructuredLogger

    logger = StructuredLogger("my-component")
    logger.info("Operation completed", operation="data_sync", duration_ms=150)

Principles:
    - No hardcoded log messages (use message catalogs)
    - Always include correlation IDs for tracing
    - Structured fields for searchability
    - Performance impact < 5ms per log call
"""

from typing import Any, Dict, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging
from enum import Enum


class LogLevel(Enum):
    """Log levels following syslog conventions."""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    SECURITY = 50


@dataclass
class LogEntry:
    """Structured log entry with context."""
    timestamp: datetime
    level: LogLevel
    message: str
    component: str
    operation: Optional[str] = None
    duration_ms: Optional[float] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.name,
            "message": self.message,
            "component": self.component,
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "metadata": self.metadata,
        }


class LogFormatter:
    """Format log entries for different output targets."""

    @staticmethod
    def to_json(entry: LogEntry) -> str:
        """Format as JSON for structured logging systems."""
        return json.dumps(entry.to_dict())

    @staticmethod
    def to_console(entry: LogEntry) -> str:
        """Format for console output with colors."""
        level_colors = {
            LogLevel.TRACE: "\033[36m",    # Cyan
            LogLevel.DEBUG: "\033[34m",     # Blue
            LogLevel.INFO: "\033[32m",      # Green
            LogLevel.WARNING: "\033[33m",   # Yellow
            LogLevel.ERROR: "\033[31m",     # Red
            LogLevel.SECURITY: "\033[35m",  # Magenta
        }
        reset = "\033[0m"
        color = level_colors.get(entry.level, "")
        return (
            f"{color}{entry.timestamp:%H:%M:%S}{reset} "
            f"[{entry.level.name:8}] "
            f"{entry.component}: "
            f"{entry.message}"
        )


class StructuredLogger:
    """
    Main logger interface with structured context support.

    Implements DRY by centralizing logging configuration.
    All components should use this instead of direct logging calls.

    Usage:
        logger = StructuredLogger("api-gateway")
        logger.info("Request processed",
                    path="/api/users",
                    method="GET",
                    status=200)
    """

    def __init__(
        self,
        component: str,
        level: LogLevel = LogLevel.INFO,
        formatter: Optional[LogFormatter] = None,
    ):
        self.component = component
        self.level = level
        self.formatter = formatter or LogFormatter()
        self._correlation_id: Optional[str] = None

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracing."""
        self._correlation_id = correlation_id

    def _create_entry(
        self,
        level: LogLevel,
        message: str,
        **kwargs: Any,
    ) -> LogEntry:
        """Create structured log entry."""
        return LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            message=message,
            component=self.component,
            correlation_id=self._correlation_id,
            **kwargs,
        )

    def trace(self, message: str, **kwargs: Any) -> None:
        """Log trace level message."""
        if self.level.value <= LogLevel.TRACE.value:
            entry = self._create_entry(LogLevel.TRACE, message, **kwargs)
            print(self.formatter.to_console(entry))

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug level message."""
        if self.level.value <= LogLevel.DEBUG.value:
            entry = self._create_entry(LogLevel.DEBUG, message, **kwargs)
            print(self.formatter.to_console(entry))

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info level message."""
        if self.level.value <= LogLevel.INFO.value:
            entry = self._create_entry(LogLevel.INFO, message, **kwargs)
            print(self.formatter.to_console(entry))

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning level message."""
        if self.level.value <= LogLevel.WARNING.value:
            entry = self._create_entry(LogLevel.WARNING, message, **kwargs)
            print(self.formatter.to_console(entry))

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error level message."""
        if self.level.value <= LogLevel.ERROR.value:
            entry = self._create_entry(LogLevel.ERROR, message, **kwargs)
            print(self.formatter.to_console(entry))

    def security(self, message: str, **kwargs: Any) -> None:
        """Log security-related event (CRITICAL)."""
        if self.level.value <= LogLevel.SECURITY.value:
            entry = self._create_entry(LogLevel.SECURITY, message, **kwargs)
            print(self.formatter.to_console(entry))


class SecurityLogHandler:
    """
    Specialized handler for security events.

    Security events are logged separately for audit compliance.
    Format is designed for SIEM integration.
    """

    def log_authentication(
        self,
        event: str,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Log authentication event."""
        logger = StructuredLogger("security")
        logger.security(
            f"Authentication {event}: {'success' if success else 'failure'}",
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            **kwargs,
        )

    def log_authorization(
        self,
        event: str,
        user_id: str,
        resource: str,
        allowed: bool,
        **kwargs: Any,
    ) -> None:
        """Log authorization event."""
        logger = StructuredLogger("security")
        logger.security(
            f"Authorization {event}: {'allowed' if allowed else 'denied'}",
            user_id=user_id,
            resource=resource,
            allowed=allowed,
            **kwargs,
        )

    def log_data_access(
        self,
        operation: str,
        user_id: str,
        resource: str,
        record_count: int,
        **kwargs: Any,
    ) -> None:
        """Log data access for compliance."""
        logger = StructuredLogger("security")
        logger.info(
            f"Data access: {operation}",
            user_id=user_id,
            resource=resource,
            record_count=record_count,
            **kwargs,
        )


# Convenience exports
StructuredLog = StructuredLogger
Log = StructuredLogger