"""Governance module boundary for thegent."""

def get_governance_package():
    """Return the canonical governance/audit package module."""
    import thegent_audit as audit_pkg

    return audit_pkg


__all__ = ["get_governance_package"]
