"""Thegent CLI plan/DAG commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import orjson as json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, cast

import typer

from rich.table import Table

from thegent.cli.commands.plan_output_helpers import (
    render_plan_next_items,
    resolve_output_format,
)

from thegent.cli.commands._cli_shared import (
    RunRegistry,
    ThegentSettings,
    _default_owner_tag,
    _parse_dag_full,
    _resolve_cwd,
    console,
)


def plan_claim_cmd(item_id: str, agent_id: str | None = None, cd: Path | None = None) -> None:
    """Claim an item in the unified work stream."""
    from thegent.cli.commands.work_stream_impl import work_stream_claim_impl
    from thegent.discovery import get_current_agent_id

    aid = agent_id or get_current_agent_id()
    result = work_stream_claim_impl(item_id, aid, cd=cd)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        if result.get("remediation"):
            console.print(f"[yellow]{result['remediation']}[/yellow]")
        raise typer.Exit(1)
    console.print(f"[green]Claimed {item_id} for {aid}[/green]")



def plan_complete_cmd(item_id: str, agent_id: str | None = None, cd: Path | None = None) -> None:
    """Mark an item as complete in the unified work stream."""
    from thegent.cli.commands.work_stream_impl import work_stream_complete_impl
    from thegent.discovery import get_current_agent_id

    aid = agent_id or get_current_agent_id()
    result = work_stream_complete_impl(item_id, aid, cd=cd)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Completed {item_id} (agent: {aid})[/green]")



