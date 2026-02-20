"""Worker Node for Multi-Runtime Bridge.

Runs on specialized runtimes (PyPy, CPython 3.14) and executes dispatched tasks.
"""

import argparse
import asyncio
import importlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Ensure we can import thegent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from thegent.infra.ipc import MaildirQueue

try:
    from thegent_shm import init_shm, record_resource_usage
    HAS_SHM = True
except ImportError:
    HAS_SHM = False

async def worker_loop(mesh_root: Path, runtime_name: str):
    queue_path = mesh_root / "queue" / runtime_name.lower()

    queue = MaildirQueue(queue_path)

    # Initialize SHM if available
    if HAS_SHM:
        init_shm(str(mesh_root / "state.shm"))

    while True:
        # Check for new messages
        result = queue.receive()
        if result:
            _msg_id, message = result
            if message.get("type") == "task":
                task_id = message["task_id"]
                module_name = message["module"]
                func_name = message["function"]
                args = message.get("args", [])
                kwargs = message.get("kwargs", {})


                try:
                    # Dynamic Import and Execution
                    module = importlib.import_module(module_name)
                    func = getattr(module, func_name)

                    start_time = time.perf_counter()
                    output = func(*args, **kwargs)
                    duration = time.perf_counter() - start_time

                    # Store result back in mesh (e.g., results/task_id.json)
                    result_path = mesh_root / "results" / f"{task_id}.json"
                    result_path.parent.mkdir(parents=True, exist_ok=True)
                    result_path.write_text(json.dumps({
                        "status": "success",
                        "output": output,
                        "duration": duration,
                        "runtime": runtime_name,
                        "implementation": sys.implementation.name,
                        "version": sys.version
                    }))

                except Exception as e:
                    result_path = mesh_root / "results" / f"{task_id}.json"
                    result_path.write_text(json.dumps({
                        "status": "error",
                        "error": str(e),
                        "runtime": runtime_name
                    }))

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh-root", type=str, required=True)
    parser.add_argument("--runtime", type=str, required=True)
    args = parser.parse_args()

    asyncio.run(worker_loop(Path(args.mesh_root), args.runtime))
