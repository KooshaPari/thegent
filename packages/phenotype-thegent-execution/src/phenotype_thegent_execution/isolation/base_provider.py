"""Abstract base class for isolation providers."""

from abc import ABC, abstractmethod

from phenotype_thegent_execution.isolation.models import TenantContext


class IsolationProvider(ABC):
    """Abstract interface for tenant isolation."""

    @abstractmethod
    def allocate_tenant(self, tenant_id: str, agent_id: str | None = None) -> TenantContext:
        """
        Allocate resources for a tenant.

        Args:
            tenant_id: Unique identifier for the tenant
            agent_id: Optional agent identifier

        Returns:
            TenantContext with allocated resources

        Raises:
            TenantAllocationError: If allocation fails
        """

    @abstractmethod
    def execute_in_context(self, context: TenantContext, command: list, timeout_sec: int = 300) -> dict:
        """
        Execute a command in the tenant's isolated context.

        Args:
            context: TenantContext for this execution
            command: List of command arguments
            timeout_sec: Execution timeout in seconds

        Returns:
            Dict with 'returncode', 'stdout', 'stderr'

        Raises:
            ExecutionContextError: If execution fails
        """

    @abstractmethod
    def cleanup_tenant(self, context: TenantContext) -> None:
        """
        Clean up resources allocated for a tenant.

        Args:
            context: TenantContext to clean up

        Raises:
            IsolationError: If cleanup fails
        """
