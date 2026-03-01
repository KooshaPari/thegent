"""Sub-user isolation provider implementation."""

import logging
import os
import resource
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
from pathlib import Path
from typing import Any

from thegent.infra.os_user_manager import OSUserManager
from thegent_execution.isolation.base_provider import IsolationProvider
from thegent_execution.isolation.exceptions import (
    ExecutionContextError,
    TenantAllocationError,
)
from thegent_execution.isolation.models import TenantContext
from thegent_execution.isolation.uid_pool import UidPool
from thegent_execution.isolation.vfs import VfsAdapter
from thegent.orchestration.execution.cmd_share import CommandSharer

logger = logging.getLogger(__name__)


class SubUserIsolationProvider(IsolationProvider):
    """
    Optimized isolation provider using persistent UID pools,
    VFS-backed home directories, and resource guardrails.

    Supports L1/L2 nesting via OSUserManager.
    """

    def __init__(
        self,
        base_home_dir: str = "/tmp/thegent",
        base_uid: int = 2000,
        uid_pool_size: int = 1000,
        state_dir: str | None = None,
        skel_dir: str | None = None,
        enable_l1_nesting: bool = False,
    ) -> None:
        """
        Initialize SubUserIsolationProvider.

        Args:
            base_home_dir: Base directory for tenant home directories
            base_uid: Starting UID for tenant allocation
            uid_pool_size: Maximum number of tenants (pool size)
            state_dir: Directory for persistence (defaults to base_home_dir/.state)
            skel_dir: Skeleton directory for home dir templates
            enable_l1_nesting: Whether to use real OS users for L1 identity
        """
        self.base_home_dir = Path(base_home_dir)
        self.state_dir = Path(state_dir) if state_dir else self.base_home_dir / ".state"
        self.skel_dir = Path(skel_dir) if skel_dir else None
        self.enable_l1_nesting = enable_l1_nesting

        # Core components for optimization
        self.uid_pool = UidPool(
            base_uid=base_uid,
            size=uid_pool_size,
            state_file=self.state_dir / "uid_pool.json",
        )
        self.vfs = VfsAdapter(base_skel_dir=self.skel_dir)
        self.os_user_manager = OSUserManager() if enable_l1_nesting else None
        self.cmd_sharer = CommandSharer(self.base_home_dir / ".share")

        self._tenant_cache: dict[str, TenantContext] = {}

        # Ensure directories exist
        self.base_home_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def allocate_tenant(self, tenant_id: str, agent_id: str | None = None, role: str | None = None) -> TenantContext:
        """
        Allocate resources for a tenant using persistent UID pool and VFS.
        Supports optional L1 OS User creation.
        """
        # Check cache first (idempotency)
        if tenant_id in self._tenant_cache:
            return self._tenant_cache[tenant_id]

        try:
            l1_user = None
            if self.enable_l1_nesting and role:
                # Create/Get L1 OS User for this role (e.g., 'frontend_lead')
                l1_user = self.os_user_manager.create_user(role)

            # Allocate deterministic UID from persistent pool for L2
            uid = self.uid_pool.allocate(tenant_id)
            gid = uid  # Use same UID as GID for simplicity

            # Create optimized home directory
            home_dir = self.base_home_dir / tenant_id
            self.vfs.create_home_dir(home_dir, tenant_id)

            # Create TenantContext
            ctx = TenantContext(
                tenant_id=tenant_id,
                agent_id=agent_id,
                uid=uid,
                gid=gid,
                home_dir=str(home_dir),
            )

            if l1_user:
                ctx.metadata["l1_username"] = l1_user.username
                ctx.metadata["l1_uid"] = l1_user.uid

            # Cache the context
            self._tenant_cache[tenant_id] = ctx
            return ctx

        except Exception as e:
            raise TenantAllocationError(f"Failed to allocate tenant {tenant_id}: {e}")

    def execute_in_context(
        self,
        context: TenantContext,
        command: list,
        timeout_sec: int = 300,
        limits: dict[str, Any] | None = None,
        share: bool = False,
    ) -> dict:
        """
        Execute a command in the tenant's isolated context with resource guardrails.
        If 'share' is True, uses CommandSharer to debounce and attach to existing runs.
        """
        try:
            # Build environment with tenant variables
            assert context.home_dir is not None, f"home_dir must be set for tenant {context.tenant_id}"
            env = os.environ.copy()
            env.update(context.env_vars)
            env["HOME"] = context.home_dir
            env["TMPDIR"] = context.home_dir  # Isolate temp files

            if share:
                return self.cmd_sharer.execute_shared(command=command, cwd=Path(context.home_dir), env=env)

            # Default guardrail limits (can be tuned via Harness Cards)
            effective_limits = {
                "nproc": 100,
                "nofile": 1024,
                "as": 1024 * 1024 * 1024,  # 1GB virtual memory
            }
            if limits:
                effective_limits.update(limits)

            def preexec_fn():
                """Apply POSIX resource limits before execution."""
                try:
                    # Set process count limit
                    resource.setrlimit(resource.RLIMIT_NPROC, (effective_limits["nproc"], effective_limits["nproc"]))
                    # Set file descriptor limit
                    resource.setrlimit(resource.RLIMIT_NOFILE, (effective_limits["nofile"], effective_limits["nofile"]))
                    # Set address space (memory) limit
                    resource.setrlimit(resource.RLIMIT_AS, (effective_limits["as"], effective_limits["as"]))
                except Exception as e:
                    # Non-fatal: some systems (WSL2 with specific configs) may restrict setrlimit
                    logger.debug(f"Failed to set rlimit: {e}")

            # Execute command
            result = shim_run(
                command,
                cwd=context.home_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                preexec_fn=preexec_fn if os.name == "posix" else None,
                check=False,
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            raise ExecutionContextError(f"Command timeout after {timeout_sec}s: {' '.join(command)}")
        except Exception as e:
            raise ExecutionContextError(f"Failed to execute command in context {context.tenant_id}: {e}")

    def cleanup_tenant(self, context: TenantContext) -> None:
        """
        Clean up resources allocated for a tenant.
        """
        try:
            # Use VFS for safe cleanup (unmount + remove)
            assert context.home_dir is not None, f"home_dir must be set for tenant {context.tenant_id}"
            home_dir = Path(context.home_dir)
            self.vfs.cleanup_home_dir(home_dir, context.tenant_id)

            # Release UID back to pool
            self.uid_pool.release(context.tenant_id)

            # Remove from cache
            self._tenant_cache.pop(context.tenant_id, None)

        except Exception as e:
            logger.warning(f"Cleanup failed for tenant {context.tenant_id}: {e}")
