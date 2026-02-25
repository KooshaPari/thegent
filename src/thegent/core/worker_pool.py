"""Persistent Python Worker Pool (MTSP-06).

Eliminates ~300ms Python startup latency by maintaining a pool of warm
worker processes. Each worker is a long-lived Python process that accepts
AgentTask payloads over stdin/stdout IPC and returns AgentResult payloads.

Workers are pre-imported with common thegent modules to amortise import cost.
On task completion, the worker returns to the pool (not killed/restarted).

Tasks are executed in-process via the agent registry (no subprocess per task).

# @trace FR-OPT-006
"""

from __future__ import annotations

import asyncio
from asyncio import subprocess
import dataclasses
import orjson as json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Domain types                                                                  #
# --------------------------------------------------------------------------- #


@dataclass
class AgentTask:
    """Task submitted to a worker process."""

    task_id: str
    prompt: str
    cwd: str
    mode: str = "write"
    timeout: int = 600
    env: dict[str, str] = field(default_factory=dict)
    agent_name: str = "default"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result returned from a worker process."""

    task_id: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    duration_ms: float = 0.0
    worker_pid: int = 0


# --------------------------------------------------------------------------- #
# In-process task runner (WL-076)                                              #
# --------------------------------------------------------------------------- #


def get_runner(agent_name: str) -> Any:
    """Resolve agent name to a runner instance via the registry.

    Lazy import to avoid circular imports at module level.
    """
    from thegent.agents.registry import get_runner as _registry_get_runner

    runner = _registry_get_runner(agent_name)
    if runner is None:
        raise ValueError(f"No runner found for agent: {agent_name!r}")
    return runner


def run_task_in_process(task: dict[str, Any]) -> dict[str, Any]:
    """Execute an agent task in-process via the agent registry.

    Replaces the old shim_run() approach. Errors propagate directly
    instead of being silently swallowed.

    # @trace FR-OPT-006
    # @trace WL-076
    """
    task_id = task.get("task_id", "")
    prompt = task.get("prompt", "")
    cwd_str = task.get("cwd", "")
    mode = task.get("mode", "write")
    timeout = int(task.get("timeout", 600))
    env_over = task.get("env", {})
    agent_name = task.get("agent_name", "default")

    cwd = Path(cwd_str) if cwd_str else None

    runner = get_runner(agent_name)

    t0 = time.monotonic()
    result = runner.run(
        prompt=prompt,
        cwd=cwd,
        mode=mode,
        timeout=timeout,
        env=env_over if env_over else None,
    )
    duration_ms = (time.monotonic() - t0) * 1000

    return {
        "task_id": task_id,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "timed_out": result.timed_out,
        "duration_ms": duration_ms,
        "worker_pid": os.getpid(),
    }


# --------------------------------------------------------------------------- #
# Worker subprocess entry-point (embedded script, executed via -c)            #
# --------------------------------------------------------------------------- #

_WORKER_BOOTSTRAP = r"""
import json, sys, os, time
from pathlib import Path

# Pre-warm: import the heaviest thegent modules so the first task is fast.
import thegent.agents.base      # noqa: F401
import thegent.agents.registry  # noqa: F401
import thegent.config           # noqa: F401

from thegent.core.worker_pool import _run_task_in_process

sys.stdout.write("READY\n")
sys.stdout.flush()

for raw_line in sys.stdin:
    raw_line = raw_line.strip()
    if not raw_line:
        continue
    try:
        task = json.loads(raw_line)
    except json.JSONDecodeError as exc:
        sys.stdout.write(json.dumps({"error": str(exc).decode()}) + "\n")
        sys.stdout.flush()
        continue
    result = _run_task_in_process(task)
    sys.stdout.write(json.dumps(result).decode() + "\n")
    sys.stdout.flush()
