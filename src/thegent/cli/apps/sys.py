"""Logical stream: System and Lifecycle Operations."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="System configuration, MCP servers, and daemon ops.")


@app.command("setup", help="Interactive system setup and configuration.")
def sys_setup():
    from thegent.cli.commands.cli import setup_cmd

    setup_cmd()


@app.command("mcp", help="Manage Model Context Protocol (MCP) servers.")
def sys_mcp(
    action: str = typer.Argument(..., help="Action (list|add|remove|prune)"),
    server: str | None = typer.Option(None, "--server", "-s", help="Server name"),
    command: str | None = typer.Option(None, "--command", "-c", help="Command to run the server"),
):
    from thegent.cli.commands.cli import mcp_cmd

    mcp_cmd(action=action, name=server, command=command)


@app.command("lsp", help="Manage Language Server Protocol (LSP) processes.")
def sys_lsp(
    action: str = typer.Argument(..., help="Action (list|restart|prune)"),
    language: str | None = typer.Option(None, "--lang", "-l", help="Language identifier"),
):
    from thegent.cli.commands.cli import lsp_cmd

    lsp_cmd(action=action, language=language)


@app.command("cp", help="Manage the Thegent control-plane daemon.")
def sys_cp(
    action: str = typer.Argument(..., help="Action (status|start|stop|restart)"),
):
    from thegent.cli.commands.cli import cp_cmd

    cp_cmd(action=action)


@app.command("session", help="Manage agent background sessions and artifacts.")
def sys_session(
    action: str = typer.Argument(..., help="Action (list|prune|archive)"),
    session_id: str | None = typer.Option(None, "--id", "-i", help="Specific session ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Force the action"),
):
    from thegent.cli.commands.cli import session_cmd

    session_cmd(action=action, session_id=session_id, force=force)


@app.command("config", help="View or modify system configuration.")
def sys_config(
    action: str = typer.Argument("view", help="Action (view|set|unset)"),
    key: str | None = typer.Option(None, "--key", "-k", help="Configuration key"),
    value: str | None = typer.Option(None, "--value", "-v", help="Configuration value"),
):
    from thegent.cli.commands.cli import config_cmd

    config_cmd(action=action, key=key, value=value)


@app.command("terminal", help="Manage managed terminal sessions.")
def sys_terminal(
    action: str = typer.Argument("list", help="Action (list|open|prune)"),
    name: str | None = typer.Option(None, "--name", "-n", help="Terminal session name"),
):
    from thegent.cli.commands.cli import terminal_cmd

    terminal_cmd(action=action, name=name)
