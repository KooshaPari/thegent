"""CLI-Share Command Debouncing and Stream Attachment.

Ensures heavy commands are shared across multiple agent tenants (L2)
under the same L1 project context.
"""

import hashlib
import logging
import os
import signal
import subprocess
import time
from pathlib import Path

from thegent.orchestration.state.shm import SHMSystem

logger = logging.getLogger(__name__)


class CommandSharer:
    """
    Manages command debouncing using SHM locks.
    If a command is already running, subsequent agents attach to its output.
    """

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.shm = SHMSystem(session_dir)
        self.cache_dir = session_dir / "cmd_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def execute_shared(self, command: list[str], cwd: Path, env: dict | None = None) -> dict:
        """
        Execute a command or attach to an existing one if already running.
        """
        # 1. Generate unique hash for command + cwd + lockfile (if exists)
        cmd_str = " ".join(command)
        lock_content = ""
        for lockfile in ["package-lock.json", "Cargo.lock", "uv.lock", "poetry.lock"]:
            lp = cwd / lockfile
            if lp.exists():
                lock_content = lp.read_text()[:1000]  # Take prefix for hash
                break

        hash_input = f"{cmd_str}:{cwd}:{lock_content}"
        cmd_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

        output_path = self.cache_dir / f"{cmd_hash}.out"

        if not self.shm.is_native_active():
            # Fallback to standard execution if SHM is disabled
            return self._run_fresh(command, cwd, env, output_path)

        # 2. Try to acquire SHM lock
        import thegent_shm  # type: ignore[import-not-found]  # optional native extension

        conflict = thegent_shm.try_acquire_cmd_lock(cmd_hash=cmd_hash, pid=os.getpid(), output_path=str(output_path))

        if conflict:
            # 3. Command is already running! Attach to it.
            logger.info(f"Command '{cmd_str}' already running (PID {conflict['pid']}). Attaching...")
            return self._attach_to_existing(conflict, output_path)

        # 4. We own the lock. Run fresh.
        try:
            result = self._run_fresh(command, cwd, env, output_path)
            status = "completed" if result["returncode"] == 0 else "failed"
            thegent_shm.release_cmd_lock(cmd_hash, status)
            return result
        except Exception as e:
            thegent_shm.release_cmd_lock(cmd_hash, "failed")
            raise

    def _run_fresh(self, command: list[str], cwd: Path, env: dict | None, output_path: Path) -> dict:
        """Run the command and stream output to a cache file."""
        with open(output_path, "w") as f:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env or os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                f.write(line)
                f.flush()
                output_lines.append(line)

            process.wait()

            return {"returncode": process.returncode, "stdout": "".join(output_lines), "stderr": "", "cached": False}

    def _attach_to_existing(self, conflict: dict, output_path: Path) -> dict:
        """Wait for the existing command to finish and return its output."""
        # Optional: In a more advanced version, we'd tail the output_path live.
        # For now, we wait for the PID to exit or the lock to change status.
        pid = conflict["pid"]

        while True:
            # Check if PID is still alive
            try:
                os.kill(pid, 0)
            except OSError:
                # PID is gone!
                break

            time.sleep(0.5)

        # Once finished, read the cached output
        if output_path.exists():
            return {
                "returncode": 0,  # Assume success if we couldn't get real code
                "stdout": output_path.read_text(),
                "stderr": "",
                "cached": True,
            }

        return {"returncode": 1, "stdout": "Attached command failed to produce output.", "stderr": ""}
