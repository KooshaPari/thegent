"""Autosync release and migration checklist.

# @trace WL-200
"""

from __future__ import annotations


def get_checklist_items() -> list[str]:
    """Get the list of checklist items for autosync enablement.

    Returns:
        List of key steps required for autosync enablement.
    """
    return [
        "Set THEGENT_AUTOSYNC_ENABLED=1 environment variable",
        "Configure THEGENT_SYNC_INTERVAL (in seconds)",
        "Provide THEGENT_GH_TOKEN with appropriate scopes",
        "Enable GitHub Actions workflows",
        "Review and accept sync policy",
        "Verify endpoint reachability",
        "Test with non-production repository first",
        "Monitor sync logs and metrics",
        "Plan rollback strategy",
        "Document custom mappings and policies",
    ]


def verify_prerequisites(config: dict) -> list[str]:
    """Verify that all prerequisites for autosync are met.

    Args:
        config: Configuration dictionary with optional keys:
            - 'autosync_enabled': boolean
            - 'sync_interval': integer (seconds)
            - 'gh_token_present': boolean
            - 'workflows_enabled': boolean
            - 'policy_accepted': boolean

    Returns:
        List of missing prerequisites. Empty list if all are met.
    """
    missing: list[str] = []

    if not config.get("autosync_enabled"):
        missing.append("THEGENT_AUTOSYNC_ENABLED environment variable not set")

    if not config.get("sync_interval"):
        missing.append("THEGENT_SYNC_INTERVAL not configured")

    if not config.get("gh_token_present"):
        missing.append("THEGENT_GH_TOKEN environment variable not set")

    if not config.get("workflows_enabled"):
        missing.append("GitHub Actions workflows not enabled")

    if not config.get("policy_accepted"):
        missing.append("Sync policy not accepted")

    return missing
