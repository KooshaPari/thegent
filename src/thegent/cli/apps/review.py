"""WL-107: Read-only code review agent app.

Standalone Typer app that executes a read-only agent turn and emits a
structured review report.  sandbox_mode=read_only and allowed_tools are
enforced inside review_impl(); this module is the presentation layer only.

# @trace WL-107
"""

from __future__ import annotations

import json

import typer
from rich.console import Console

console = Console()

app = typer.Typer(name="review", help="Code review with read-only agent.")


@app.command("run", help="Run a read-only review and emit structured findings.")
def review_run(
    prompt: str = typer.Argument(..., help="Review request prompt"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Agent to run for review"),
    model: str | None = typer.Option(None, "--model", "-m", help="LLM model override"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    """WL-107: Execute a read-only review agent turn and render findings.

    Exit code 0 = no issues found.
    Exit code 1 = one or more issues found.
    Exit code 2 = invalid --format or review output failed schema validation.
    Any other non-zero exit code = review agent run failure.

    # @trace WL-107
    """
    from thegent.cli.commands.cli import _format_context_usage_line
    from thegent.cli.commands.impl import review_impl

    output_format = format.strip().lower()
    if output_format not in {"rich", "json"}:
        console.print(f"[red]Unsupported --format '{format}'. Use 'rich' or 'json'.[/red]")
        raise typer.Exit(2)

    try:
        result = review_impl(prompt=prompt, agent=agent, model=model)
    except ValueError as exc:
        console.print(f"[red]Review output validation failed:[/red] {exc}")
        raise typer.Exit(2) from exc

    run_exit = result.get("exit_code", 1)
    if run_exit not in (0, 1):
        console.print(f"[red]Review run failed:[/red] {result.get('error', '')}")
        raise typer.Exit(run_exit)

    issues = result["issues"]
    context_usage = result.get("context_usage")
    if output_format == "json":
        payload: dict[str, object] = {
            "summary": result["summary"],
            "overall_rating": result["overall_rating"],
            "issues": issues,
        }
        if isinstance(context_usage, dict):
            payload["context_usage"] = context_usage
        console.print(json.dumps(payload, indent=2))
    else:
        console.print(f"[bold]Summary:[/bold] {result['summary']}")
        console.print(f"[bold]Overall Rating:[/bold] {result['overall_rating']}")
        context_line = _format_context_usage_line(context_usage)
        if context_line:
            console.print(f"[dim]{context_line}[/dim]")
        if issues:
            for issue in issues:
                console.print(
                    f"- [{issue['severity']}] {issue['file']}:{issue['line']} - "
                    f"{issue['message']} (fix: {issue['suggestion']})"
                )
        else:
            console.print("[green]No issues found.[/green]")
    raise typer.Exit(1 if issues else 0)
