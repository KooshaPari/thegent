"""TelemetryPort: Interface for logging and metrics."""

from __future__ import annotations

from typing import Any, Protocol


class TelemetryPort(Protocol):
    """Port interface for logging and metrics collection."""

    def log_info(self, event: str, **kwargs: Any) -> None:
        """Log an informational event.

        Args:
            event: Event name or message.
            **kwargs: Additional context data.
        """
        ...

    def log_warning(self, event: str, **kwargs: Any) -> None:
        """Log a warning event.

        Args:
            event: Event name or message.
            **kwargs: Additional context data.
        """
        ...

    def log_error(self, event: str, **kwargs: Any) -> None:
        """Log an error event.

        Args:
            event: Event name or message.
            **kwargs: Additional context data.
        """
        ...

    def log_debug(self, event: str, **kwargs: Any) -> None:
        """Log a debug event.

        Args:
            event: Event name or message.
            **kwargs: Additional context data.
        """
        ...

    def record_metric(self, metric_name: str, value: float, **kwargs: Any) -> None:
        """Record a numerical metric.

        Args:
            metric_name: Name of the metric.
            value: Metric value.
            **kwargs: Additional tags/labels.
        """
        ...


__all__ = [
    "TelemetryPort",
]
