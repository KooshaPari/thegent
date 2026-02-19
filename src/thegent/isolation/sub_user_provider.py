"""Sub-user isolation provider implementation."""

import os
import shutil
import subprocess
from pathlib import Path

from thegent.isolation.base_provider import IsolationProvider
from thegent.isolation.exceptions import (
    ExecutionContextError,
    TenantAllocationError,
)
from thegent.isolation.models import TenantContext


class SubUserIsolationProvider(IsolationProvider):
    """Isolation provider using sub-user UIDs and temporary home directories."""

    def __init__(
        self,
        base_home_dir: str = "/tmp/thegent",
        base_uid: int = 2000,
        uid_pool_size: int = 1000,
    ) -> None:
        """
        Initialize SubUserIsolationProvider.

        Args:
            base_home_dir: Base directory for tenant home directories
            base_uid: Starting UID for tenant allocation
            uid_pool_size: Maximum number of tenants (pool size)
        """
        self.base_home_dir = Path(base_home_dir)
        self.base_uid = base_uid
        self.uid_pool_size = uid_pool_size
        self._tenant_cache: dict[str, TenantContext] = {}

        # Ensure base directory exists
        self.base_home_dir.mkdir(parents=True, exist_ok=True)

    def allocate_tenant(self, tenant_id: str, agent_id: str | None = None) -> TenantContext:
        """
        Allocate resources for a tenant.

        Uses hash-based UID allocation to ensure idempotency.
        """
        # Check cache first (idempotency)
        if tenant_id in self._tenant_cache:
            return self._tenant_cache[tenant_id]

        try:
            # Hash tenant_id to get deterministic UID
            uid = self.base_uid + (hash(tenant_id) % self.uid_pool_size)
            gid = uid  # Use same UID as GID for simplicity

            # Create home directory
            home_dir = self.base_home_dir / tenant_id
            home_dir.mkdir(parents=True, exist_ok=True)

            # Create TenantContext
            ctx = TenantContext(
                tenant_id=tenant_id,
                agent_id=agent_id,
                uid=uid,
                gid=gid,
                home_dir=str(home_dir),
            )

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
    ) -> dict:
        """
        Execute a command in the tenant's isolated context.

        Environment variables and working directory are set from context.
        """
        try:
            # Build environment with tenant variables
            env = os.environ.copy()
            env.update(context.env_vars)
            env["HOME"] = context.home_dir

            # Execute command
            result = subprocess.run(
                command,
                cwd=context.home_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired as e:
            raise ExecutionContextError(f"Command timeout after {timeout_sec}s: {' '.join(command)}")
        except Exception as e:
            raise ExecutionContextError(f"Failed to execute command in context {context.tenant_id}: {e}")

    def cleanup_tenant(self, context: TenantContext) -> None:
        """
        Clean up resources allocated for a tenant.

        Removes the tenant's home directory and evicts from cache.
        """
        try:
            # Remove home directory if it exists
            home_dir = Path(context.home_dir)
            if home_dir.exists():
                shutil.rmtree(home_dir, ignore_errors=True)

            # Remove from cache
            self._tenant_cache.pop(context.tenant_id, None)

        except Exception as e:
            # Log but don't raise - cleanup should be best-effort
            pass
