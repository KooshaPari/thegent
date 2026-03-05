"""Execution module boundary for thegent."""

def get_execution_package():
    """Return the canonical execution package module."""
    import thegent_execution as execution_pkg

    return execution_pkg


__all__ = ["get_execution_package"]
