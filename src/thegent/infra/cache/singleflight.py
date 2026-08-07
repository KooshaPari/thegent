"""TGNT-P9.1 — singleflight (request coalescing) primitives.

This module is the canonical home for :class:`Singleflight` and
:class:`CrossProcessSingleflight`. Both implement the Singleflight
pattern (https://pkg.go.dev/sync/singleflight) — coalescing concurrent
duplicate calls into a single execution.

It is part of the WL706 L1 Architecture hardening pass that splits the
legacy single-file ``infra/cache_v2.py`` (419 LOC) into focused
single-responsibility sub-modules. ``CrossProcessSingleflight.do`` was
refactored into a thin orchestrator over three helpers
(``_try_acquire_lock`` / ``_wait_for_result`` / ``_persist_result``) to
collapse the recursive stale-lock retry + sleep-loop into ≤35 LOC.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)


class Singleflight:
    """Implementation of Singleflight pattern to prevent duplicate requests."""

    def __init__(self) -> None:
        self.calls: dict[str, threading.Event] = {}
        self.results: dict[str, Any] = {}
        self.lock = threading.Lock()

    def do(self, key: str, func: Callable[[], Any]) -> Any:
        """Execute func for key, coalescing concurrent calls."""
        with self.lock:
            if key in self.calls:
                event = self.calls[key]
                self.lock.release()
                event.wait()
                self.lock.acquire()
                return self.results.get(key)

            event = threading.Event()
            self.calls[key] = event

        try:
            result = func()
            with self.lock:
                self.results[key] = result
            return result
        finally:
            with self.lock:
                event.set()
                del self.calls[key]


class CrossProcessSingleflight:
    """Implementation of Singleflight pattern across processes using file locks.

    The ``do`` method fans out across four branches (acquired / stale /
    wait / missing pid) with a recursive retry on stale-lock break and a
    120-second sleep-loop while waiting for the leader to write its
    result. The WL706 hardening pass collapsed each branch into a
    dedicated helper to drop the cognitive complexity and pin the
    behaviour with hardening tests.
    """

    LOCK_TTL_SECONDS = 120
    WAIT_TTL_SECONDS = 120
    POLL_INTERVAL_SECONDS = 1

    def __init__(self, coordination_dir: Path) -> None:
        self.coordination_dir = coordination_dir
        self.coordination_dir.mkdir(parents=True, exist_ok=True)

    def do(self, key: str, func: Callable[[], Any], ttl: int = 300) -> Any:
        """Execute func for key, coalescing concurrent calls across processes."""
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        lock_file = self.coordination_dir / f"{hashed_key}.lock"
        result_file = self.coordination_dir / f"{hashed_key}.result"

        # 1. Check if a recent result already exists
        if result_file.exists():
            try:
                data = json.loads(result_file.read_text())
                if time.time() - data.get("timestamp", 0) < ttl:
                    return data.get("result")
            except Exception:
                pass

        # 2. Try to acquire lock
        acquisition = self._try_acquire_lock(lock_file, key)
        if acquisition == "stale_broken":
            # Recursive retry after stale-lock break.
            return self.do(key, func, ttl)
        if acquisition == "wait":
            outcome, value = self._wait_for_result(result_file, lock_file, key)
            if outcome == "found":
                return value
            if outcome == "lock_disappeared":
                # Lock released but no result? Retry.
                return self.do(key, func, ttl)
            logger.error(f"Timeout waiting for singleflight result: {key}")
            return None

        # 3. We have the lock, execute func.
        try:
            result = func()
            self._persist_result(result_file, result)
            return result
        finally:
            if lock_file.exists():
                lock_file.unlink()

    def _try_acquire_lock(
        self, lock_file: Path, key: str
    ) -> Literal["acquired", "stale_broken", "wait", "missing_pid"]:
        """Try to acquire the cross-process lock.

        Returns:

        * ``"acquired"`` — caller owns the lock and must execute ``func``.
        * ``"stale_broken"`` — stale lock was broken; caller should retry.
        * ``"wait"`` — lock is held by someone else; caller should poll.
        * ``"missing_pid"`` — lock file is unparseable; caller should poll.
        """
        try:
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write(f"{os.getpid()}|{time.time()}")
            return "acquired"
        except FileExistsError:
            try:
                content = lock_file.read_text().split("|")
                lock_time = float(content[1])
                if time.time() - lock_time > self.LOCK_TTL_SECONDS:
                    logger.warning(f"Stale lock found for {key}, breaking.")
                    lock_file.unlink()
                    return "stale_broken"
            except (IndexError, ValueError, OSError):
                return "missing_pid"
            return "wait"

    def _wait_for_result(
        self, result_file: Path, lock_file: Path, key: str
    ) -> tuple[Literal["found", "timeout", "lock_disappeared"], Any]:
        """Wait for the lock-holder to publish a result.

        Returns a ``(outcome, value)`` tuple. ``outcome`` is one of:

        * ``"found"`` — ``value`` is the parsed result payload.
        * ``"lock_disappeared"`` — caller should retry the whole ``do``.
        * ``"timeout"`` — waited ``WAIT_TTL_SECONDS`` seconds without a
          result; caller should log and return ``None``.
        """
        del key  # reserved for future structured logging
        start_wait = time.time()
        while time.time() - start_wait < self.WAIT_TTL_SECONDS:
            if result_file.exists():
                try:
                    data = json.loads(result_file.read_text())
                    return ("found", data.get("result"))
                except Exception:
                    pass
            if not lock_file.exists():
                return ("lock_disappeared", None)
            time.sleep(self.POLL_INTERVAL_SECONDS)
        return ("timeout", None)

    def _persist_result(self, result_file: Path, result: Any) -> None:
        """Write the canonical ``{result, timestamp}`` JSON payload."""
        result_file.write_text(json.dumps({"result": result, "timestamp": time.time()}))


__all__ = ["Singleflight", "CrossProcessSingleflight"]
