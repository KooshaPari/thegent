"""Remote compute runner with SSH execution, rsync file sync, and process management.

This module provides:
- RemoteRunner: High-level interface for remote task execution
- SSH-based remote execution via existing RemoteExecutor
- File synchronization with rsync
- Remote process management (start, stop, status)
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from thegent.compute.remote_executor import RemoteExecutor, RemoteExecutorError, RemoteResult, RemoteTask

_log = logging.getLogger(__name__)


class RemoteRunnerError(Exception):
    """Raised when a remote runner operation fails."""


@dataclass
class RemoteProcess:
    """Represents a running process on a remote node.

    Attributes:
        pid: Process ID on the remote node.
        command: The command that was executed.
        node: The remote node where the process is running.
        start_time: When the process was started (monotonic timestamp).
        status: Current status of the process (running, completed, failed).
        exit_code: Exit code if the process has completed.
    """

    pid: int
    command: str
    node: str
    start_time: float
    status: str = "running"
    exit_code: int | None = None


class RemoteRunner:
    """High-level remote compute runner with SSH execution, rsync sync, and process management.

    This class provides a simplified interface for running tasks on remote nodes,
    optionally syncing the workspace before execution.

    Environment variable configuration:
    * ``THGENT_REMOTE_NODES`` — comma-separated list of hostnames/IPs.
    * ``THGENT_REMOTE_SSH_USER`` — SSH login user (optional).

    Args:
        node: Explicit target hostname/IP. When *None*, uses round-robin selection.
        sync_workspace: Whether to sync the workspace directory before execution.
        ssh_user: Optional SSH username override.
    """

    _SSH_OPTS: ClassVar[list[str]] = ["-o", "StrictHostKeyChecking=no"]
    _RSYNC_OPTS: ClassVar[list[str]] = ["-az", "--delete"]

    def __init__(
        self,
        node: str | None = None,
        sync_workspace: bool = False,
        ssh_user: str | None = None,
    ) -> None:
        self._node = node
        self._sync_workspace = sync_workspace
        self._ssh_user = ssh_user
        self._executor = RemoteExecutor(nodes=[node] if node else None, ssh_user=ssh_user)
        self._active_processes: dict[str, RemoteProcess] = {}

    @property
    def node(self) -> str | None:
        """Return the configured node, or None for round-robin."""
        return self._node

    @property
    def sync_workspace(self) -> bool:
        """Return whether workspace sync is enabled."""
        return self._sync_workspace

    # -------------------------------------------------------------------------
    # Workspace synchronization
    # -------------------------------------------------------------------------

    def sync_to_remote(
        self,
        local_path: str | Path,
        remote_path: str | Path,
        exclude: list[str] | None = None,
    ) -> bool:
        """Sync local directory to remote using rsync.

        Args:
            local_path: Local directory path to sync.
            remote_path: Remote destination path.
            exclude: Optional list of patterns to exclude (rsync --exclude).

        Returns:
            True if sync succeeded, False otherwise.
        """
        local_path = Path(local_path).resolve()
        if not local_path.exists():
            _log.warning("Local path does not exist: %s", local_path)
            return False

        # Get target node
        target = self._resolve_node()

        # Build rsync command
        cmd = ["rsync", *self._RSYNC_OPTS]

        # Add excludes
        if exclude:
            for pattern in exclude:
                cmd.extend(["--exclude", pattern])

        # Add standard excludes for common unneeded files
        cmd.extend(["--exclude", "__pycache__"])
        cmd.extend(["--exclude", "*.pyc"])
        cmd.extend(["--exclude", ".git"])
        cmd.extend(["--exclude", "node_modules"])

        # Build destination
        ssh_user = self._ssh_user or ""
        dest = f"{ssh_user + '@' if ssh_user else ''}{target}:{remote_path}"

        cmd.append(str(local_path))
        cmd.append(dest)

        _log.info("Syncing %s to %s", local_path, dest)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300.0,
                check=False,
            )
            if result.returncode != 0:
                _log.error("rsync failed: %s", result.stderr)
                return False
            _log.info("Sync completed successfully")
            return True
        except subprocess.TimeoutExpired:
            _log.error("rsync timed out")
            return False
        except OSError as exc:
            _log.error("rsync failed to spawn: %s", exc)
            return False

    def sync_from_remote(
        self,
        remote_path: str | Path,
        local_path: str | Path,
        exclude: list[str] | None = None,
    ) -> bool:
        """Sync remote directory to local using rsync.

        Args:
            remote_path: Remote source path.
            local_path: Local destination directory.
            exclude: Optional list of patterns to exclude.

        Returns:
            True if sync succeeded, False otherwise.
        """
        remote_path = str(remote_path)
        local_path = Path(local_path).resolve()

        # Get target node
        target = self._resolve_node()

        # Build rsync command (reverse direction)
        cmd = ["rsync", *self._RSYNC_OPTS]

        if exclude:
            for pattern in exclude:
                cmd.extend(["--exclude", pattern])

        # Build source
        ssh_user = self._ssh_user or ""
        source = f"{ssh_user + '@' if ssh_user else ''}{target}:{remote_path}"

        cmd.append(source)
        cmd.append(str(local_path))

        _log.info("Syncing from %s to %s", source, local_path)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300.0,
                check=False,
            )
            if result.returncode != 0:
                _log.error("rsync failed: %s", result.stderr)
                return False
            return True
        except (subprocess.TimeoutExpired, OSError) as exc:
            _log.error("rsync failed: %s", exc)
            return False

    # -------------------------------------------------------------------------
    # Remote execution
    # -------------------------------------------------------------------------

    def run_agent_task(
        self,
        prompt: str,
        agent: str | None = None,
        timeout_s: float = 300.0,
        cd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> RemoteResult:
        """Run an agent task on the remote node.

        This method:
        1. Optionally syncs the workspace to the remote node
        2. Executes the agent command via SSH
        3. Optionally syncs results back (if workspace was synced)

        Args:
            prompt: The prompt for the agent.
            agent: Optional agent name to use.
            timeout_s: Execution timeout in seconds.
            cd: Optional working directory for the task.
            env: Optional environment variables.

        Returns:
            RemoteResult with the execution outcome.
        """
        target = self._resolve_node()

        # Build the command to run
        cmd_parts: list[str] = []

        if cd:
            cmd_parts.append(f"cd {cd} && ")

        # Build theagent command
        thegent_cmd = "thegent run agent"
        if agent:
            thegent_cmd += f" --agent {agent}"
        thegent_cmd += f' "{prompt}"'

        cmd_parts.append(thegent_cmd)
        command = "".join(cmd_parts)

        # Build task environment
        task_env = dict(env or {})
        task_env.setdefault("THGENT_REMOTE_EXEC", "1")

        # Create remote task
        task = RemoteTask(
            task_id=f"runner-{int(time.time())}",
            command=command,
            env=task_env,
            timeout_s=timeout_s,
            node=target,
        )

        _log.info("Executing remote task on %s: %s", target, command[:100])

        # Execute
        try:
            result = self._executor.execute(task)
            _log.info(
                "Task completed on %s in %.2fs (exit=%d)",
                result.node,
                result.elapsed_s,
                result.exit_code,
            )
            return result
        except RemoteExecutorError as exc:
            raise RemoteRunnerError(f"Remote execution failed: {exc}") from exc

    async def run_agent_task_async(
        self,
        prompt: str,
        agent: str | None = None,
        timeout_s: float = 300.0,
        cd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> RemoteResult:
        """Asynchronously run an agent task on the remote node.

        Args:
            prompt: The prompt for the agent.
            agent: Optional agent name to use.
            timeout_s: Execution timeout in seconds.
            cd: Optional working directory for the task.
            env: Optional environment variables.

        Returns:
            RemoteResult with the execution outcome.
        """
        target = self._resolve_node()

        # Build the command
        cmd_parts = []
        if cd:
            cmd_parts.append(f"cd {cd} && ")

        thegent_cmd = "thegent run agent"
        if agent:
            thegent_cmd += f" --agent {agent}"
        thegent_cmd += f' "{prompt}"'

        cmd_parts.append(thegent_cmd)
        command = "".join(cmd_parts)

        task_env = dict(env or {})
        task_env.setdefault("THGENT_REMOTE_EXEC", "1")

        task = RemoteTask(
            task_id=f"runner-async-{int(time.time())}",
            command=command,
            env=task_env,
            timeout_s=timeout_s,
            node=target,
        )

        _log.info("Executing async remote task on %s: %s", target, command[:100])

        try:
            result = await self._executor.execute_async(task)
            return result
        except RemoteExecutorError as exc:
            raise RemoteRunnerError(f"Async remote execution failed: {exc}") from exc

    def execute(
        self,
        command: str,
        timeout_s: float = 300.0,
        env: dict[str, str] | None = None,
    ) -> RemoteResult:
        """Execute a raw command on the remote node.

        Args:
            command: Shell command to execute.
            timeout_s: Execution timeout in seconds.
            env: Optional environment variables.

        Returns:
            RemoteResult with the execution outcome.
        """
        target = self._resolve_node()

        task = RemoteTask(
            task_id=f"exec-{int(time.time())}",
            command=command,
            env=env or {},
            timeout_s=timeout_s,
            node=target,
        )

        _log.info("Executing on %s: %s", target, command[:100])

        try:
            return self._executor.execute(task)
        except RemoteExecutorError as exc:
            raise RemoteRunnerError(f"Remote execution failed: {exc}") from exc

    async def execute_async(
        self,
        command: str,
        timeout_s: float = 300.0,
        env: dict[str, str] | None = None,
    ) -> RemoteResult:
        """Asynchronously execute a raw command on the remote node.

        Args:
            command: Shell command to execute.
            timeout_s: Execution timeout in seconds.
            env: Optional environment variables.

        Returns:
            RemoteResult with the execution outcome.
        """
        target = self._resolve_node()

        task = RemoteTask(
            task_id=f"exec-async-{int(time.time())}",
            command=command,
            env=env or {},
            timeout_s=timeout_s,
            node=target,
        )

        try:
            return await self._executor.execute_async(task)
        except RemoteExecutorError as exc:
            raise RemoteRunnerError(f"Async remote execution failed: {exc}") from exc

    # -------------------------------------------------------------------------
    # Remote process management
    # -------------------------------------------------------------------------

    def start_process(
        self,
        command: str,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
    ) -> RemoteProcess:
        """Start a long-running process on the remote node (non-blocking).

        Uses nohup to ensure the process persists after SSH disconnects.

        Args:
            command: Command to execute.
            env: Optional environment variables.
            cwd: Optional working directory.

        Returns:
            RemoteProcess with PID and details.
        """
        target = self._resolve_node()

        # Build the command with nohup
        parts = ["nohup"]
        if cwd:
            parts.append(f"cd {cwd} &&")
        parts.append(command)
        parts.append("> /dev/null 2>&1 &")
        parts.append("echo $!")

        full_cmd = " ".join(parts)

        # Execute and get PID
        task = RemoteTask(
            task_id=f"start-proc-{int(time.time())}",
            command=full_cmd,
            env=env or {},
            timeout_s=30.0,
            node=target,
        )

        result = self._executor.execute(task)

        try:
            pid = int(result.stdout.strip())
        except ValueError:
            raise RemoteRunnerError(f"Failed to parse PID from: {result.stdout}")

        process = RemoteProcess(
            pid=pid,
            command=command,
            node=target,
            start_time=time.monotonic(),
        )

        self._active_processes[str(pid)] = process
        _log.info("Started process %d on %s", pid, target)

        return process

    def stop_process(self, pid: int) -> bool:
        """Stop a running process on the remote node.

        Args:
            pid: Process ID to stop.

        Returns:
            True if the process was stopped successfully.
        """
        if str(pid) not in self._active_processes:
            _log.warning("Process %d not tracked, attempting direct kill", pid)
            # Try to kill anyway
            target = self._resolve_node()
            task = RemoteTask(
                task_id=f"kill-{pid}",
                command=f"kill {pid} 2>/dev/null || true",
                timeout_s=10.0,
                node=target,
            )
            self._executor.execute(task)
            return True

        process = self._active_processes[str(pid)]
        target = process.node

        task = RemoteTask(
            task_id=f"kill-{pid}",
            command=f"kill {pid} 2>/dev/null || true",
            timeout_s=10.0,
            node=target,
        )

        try:
            self._executor.execute(task)
            del self._active_processes[str(pid)]
            _log.info("Stopped process %d on %s", pid, target)
            return True
        except RemoteExecutorError:
            return False

    def get_process_status(self, pid: int) -> RemoteProcess | None:
        """Get the status of a remote process.

        Args:
            pid: Process ID to check.

        Returns:
            RemoteProcess if found and running, None otherwise.
        """
        if str(pid) not in self._active_processes:
            return None

        process = self._active_processes[str(pid)]

        # Check if process is still running
        task = RemoteTask(
            task_id=f"status-{pid}",
            command=f"ps -p {pid} -o pid= 2>/dev/null",
            timeout_s=10.0,
            node=process.node,
        )

        result = self._executor.execute(task)

        if result.exit_code != 0 or not result.stdout.strip():
            # Process is not running
            process.status = "completed"
            return process

        return process

    def list_processes(self) -> list[RemoteProcess]:
        """List all tracked processes.

        Returns:
            List of RemoteProcess objects.
        """
        return list(self._active_processes.values())

    # -------------------------------------------------------------------------
    # Internals
    # -------------------------------------------------------------------------

    def _resolve_node(self) -> str:
        """Resolve the target node for execution.

        Returns:
            The hostname or IP of the target node.

        Raises:
            RemoteRunnerError: If no nodes are configured.
        """
        if self._node:
            return self._node

        # Get available nodes from executor
        available = self._executor.available_nodes()
        if not available:
            raise RemoteRunnerError(
                "No remote nodes configured. Set THGENT_REMOTE_NODES or pass node= to RemoteRunner."
            )

        # Use round-robin (first available)
        return available[0]


def load_config_from_env() -> dict[str, str]:
    """Load configuration from environment variables.

    Returns:
        Dictionary with remote runner configuration.
    """
    return {
        "nodes": os.environ.get("THGENT_REMOTE_NODES", ""),
        "ssh_user": os.environ.get("THGENT_REMOTE_SSH_USER", ""),
    }
