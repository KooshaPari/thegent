"""WP-19002: Role-Based Access Control (RBAC).
Formally defines roles, permissions, and access checks.
"""

from enum import StrEnum
from typing import Any

from thegent.governance.personas import PersonaManager


class Permission(StrEnum):
    """Fine-grained permissions."""

    RUN_AGENT = "run_agent"
    VIEW_LOGS = "view_logs"
    MANAGE_POLICY = "manage_policy"
    OVERRIDE_POLICY = "override_policy"
    PURGE_DATA = "purge_data"
    MANAGE_TEAM = "manage_team"
    VIEW_REPORTS = "view_reports"


class Role(StrEnum):
    """Standard operator roles."""

    ADMIN = "platform_admin"
    OPERATOR = "operator"
    INCIDENT_COMMANDER = "incident_commander"
    AUDITOR = "compliance_officer"


# Mapping of roles to fine-grained permissions
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: set(Permission),
    Role.OPERATOR: {
        Permission.RUN_AGENT,
        Permission.VIEW_LOGS,
        Permission.VIEW_REPORTS,
    },
    Role.INCIDENT_COMMANDER: {
        Permission.RUN_AGENT,
        Permission.VIEW_LOGS,
        Permission.OVERRIDE_POLICY,
        Permission.VIEW_REPORTS,
    },
    Role.AUDITOR: {
        Permission.VIEW_LOGS,
        Permission.VIEW_REPORTS,
    },
}


class RBACManager:
    """Orchestrates RBAC checks across the system."""

    def __init__(self) -> None:
        self.persona_manager = PersonaManager()

    def has_permission(self, role: Role, permission: Permission) -> bool:
        """Check if a role has a specific permission."""
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return permission in role_perms

    def check_access(self, role: Role, operation: str, lane: str = "standard") -> dict[str, Any]:
        """Hybrid check using both fine-grained permissions and persona-based constraints."""
        # 1. Map operation to required permission (simplified mapping)
        required_perm = self._map_operation_to_permission(operation)

        # 2. Check fine-grained permission
        if required_perm and not self.has_permission(role, required_perm):
            return {
                "allowed": False,
                "reason": f"Role '{role}' lacks required permission '{required_perm}' for '{operation}'",
            }

        # 3. Delegate to PersonaManager for legacy/contextual checks (lane, budget, etc.)
        return self.persona_manager.check_access(role, operation, lane)

    def _map_operation_to_permission(self, operation: str) -> Permission | None:
        """Maps a command/operation string to a required Permission."""
        op = operation.lower()
        if op.startswith(("run", "bg", "orchestrate")):
            return Permission.RUN_AGENT
        if op.startswith(("logs", "history", "inspect")):
            return Permission.VIEW_LOGS
        if op.startswith(("govern purge", "purge")):
            return Permission.PURGE_DATA
        if op.startswith(("govern", "policy")):
            return Permission.MANAGE_POLICY
        if op.startswith("team"):
            return Permission.MANAGE_TEAM
        if op.startswith(("report", "cockpit", "status")):
            return Permission.VIEW_REPORTS
        return None
