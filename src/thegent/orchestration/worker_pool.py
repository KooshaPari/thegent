"""Shared task worker pool (MTSP-03).

Consolidates task execution into a persistent daemon managed by
process-compose to reduce overhead of repeatedly spawning task processes.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


@dataclass
class TaskRequest:
    """A request to execute a task."""

    id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    command: list[str] = field(default_factory=list)
    cwd: str | None = None
    env: dict[str, str] = field(default_factory=dict)
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class TaskResult:
    """The result of a task execution."""

    task_id: str
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    ended_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class TaskWorkerPool:
    """Persistent task worker pool (MTSP-03)."""

    def __init__(
        self,
        max_workers: int = 4,
        queue_dir: Path | None = None,
    ) -> None:
        settings = ThegentSettings()
        self.max_workers = max_workers
        self.queue_dir = queue_dir or settings.cache_dir / "task_queue"
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.inbox = self.queue_dir / "inbox"
        self.results = self.queue_dir / "results"
        self.inbox.mkdir(exist_ok=True)
        self.results.mkdir(exist_ok=True)
        self._running = False

    async def start(self) -> None:
        """Start the worker pool daemon."""
        self._running = True
        _log.info("MTSP-03: Task worker pool started with %d workers", self.max_workers)

        workers = [self._worker_loop(i) for i in range(self.max_workers)]
        await asyncio.gather(*workers)

    def stop(self) -> None:
        """Stop the worker pool daemon."""
        self._running = False

    async def _worker_loop(self, worker_id: int) -> None:
        """Individual worker loop."""
        _log.info("Worker %d starting", worker_id)
        while self._running:
            # Poll for new tasks in the inbox
            task_files = sorted(self.inbox.glob("*.json"), key=lambda p: p.stat().st_mtime)
            if not task_files:
                await asyncio.sleep(0.5)
                continue

            task_file = task_files[0]
            # Try to claim the task by renaming it
            claim_file = self.queue_dir / f"claiming_{task_file.name}"
            try:
                task_file.rename(claim_file)
            except OSError:
                # Someone else claimed it
                continue

            # Read and execute task
            try:
                task_data = json.loads(claim_file.read_text())
                task = TaskRequest(**task_data)
                _log.info("Worker %d executing task %s: %s", worker_id, task.id, " ".join(task.command))

                start_time = time.time()
                proc = await asyncio.create_subprocess_exec(
                    *task.command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=task.cwd,
                    env={**os.environ, **task.env},
                )
                stdout, stderr = await proc.communicate()
                duration = time.time() - start_time

                result = TaskResult(
                    task_id=task.id,
                    exit_code=proc.returncode or 0,
                    stdout=stdout.decode(errors="replace"),
                    stderr=stderr.decode(errors="replace"),
                    duration_s=duration,
                )

                # Write result
                result_file = self.results / f"{task.id}.json"
                result_file.write_text(json.dumps(result.__dict__))
                _log.info("Worker %d completed task %s with exit code %d", worker_id, task.id, result.exit_code)

            except Exception as e:
                _log.error("Worker %d failed to execute task: %s", worker_id, e)
            finally:
                if claim_file.exists():
                    claim_file.unlink()

    def submit_task(self, task: TaskRequest) -> Path:
        """Submit a task to the queue (client-side)."""
        task_file = self.inbox / f"{task.id}.json"
        task_file.write_text(json.dumps(task.__dict__))
        return task_file

    def get_result(self, task_id: str, timeout: int = 60) -> TaskResult | None:
        """Wait for and retrieve a task result (client-side)."""
        result_file = self.results / f"{task_id}.json"
        start_time = time.time()
        while time.time() - start_time < timeout:
            if result_file.exists():
                try:
                    data = json.loads(result_file.read_text())
                    result_file.unlink()
                    return TaskResult(**data)
                except (OSError, json.JSONDecodeError):
                    pass
            time.sleep(0.5)
        return None
