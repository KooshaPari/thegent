"""Operations command group extracted from infra_cmds.py (WL-124)."""

from __future__ import annotations

import orjson as json
import sys
from typing import Any

import typer
from rich.table import Table


def operations_cmd(*, format: str | None, operation: str | None, console: Any) -> None:
    """List universal operation taxonomy (orchestrate, govern, recover, observe, plan)."""
    from thegent_agents.operations import Operation, get_operations_by_type, list_operations

    if operation:
        try:
            op = Operation(operation)
        except ValueError:
            console.print(
                f"[red]Unknown operation: {operation}. Use: orchestrate, govern, recover, observe, plan[/red]"
            )
            raise typer.Exit(1)
        entries = get_operations_by_type(op)
        data = {
            op.value: [{"command": e.command, "description": e.description, "mcp_tool": e.mcp_tool} for e in entries]
        }
    else:
        data = list_operations()

    if format == "json":
        sys.stdout.write(json.dumps(data).decode() + "\n")
        return

    table = Table(title="Universal Operations")
    table.add_column("Operation")
    table.add_column("Command")
    table.add_column("Description")
    table.add_column("MCP Tool")
    for op_name, items in data.items():
        for index, item in enumerate(items):
            table.add_row(
                op_name if index == 0 else "",
                item["command"],
                item["description"],
                item.get("mcp_tool") or "",
            )
    console.print(table)


__all__ = ["operations_cmd"]
