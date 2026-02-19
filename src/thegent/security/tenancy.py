"""WP-19001: Multi-Tenant Key Isolation.
Ensures API keys are isolated by owner/tenant in the auth directory.
"""

import shutil
from pathlib import Path

from thegent.config import ThegentSettings


class KeyIsolator:
    """Manages isolated key storage for multi-tenant environments."""

    def __init__(self, settings: ThegentSettings | None = None) -> None:
        self.settings = settings or ThegentSettings()
        self.base_auth_dir = self.settings.cliproxy_auth_dir.expanduser().resolve()

    def get_tenant_dir(self, owner: str) -> Path:
        """Get the isolated auth directory for a specific owner."""
        # Sanitize owner name to prevent path traversal
        safe_owner = "".join(c for c in owner if c.isalnum() or c in "-_").strip()
        if not safe_owner:
            safe_owner = "default"

        tenant_dir = self.base_auth_dir / "tenants" / safe_owner
        tenant_dir.mkdir(parents=True, exist_ok=True)
        return tenant_dir

    def isolate_key(self, owner: str, provider: str, api_key: str) -> Path:
        """Write an API key to the isolated tenant directory."""
        tenant_dir = self.get_tenant_dir(owner)
        key_file = tenant_dir / f"{provider.lower()}.key"
        key_file.write_text(api_key.strip(), encoding="utf-8")
        # Ensure restrictive permissions (0600)
        key_file.chmod(0o600)
        return key_file

    def get_key(self, owner: str, provider: str) -> str | None:
        """Retrieve a key for a specific owner and provider."""
        tenant_dir = self.get_tenant_dir(owner)
        key_file = tenant_dir / f"{provider.lower()}.key"
        if key_file.exists():
            return key_file.read_text(encoding="utf-8").strip()
        return None

    def list_tenants(self) -> list[str]:
        """List all tenants with isolated keys."""
        tenants_dir = self.base_auth_dir / "tenants"
        if not tenants_dir.exists():
            return []
        return [d.name for d in tenants_dir.iterdir() if d.is_dir()]

    def delete_tenant(self, owner: str) -> None:
        """Delete all keys for a specific tenant."""
        tenant_dir = self.get_tenant_dir(owner)
        if tenant_dir.exists() and tenant_dir != self.base_auth_dir:
            shutil.rmtree(tenant_dir)
