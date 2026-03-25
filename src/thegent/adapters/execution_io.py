"""I/O and subprocess management for task execution.

Handles:
- Shadow workspace creation/cleanup
- Resource locking
- Subprocess spawning with keepalive
- File I/O for session artifacts
- Process environment setup
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Any

import structlog

_log = structlog.get_logger(__name__)


class ShadowWorkspaceManager:
    """Manages shadow workspace lifecycle."""

    @staticmethod
    def create_if_enabled(
        original_cwd: Path,
        run_id: str,
        enabled: bool = False,
    ) -> tuple[Any | None, Path, dict[str, str] | None]:
        """Create shadow workspace if enabled.

        Returns (shadow_ws, agent_cwd, shadow_env).
        - If not enabled or creation fails: (None, original_cwd, None)
        """
        if not enabled:
            return None, original_cwd, None

        try:
            from thegent.orchestration.shadow import ShadowWorkspace

            shadow_ws = ShadowWorkspace(original_cwd, run_id)
            if shadow_ws.create():
                _log.info("Running in shadow workspace: %s", shadow_ws.shadow_root)
                return shadow_ws, shadow_ws.shadow_root, shadow_ws.get_env()
            else:
                _log.warning("Failed to create shadow workspace; falling back to main project.")
                return None, original_cwd, None
        except Exception as e:
            _log.warning("Shadow workspace creation failed: %s", e)
            return None, original_cwd, None

    @staticmethod
    def cleanup(shadow_ws: Any | None) -> None:
        """Clean up shadow workspace if it was created."""
        if shadow_ws is not None:
            try:
                shadow_ws.destroy()
            except Exception as e:
                _log.warning("Shadow workspace cleanup failed: %s", e)

    @staticmethod
    def merge_back(shadow_ws: Any | None, auto_merge: bool = False) -> bool:
        """Merge shadow workspace changes back to main project."""
        if shadow_ws is None or not auto_merge:
            return False
        try:
            return shadow_ws.merge_back()
        except Exception as e:
            _log.error("Failed to merge shadow changes: %s", e)
            return False


class ResourceLockManager:
    """Manages resource file leases for concurrency control."""

    @staticmethod
    def acquire_locks(
        lock_paths: list[str],
        run_id: str,
        timeout: int,
        session_dir: Path,
        base_cwd: Path,
    ) -> list[tuple[Path, str]]:
        """Acquire leases for locked resources.

        Returns list of (path, token) tuples for locked resources.
        Raises RuntimeError if any lock fails.
        """
        from thegent.coordination.file_coordination import FileLeaseRegistry

        locked_tokens = []
        lease_registry = FileLeaseRegistry(session_dir / "leases")

        for resource in lock_paths:
            path = Path(resource)
            if not path.is_absolute():
                path = base_cwd / path

            token = lease_registry.claim_lease(path, run_id, ttl=timeout)
            if token:
                locked_tokens.append((path, token))
                _log.info("Acquired lease for %s", resource)
            else:
                _log.error(
                    "Failed to acquire lease for %s; already locked by another agent.",
                    resource,
                )
                raise RuntimeError(
                    f"Resource {resource} is locked by another agent."
                )

        return locked_tokens

    @staticmethod
    def release_locks(
        locked_tokens: list[tuple[Path, str]],
        run_id: str,
        session_dir: Path,
    ) -> None:
        """Release all acquired resource leases."""
        from thegent.coordination.file_coordination import FileLeaseRegistry

        if not locked_tokens:
            return

        lease_registry = FileLeaseRegistry(session_dir / "leases")
        for path, token in locked_tokens:
            try:
                lease_registry.release_lease(path, run_id, token)
                _log.info("Released lease for %s", path)
            except Exception as e:
                _log.warning("Failed to release lease for %s: %s", path, e)


class ProcessEnvironmentBuilder:
    """Builds environment for subprocess execution."""

    @staticmethod
    def build_env(
        session_id: str,
        session_paths: dict[str, Path],
        owner_tag: str,
        shadow_env: dict[str, str] | None = None,
        filter_env: bool = False,
        allowlist: list[str] | None = None,
    ) -> dict[str, str]:
        """Build subprocess environment dict."""
        if filter_env and allowlist:
            env = {k: v for k, v in os.environ.items() if k in allowlist or k.startswith("THGENT_")}
        else:
            env = os.environ.copy()

        # Apply shadow environment overrides if present
        if shadow_env:
            env.update(shadow_env)

        env["PYTHONUNBUFFERED"] = "1"
        env.update(
            {
                "THGENT_SESSION_ID": session_id,
                "THGENT_SESSION_META_PATH": str(session_paths.get("meta", "")),
                "THGENT_SESSION_RC_PATH": str(session_paths.get("rc", "")),
                "THGENT_SESSION_STDOUT_PATH": str(session_paths.get("stdout", "")),
                "THGENT_SESSION_STDERR_PATH": str(session_paths.get("stderr", "")),
                "THGENT_OWNER_TAG": owner_tag,
            }
        )
        return env

    @staticmethod
    def apply_sandbox_wrapper(
        cmd: list[str],
        settings: Any,
        project_root: Path,
    ) -> list[str]:
        """Apply macOS sandbox wrapping if configured."""
        try:
            from thegent.security.macos_sandbox import MacOSSandbox, SandboxLevel

            sandbox = MacOSSandbox.from_env()
            sandbox_level = MacOSSandbox.level_from_settings()
            if sandbox_level not in (SandboxLevel.NONE, SandboxLevel.FULL):
                cmd = sandbox.apply_to_command(cmd, sandbox_level, project_root=project_root)
                _log.debug("macOS sandbox level %r applied", sandbox_level.value)
        except Exception as e:
            _log.debug("Sandbox wrapper failed: %s", e)
        return cmd


class ProcessSpawner:
    """Spawns and monitors subprocess execution."""

    @staticmethod
    def spawn_process(
        cmd: list[str],
        cwd: str,
        env: dict[str, str],
        stdin_handle: int | None = None,
        stdout_handle: Any = None,
        stderr_handle: Any = None,
        spawn_fn: Any = None,
    ) -> subprocess.Popen[bytes]:
        """Spawn subprocess with given configuration.

        spawn_fn: Optional custom spawner (defaults to subprocess.Popen).
        """
        if spawn_fn is None:
            spawn_fn = subprocess.Popen

        try:
            proc = spawn_fn(
                cmd,
                cwd=cwd,
                env=env,
                stdin=stdin_handle if stdin_handle is not None else subprocess.DEVNULL,
                stdout=stdout_handle,
                stderr=stderr_handle,
            )
            return proc
        except Exception as e:
            _log.error("Failed to spawn process: %s", e)
            raise

    @staticmethod
    def setup_fifo_stdin(fifo_path: Path) -> int | None:
        """Set up FIFO for stdin on Unix systems.

        Returns file descriptor or None if not supported.
        """
        if platform.system() == "Windows":
            _log.warning("FIFO not supported on Windows; using DEVNULL.")
            return None

        try:
            if not fifo_path.exists():
                os.mkfifo(str(fifo_path))
            fifo_fd = os.open(str(fifo_path), os.O_RDONLY | os.O_NONBLOCK)
            return fifo_fd
        except Exception as e:
            _log.warning("Failed to create FIFO: %s", e)
            return None

    @staticmethod
    def cleanup_stdin(stdin_handle: int | None) -> None:
        """Clean up stdin file descriptor if it's an FD."""
        if isinstance(stdin_handle, int) and stdin_handle > 0:
            try:
                os.close(stdin_handle)
            except Exception as e:
                _log.debug("Failed to close stdin FD: %s", e)
