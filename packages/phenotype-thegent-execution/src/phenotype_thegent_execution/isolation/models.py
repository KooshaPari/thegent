"""Data models for isolation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IsolationMode(Enum):
    """Isolation mode for tenant execution."""

    SUB_USER = "sub-user"
    OS_USER = "os-user"
    DOCKER = "docker"


@dataclass
class TenantContext:
    """Context for a single tenant execution."""

    tenant_id: str
    agent_id: str | None = None
    uid: int | None = None
    gid: int | None = None
    home_dir: str | None = None
    env_vars: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize environment variables."""
        if not self.env_vars:
            self.env_vars = {
                "THEGENT_TENANT_ID": self.tenant_id,
            }
            if self.agent_id:
                self.env_vars["THEGENT_AGENT_ID"] = self.agent_id
