"""Governance sign-off template utilities for autosync production enablement.

This module provides functions to retrieve and render the autosync sign-off
template, which documents approval and validation before production enablement.
"""

from __future__ import annotations

from pathlib import Path


def get_template_path() -> Path:
    """Get the path to the autosync sign-off template.

    Returns:
        Path to docs/governance/AUTOSYNC_SIGNOFF_TEMPLATE.md.
    """
    # Resolve relative to this file's location
    current_file = Path(__file__).resolve()
    # Navigate up: integrations -> thegent -> src -> root
    project_root = current_file.parents[3]
    template_path = project_root / "docs" / "governance" / "AUTOSYNC_SIGNOFF_TEMPLATE.md"
    return template_path


def render_template(
    date: str, reviewer: str, environment: str, connectors: list[str]
) -> str:
    """Render the sign-off template with provided values.

    Reads the template and fills in the Summary section with the provided values.

    Args:
        date: Date in YYYY-MM-DD format.
        reviewer: Reviewer name or Agent ID.
        environment: Environment name (e.g., "staging", "production").
        connectors: List of connector names.

    Returns:
        Rendered template with Summary fields populated.

    Raises:
        FileNotFoundError: If template file does not exist.
    """
    template_path = get_template_path()
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found at {template_path}")

    content = template_path.read_text()

    # Replace Summary section values
    connectors_str = ", ".join(connectors)

    # Replace table rows in Summary section
    content = content.replace("| Date | YYYY-MM-DD |", f"| Date | {date} |")
    content = content.replace("| Reviewer | Agent ID or Human Name |", f"| Reviewer | {reviewer} |")
    content = content.replace("| Environment | staging / production |", f"| Environment | {environment} |")
    content = content.replace("| Connector(s) | comma-separated list |", f"| Connector(s) | {connectors_str} |")

    return content
