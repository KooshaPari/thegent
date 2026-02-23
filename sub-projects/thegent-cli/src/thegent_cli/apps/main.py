"""CLI entry point — delegate to agents via MCP."""

from __future__ import annotations

import sys

import typer

app = typer.Typer(
    name="thegent",
    help="Unified agent orchestration CLI",
    no_args_is_help=True,
)


def _write_stdout(text: str, *, end: str = "\n", flush: bool = False) -> None:
    """Write to stdout (CLI output is expected to use stdout)."""
    sys.stdout.write(text + end)
    if flush:
        sys.stdout.flush()


@app.command()
def free(
    prompt: str = typer.Argument(..., help="Agent task/prompt"),
    agent: str = typer.Option("default", "--agent", "-a", help="Agent persona"),
    model: str | None = typer.Option(None, "--model", "-m"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Run an agent task freely without constraints."""
    import asyncio

    from thegent_cli.mcp_client import CLIAgentClient

    async def _run() -> None:
        client = CLIAgentClient()
        context: dict = {}
        if model:
            context["model"] = model

        async with client.connect():
            async for chunk in client.run_agent(prompt, agent_id=agent, context=context):
                _write_stdout(chunk, end="", flush=True)
        _write_stdout("")

    asyncio.run(_run())


@app.command()
def ps() -> None:
    """List running agents."""
    import asyncio

    from thegent_cli.mcp_client import CLIAgentClient

    async def _run() -> None:
        client = CLIAgentClient()
        async with client.connect():
            agents = await client.list_agents()
            for a in agents:
                _write_stdout(a)

    asyncio.run(_run())