"""


# --------------------------------------------------------------------------- #
# Worker wrapper                                                               #
# --------------------------------------------------------------------------- #


class Worker:
    """A single warm Python subprocess ready to handle tasks."""

    def __init__(self, pid: int, proc: subprocess.Process) -> None:
        self.pid = pid
        self._proc = proc
        self._in_use = False
        self._created_at = time.monotonic()
        self._last_used_at = time.monotonic()

    @property
    def in_use(self) -> bool:
        return self._in_use

    @property
    def idle_seconds(self) -> float:
        return time.monotonic() - self._last_used_at

    def mark_busy(self) -> None:
        self._in_use = True

    def mark_idle(self) -> None:
        self._in_use = False
        self._last_used_at = time.monotonic()

    def is_alive(self) -> bool:
        return self._proc.returncode is None

    async def execute(self, task: AgentTask) -> AgentResult:
        """Send task JSON to the worker over stdin, await JSON result on stdout."""
        if self._proc.stdin is None or self._proc.stdout is None:
            raise RuntimeError(f"Worker {self.pid} has closed pipes")

        payload = json.dumps(dataclasses.asdict(task).decode()) + "\n"
        self._proc.stdin.write(payload.encode())
        await self._proc.stdin.drain()

        raw = await self._proc.stdout.readline()
        if not raw:
            raise RuntimeError(f"Worker {self.pid} closed stdout unexpectedly")
        data = json.loads(raw.decode().strip())
        if "error" in data:
            raise RuntimeError(f"Worker {self.pid} task error: {data['error']}")
        return AgentResult(
            task_id=data.get("task_id", task.task_id),
            exit_code=data.get("exit_code", 1),
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            timed_out=data.get("timed_out", False),
            duration_ms=data.get("duration_ms", 0.0),
            worker_pid=data.get("worker_pid", self.pid),
        )

    async def terminate(self) -> None:
        """Gracefully terminate the worker subprocess."""
        if self._proc.returncode is None:
            self._proc.terminate()


# --------------------------------------------------------------------------- #
# Pool                                                                         #
# --------------------------------------------------------------------------- #


class PersistentWorkerPool:
    """Pool of warm Python processes ready to handle agent runner invocations.

    Reduces per-invocation overhead from ~300ms to <10ms by reusing warm
    processes. Workers are spawned at pool initialisation; tasks are
    dispatched to the first available idle worker.

    # @trace FR-OPT-006
    """

    def __init__(self, pool_size: int = 4, idle_timeout: int = 300) -> None:
        self._pool_size = pool_size
        self._idle_timeout = idle_timeout
        self._workers: list[Worker] = []
        self._lock: asyncio.Lock | None = None
        self._started = False
        self._reaper_task: asyncio.Task[None] | None = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    # ---------------------------------------------------------------------- #
    # Lifecycle                                                                #
    # ---------------------------------------------------------------------- #

    async def start(self) -> None:
        """Spawn all workers and wait for their READY signal."""
        if self._started:
            return
        lock = self._get_lock()
        async with lock:
            if self._started:
                return
            spawn_tasks = [self._spawn_worker() for _ in range(self._pool_size)]
            workers = await asyncio.gather(*spawn_tasks)
            self._workers = list(workers)
            self._started = True
            self._reaper_task = asyncio.create_task(self._idle_reaper(), name="worker-pool-reaper")
            _log.info("MTSP-06: worker pool started with %d workers", self._pool_size)

    async def stop(self) -> None:
        """Terminate all workers and cancel the reaper."""
        if self._reaper_task is not None:
            self._reaper_task.cancel()
        for w in self._workers:
            await w.terminate()
        self._workers.clear()
        self._started = False
        _log.info("MTSP-06: worker pool stopped")

    # ---------------------------------------------------------------------- #
    # Public API                                                               #
    # ---------------------------------------------------------------------- #

    async def acquire(self) -> Worker:
        """Acquire an idle worker, blocking until one is available."""
        lock = self._get_lock()
        while True:
            async with lock:
                for w in self._workers:
                    if not w.in_use and w.is_alive():
                        w.mark_busy()
                        return w
                # All workers busy — spawn a temporary overflow worker
                overflow = await self._spawn_worker()
                overflow.mark_busy()
                self._workers.append(overflow)
                _log.debug("MTSP-06: spawned overflow worker pid=%d", overflow.pid)
                return overflow
            await asyncio.sleep(0.010)

    async def release(self, worker: Worker) -> None:
        """Return a worker to the idle pool."""
        worker.mark_idle()
        _log.debug("MTSP-06: worker pid=%d returned to pool", worker.pid)

    async def submit(self, task: AgentTask) -> AgentResult:
        """Acquire a worker, execute the task, release the worker, return result."""
        worker = await self.acquire()
        try:
            result = await worker.execute(task)
        finally:
            await self.release(worker)
        return result

    # ---------------------------------------------------------------------- #
    # Internal helpers                                                         #
    # ---------------------------------------------------------------------- #

    async def _spawn_worker(self) -> Worker:
        """Start a worker subprocess and wait for its READY handshake."""
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-c",
            _WORKER_BOOTSTRAP,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        try:
            ready_line = await asyncio.wait_for(
                proc.stdout.readline(),  # type: ignore[union-attr]
                timeout=10.0,
            )
        except TimeoutError as exc:
            proc.terminate()
            raise RuntimeError("Worker failed to send READY within 10 s") from exc
        if ready_line.strip() != b"READY":
            proc.terminate()
            raise RuntimeError(f"Unexpected worker startup message: {ready_line!r}")
        worker = Worker(pid=proc.pid, proc=proc)  # type: ignore[arg-type]
        _log.debug("MTSP-06: worker spawned pid=%d", proc.pid)
        return worker

    async def _idle_reaper(self) -> None:
        """Periodically evict workers that have been idle longer than idle_timeout."""
        while True:
            await asyncio.sleep(30)
            lock = self._get_lock()
            async with lock:
                alive: list[Worker] = []
                for w in self._workers:
                    if not w.in_use and w.idle_seconds > self._idle_timeout and len(alive) >= self._pool_size:
                        await w.terminate()
                        _log.debug(
                            "MTSP-06: evicted idle worker pid=%d (idle %.0fs)",
                            w.pid,
                            w.idle_seconds,
                        )
                    else:
                        alive.append(w)
                self._workers = alive


# --------------------------------------------------------------------------- #
# Module-level singleton                                                       #
# --------------------------------------------------------------------------- #

_pool: PersistentWorkerPool | None = None


def get_worker_pool(pool_size: int = 4, idle_timeout: int = 300) -> PersistentWorkerPool:
    """Return the module-level singleton pool (not yet started)."""
    global _pool
    if _pool is None:
        _pool = PersistentWorkerPool(pool_size=pool_size, idle_timeout=idle_timeout)
    return _pool
