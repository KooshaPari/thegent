"""Example: Integrating isolation provider into executor.

This module demonstrates how to integrate SubUserIsolationProvider
into the main agent executor for Phase 1.
"""

from thegent.isolation.sub_user_provider import SubUserIsolationProvider


class IsolatedExecutor:
    """Example executor with isolation support."""

    def __init__(
        self,
        isolation_provider: SubUserIsolationProvider | None = None,
        enable_isolation: bool = False,
    ) -> None:
        """
        Initialize executor with optional isolation.

        Args:
            isolation_provider: Provider for tenant isolation
            enable_isolation: Whether to use isolation
        """
        self.isolation_provider = isolation_provider
        self.enable_isolation = enable_isolation

        if enable_isolation and not isolation_provider:
            # Create default provider
            self.isolation_provider = SubUserIsolationProvider()

    def execute_for_tenant(
        self,
        tenant_id: str,
        agent_id: str,
        command: list,
        timeout_sec: int = 300,
    ) -> dict:
        """
        Execute a command for a tenant with optional isolation.

        Integration point: This is where the executor would use
        the isolation provider to ensure commands run in isolated
        tenant contexts.

        Args:
            tenant_id: Tenant identifier
            agent_id: Agent identifier
            command: Command to execute
            timeout_sec: Execution timeout

        Returns:
            Execution result dict with returncode, stdout, stderr
        """
        if not self.enable_isolation:
            # Fall back to non-isolated execution
            import subprocess

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        # Isolated execution
        context = self.isolation_provider.allocate_tenant(tenant_id, agent_id)
        try:
            return self.isolation_provider.execute_in_context(
                context,
                command,
                timeout_sec=timeout_sec,
            )
        finally:
            # Clean up tenant context
            self.isolation_provider.cleanup_tenant(context)


# Usage example (doctest)
def example_usage():
    """
    Example: How to use IsolatedExecutor.

    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     provider = SubUserIsolationProvider(base_home_dir=tmpdir)
    ...     executor = IsolatedExecutor(
    ...         isolation_provider=provider,
    ...         enable_isolation=True,
    ...     )
    ...     result = executor.execute_for_tenant(
    ...         tenant_id='tenant-1',
    ...         agent_id='agent-1',
    ...         command=['echo', 'hello'],
    ...     )
    ...     print(f"Exit code: {result['returncode']}")
    ...     print(f"Output: {result['stdout'].strip()}")
    Exit code: 0
    Output: hello
    """
