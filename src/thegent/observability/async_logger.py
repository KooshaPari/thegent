"""GW-39: Async fire-and-forget observability logging.

Provides non-blocking background logging of LLM call events.
Does NOT impact the hot request path — events are queued and processed
by a background thread.

# @trace FR-OBS-039
"""

from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar

_log = logging.getLogger(__name__)


@dataclass
class ObservabilityEvent:
    """A single LLM call event to log."""

    timestamp: float
    event_type: str  # "request_complete" | "cache_hit" | "circuit_open" | "budget_alert"
    model: str
    provider: str
    event_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _default_log_handler(event: ObservabilityEvent) -> None:
    """Default handler: log to Python logging at DEBUG level."""
    _log.debug(
        "obs event_type=%s model=%s provider=%s event_id=%s metadata=%s",
        event.event_type,
        event.model,
        event.provider,
        event.event_id,
        event.metadata,
    )


class AsyncObservabilityLogger:
    """Background-thread observability logger.

    Events are enqueued (non-blocking) and processed by a daemon thread.
    If the queue is full, events are silently dropped (never blocks the hot path).
    """

    MAX_QUEUE_SIZE: ClassVar[int] = 10_000

    def __init__(self, handlers: list[Callable[[ObservabilityEvent], None]] | None = None) -> None:
        self._queue: queue.Queue[ObservabilityEvent] = queue.Queue(maxsize=self.MAX_QUEUE_SIZE)
        self._handlers = handlers or [_default_log_handler]
        self._thread: threading.Thread = threading.Thread(target=self._worker, daemon=True, name="obs-logger")
        self._running = threading.Event()
        self._running.set()
        self._thread.start()

    def log(self, event: ObservabilityEvent) -> None:
        """Enqueue an event (non-blocking). Drops if queue is full."""
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            pass  # Drop silently — never block the hot path

    def log_request(
        self,
        model: str,
        provider: str,
        event_id: str,
        status: str,
        duration_sec: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost_usd: float = 0.0,
        error_type: str = "",
    ) -> None:
        """Convenience: enqueue a request_complete event."""
        self.log(
            ObservabilityEvent(
                timestamp=time.time(),
                event_type="request_complete",
                model=model,
                provider=provider,
                event_id=event_id,
                metadata={
                    "status": status,
                    "duration_sec": duration_sec,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "cost_usd": cost_usd,
                    "error_type": error_type,
                },
            )
        )

    def _worker(self) -> None:
        """Background worker that processes events from the queue."""
        while self._running.is_set():
            try:
                event = self._queue.get(timeout=1.0)
                for handler in self._handlers:
                    try:
                        handler(event)
                    except Exception:
                        pass  # Handler errors must never kill the worker
                self._queue.task_done()
            except queue.Empty:
                continue

    def stop(self, timeout: float = 5.0) -> None:
        """Signal the worker to stop and wait for it."""
        self._running.clear()
        self._thread.join(timeout=timeout)

    def queue_size(self) -> int:
        """Return current queue depth (for monitoring)."""
        return self._queue.qsize()


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_logger_instance: AsyncObservabilityLogger | None = None
_logger_lock = threading.Lock()


def get_obs_logger(handlers: list[Callable] | None = None) -> AsyncObservabilityLogger:
    """Return the process-global AsyncObservabilityLogger singleton.

    On first call, creates the singleton with the provided handlers (or the
    default log handler when handlers is None).  Subsequent calls ignore the
    handlers argument and return the existing instance.
    """
    global _logger_instance  # noqa: PLW0603
    if _logger_instance is None:
        with _logger_lock:
            if _logger_instance is None:
                _logger_instance = AsyncObservabilityLogger(handlers=handlers)
    return _logger_instance


def reset_obs_logger() -> None:
    """Stop and discard the global singleton (for testing only)."""
    global _logger_instance  # noqa: PLW0603
    with _logger_lock:
        if _logger_instance is not None:
            _logger_instance.stop()
            _logger_instance = None
