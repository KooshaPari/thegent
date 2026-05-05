"""Stub module."""


class KeyIsolator:
    """Isolator for keys in multi-tenant environment."""

    def __init__(self, tenant_id: str = "") -> None:
        self.tenant_id = tenant_id

    def isolate(self, key: str) -> str:
        """Isolate a key for the current tenant."""
        return f"{self.tenant_id}:{key}"


__all__ = ["KeyIsolator"]
