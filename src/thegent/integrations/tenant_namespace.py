"""Tenancy-safe namespacing for multi-tenant isolation.

# @trace WL-217
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TenantNamespace:
    """Represents a tenant namespace configuration.

    Attributes:
        tenant_id: The tenant identifier.
        prefix: The namespace prefix (typically the tenant_id).
    """

    tenant_id: str
    prefix: str


class TenantNamespaceResolver:
    """Resolver for tenancy-safe key namespacing."""

    def __init__(self, tenant_id: str) -> None:
        """Initialize the namespace resolver.

        Args:
            tenant_id: The tenant identifier.
        """
        self.tenant_id = tenant_id

    def namespace(self, key: str) -> str:
        """Namespace a key with the tenant prefix.

        Args:
            key: The key to namespace.

        Returns:
            The namespaced key in format "{tenant_id}:{key}".
        """
        return f"{self.tenant_id}:{key}"

    def strip_namespace(self, namespaced_key: str) -> str:
        """Remove the namespace prefix from a key.

        Args:
            namespaced_key: The namespaced key to strip.

        Returns:
            The key without the namespace prefix.

        Raises:
            ValueError: If the key does not belong to this tenant.
        """
        prefix = f"{self.tenant_id}:"
        if not namespaced_key.startswith(prefix):
            raise ValueError(
                f"Key '{namespaced_key}' does not belong to tenant '{self.tenant_id}'"
            )
        return namespaced_key[len(prefix) :]

    def is_owned(self, namespaced_key: str) -> bool:
        """Check if a namespaced key belongs to this tenant.

        Args:
            namespaced_key: The namespaced key to check.

        Returns:
            True if the key belongs to this tenant, False otherwise.
        """
        return namespaced_key.startswith(f"{self.tenant_id}:")

    def namespace_dict(self, data: dict[str, str]) -> dict[str, str]:
        """Namespace all keys in a dictionary.

        Args:
            data: Dictionary to namespace.

        Returns:
            New dictionary with all keys namespaced.
        """
        return {self.namespace(key): value for key, value in data.items()}

    def strip_dict(self, data: dict[str, str]) -> dict[str, str]:
        """Remove namespace prefix from all keys in a dictionary.

        Args:
            data: Dictionary to strip.

        Returns:
            New dictionary with all keys stripped of namespace prefix.

        Raises:
            ValueError: If any key does not belong to this tenant.
        """
        result = {}
        for key, value in data.items():
            result[self.strip_namespace(key)] = value
        return result
