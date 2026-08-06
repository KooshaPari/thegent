"""Data protection commands."""

from __future__ import annotations

from typing import Any


def data_protection_cmd(format: str | None = None) -> None:
    """Show data protection status.

    WL-156 Phase 1: dispatch through ``_normalize_output_format`` so the
    WL-124 re-export surface is the single source of truth for output
    rendering (rich / json / csv / md). The legacy ``format == "json"``
    fast-path is preserved as a fallback for direct call sites that
    bypass the helper.

    Args:
        format: Optional output format hint. When ``None`` we fall back
            to the canonical rich rendering. Otherwise the value is
            normalized via ``_normalize_output_format`` and dispatched
            to the matching renderer.
    """
    from thegent.cli.commands._cli_shared import _normalize_output_format

    from thegent.cli.governance.governance_impl import get_data_protection_status_impl

    status: dict[str, Any] = get_data_protection_status_impl()

    if format is None:
        # Default: rich table (canonical behavior pre-WL-156).
        from thegent.cli import console

        from rich.table import Table

        table = Table(title="Data Protection Status")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for key, value in status.items():
            table.add_row(key, str(value))

        console.print(table)
        return

    # WL-156: dispatch via the canonical output-format helper.
    normalized = _normalize_output_format(format)

    if normalized == "json":
        import orjson as json

        from thegent.cli import console

        console.print(json.dumps(status))
    elif normalized == "rich":
        from thegent.cli import console

        from rich.table import Table

        table = Table(title="Data Protection Status")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for key, value in status.items():
            table.add_row(key, str(value))

        console.print(table)
    else:
        # csv / md / unknown — emit plain text best-effort so we never
        # silently swallow a call to a real CLI command.
        from thegent.cli import console

        for key, value in status.items():
            console.print(f"{key}: {value}")
