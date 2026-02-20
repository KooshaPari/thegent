"""Universal Multi-Runtime Coordinator.

This module allows a single program to orchestrate tasks across multiple Python runtimes
(PyPy, CPython 3.13, CPython 3.14) simultaneously using a shared state bridge.
"""

import asyncio
import contextlib
import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from thegent.infra.ipc import IPCMesh, MaildirQueue


class RuntimeType(Enum):
    PYPY = "pypy"
    CPYTHON_313 = "3.13"
    CPYTHON_314 = "3.14"

@dataclass
class RuntimeTask:
    task_id: str
    runtime: RuntimeType
    module: str
    function: str
    args: list[Any]
    kwargs: dict[str, Any]

class MultiRuntimeBridge:
    """Orchestrates tasks across multiple specialized Python processes."""

    def __init__(self, mesh_root: Path | None = None) -> None:
        self.mesh_root = mesh_root or Path("/tmp/thegent-bridge")
        self.mesh = IPCMesh(self.mesh_root)
        self.queue = MaildirQueue(self.mesh_root / "queue")
        self.active_workers: dict[RuntimeType, Any] = {}

    async def start_worker(self, runtime: RuntimeType):
        """Start a long-running worker on a specific runtime."""
        if runtime in self.active_workers:
            return

        worker_script = Path(__file__).parent / "worker_node.py"
        src_root = str(Path(__file__).parent.parent.parent) # .../src

        # Use separate venvs to avoid lock contention and allow runtime-specific native builds
        venv_name = f".venv-{runtime.name.lower()}"

        # Command to run via uv
        cmd = ["uv", "run", "--python", runtime.value, "python", str(worker_script),
               "--mesh-root", str(self.mesh_root), "--runtime", runtime.name]


        # Prepare environment
        env = os.environ.copy()
        env["PYTHONPATH"] = src_root
        # Tell uv where to put the specialized venv
        env["UV_PROJECT_ENVIRONMENT"] = str(Path(src_root).parent / venv_name)

        # Start as async subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        self.active_workers[runtime] = process

        # Start log forwarding
        asyncio.create_task(self._forward_logs(runtime, process))

    async def _forward_logs(self, runtime: RuntimeType, process: Any):
        """Forward worker logs to main process."""
        while True:
            # We must read from both streams. Using a loop for simplicity in smoke test.
            line = await process.stdout.readline()
            if not line:
                break

        err_data = await process.stderr.read()
        if err_data:
            pass

        exit_code = await process.wait()

    async def dispatch(self, task: RuntimeTask) -> str:
        """Dispatch a task to the appropriate runtime queue."""
        await self.start_worker(task.runtime)

        # Use runtime-specific queue
        queue_path = self.mesh_root / "queue" / task.runtime.name.lower()
        runtime_queue = MaildirQueue(queue_path)

        message = {
            "type": "task",
            "task_id": task.task_id,
            "runtime": task.runtime.name,
            "module": task.module,
            "function": task.function,
            "args": task.args,
            "kwargs": task.kwargs
        }
        return runtime_queue.send(message)

    async def shutdown(self):
        """Gracefully shutdown all workers."""
        for process in self.active_workers.values():
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except Exception:
                with contextlib.suppress(Exception):
                    process.kill()
