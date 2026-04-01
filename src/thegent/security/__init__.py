"""Security module for thegent.

Provides RBAC, secrets scanning, and other security-related functionality.
"""

from thegent.security.rbac import Permission, RBACManager, Role
from thegent.security.secrets import (
    SecretMatch,
    detect_secret_type,
    redact_secrets,
    scan_secrets,
    scan_secrets_file,
)

__all__ = [
    "Permission",
    "RBACManager",
    "Role",
    "SecretMatch",
    "detect_secret_type",
    "redact_secrets",
    "scan_secrets",
    "scan_secrets_file",
]
