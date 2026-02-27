"""MTSP-06: Persistent Python Worker Pool.

Reduces interpreter startup latency by keeping warm processes alive.
"""

import asyncio
import logging
import multiprocessing
import signal
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from typing import Any, TypeVar

T = TypeVar("T")

_log = logging.getLogger(__name__)


class PersistentWorkerPool:
    """A pool of persistent Python processes for executing tasks (MTSP-06)."""

    _instance: "PersistentWorkerPool | None" = None

    def __init__(self, size: int | None = None) -> None:
        self.size = size or max(1, multiprocessing.cpu_count() - 1)
        self.executor: ProcessPoolExecutor | None = None
        self._loop = asyncio.get_event_loop()

    @classmethod
    def get_instance(cls, size: int | None = None) -> "PersistentWorkerPool":
        if cls._instance is None:
            cls._instance = cls(size)
        return cls._instance

    def start(self) -> None:
        """Initialize the process pool."""
        if self.executor:
            return

        _log.info(f"MTSP-06: Starting persistent worker pool with {self.size} workers")
        # Use 'spawn' for safety, especially with complex imports and state
        ctx = multiprocessing.get_context("spawn")
        self.executor = ProcessPoolExecutor(
            max_workers=self.size,
            mp_context=ctx,
            initializer=self._worker_initializer,
        )

    def stop(self) -> None:
        """Shut down the pool."""
        if self.executor:
            _log.info("MTSP-06: Stopping persistent worker pool")
            self.executor.shutdown(wait=True)
            self.executor = None

    @staticmethod
    def _worker_initializer() -> None:
        """Prepare worker process (MTSP-06)."""
        # Ignore SIGINT in workers; the parent will handle it
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        # Pre-import heavy modules to warm up the cache
        try:
            import httpx
            import pydantic

            # Use them to avoid unused import warnings
            _ = (httpx.__name__, pydantic.__name__)
        except ImportError:
            pass

    async def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute a function in the pool and return the result."""
        if not self.executor:
            self.start()

        if not self.executor:
            raise RuntimeError("Failed to start worker pool")

        return await self._loop.run_in_executor(
            self.executor,
            func,
            *args,
            **kwargs,
        )


def get_worker_pool() -> PersistentWorkerPool:
    """Helper for dependency injection."""
    return PersistentWorkerPool.get_instance()
