"""Re-export facade for governance policy and compliance commands (WL-124).

Consolidates policy core, compliance (trust/sigs/compliance), and health commands.
"""

# @trace WL-124
from __future__ import annotations

# Re-export all from core + compliance facades
from thegent.cli.commands.governance_policy_core_cmds import *  # noqa: F401, F403
from thegent.cli.commands.governance_compliance_cmds import *  # noqa: F401, F403


def govern_configure_cmd(*args, **kwargs):
    """Lazy import of govern_configure_cmd."""
    # pyright: ignore[reportMissingImports]
    from thegent.cli.commands.governance_health_core_cmds import govern_configure_cmd as _cmd
    return _cmd(*args, **kwargs)


def govern_go_health_cmd(*args, **kwargs):
    """Lazy import of govern_go_health_cmd."""
    # pyright: ignore[reportMissingImports]
    from thegent.cli.commands.governance_health_core_cmds import govern_go_health_cmd as _cmd
    return _cmd(*args, **kwargs)


def govern_go_cycle_cmd(*args, **kwargs):
    """Lazy import of govern_go_cycle_cmd."""
    # pyright: ignore[reportMissingImports]
    from thegent.cli.commands.governance_health_core_cmds import govern_go_cycle_cmd as _cmd
    return _cmd(*args, **kwargs)


def govern_go_status_cmd(*args, **kwargs):
    """Lazy import of govern_go_status_cmd."""
    # pyright: ignore[reportMissingImports]
    try:
        from thegent.cli.commands.governance_agileplus_cmds import govern_go_status_cmd as _cmd
    except (ImportError, AttributeError):
        from thegent.cli.commands.governance_health_core_cmds import govern_go_status_cmd as _cmd
    return _cmd(*args, **kwargs)


def govern_go_watch_cmd(*args, **kwargs):
    """Lazy import of govern_go_watch_cmd."""
    # pyright: ignore[reportMissingImports]
    from thegent.cli.commands.governance_agileplus_cmds import govern_go_watch_cmd as _cmd
    return _cmd(*args, **kwargs)
