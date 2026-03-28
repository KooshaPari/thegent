"""Helpers for sitback dashboard panel rendering."""

from __future__ import annotations

from rich.panel import Panel


def build_dashboard_panels(data: dict, profile: str) -> tuple[list[Panel], str]:
    """Build dashboard panels and summary line from sitback payload."""
    sessions = data.get("sessions", {})
    cockpit = data.get("cockpit", {})
    terminals = data.get("terminals", {})

    session_panel = Panel(
        f"[bold]Sessions[/bold]\n"
        f"Running: [green]{sessions.get('running', 0)}[/green] | "
        f"Failed: [red]{sessions.get('failed', 0)}[/red] | "
        f"Total: {sessions.get('total', 0)}",
        title="Orchestration",
        border_style="cyan",
    )

    circuits = cockpit.get("circuits", {})
    open_c = circuits.get("open", [])
    circuit_text = "\n".join(f"- {target}: [red]OPEN[/red]" for target in open_c) or "[green]All Closed[/green]"
    circuit_panel = Panel(
        f"[bold]Circuits[/bold]\n{circuit_text}",
        title="Resource State",
        border_style="magenta",
    )

    drift = cockpit.get("drift", {})
    budget = cockpit.get("budget", {})
    drift_color = "green" if drift.get("within_budget", True) else "red"
    drift_panel = Panel(
        f"[bold]Drift[/bold]\n"
        f"Structural: [{drift_color}]{drift.get('structural_rate_pct', 0)}%[/{drift_color}] | "
        f"Semantic: [{drift_color}]{drift.get('semantic_rate_pct', 0)}%[/{drift_color}]",
        title="Quality Gate",
        border_style=drift_color,
    )

    mtd_total = budget.get("mtd_total", 0)
    mtd_budget = budget.get("mtd_budget", 100)
    budget_color = "green" if budget.get("within_budget", True) else "red"
    gov_hint = "" if data.get("govern_configured", True) else " [dim](run: thegent govern configure)[/dim]"
    budget_panel = Panel(
        f"[bold]Budget MTD[/bold]\n[{budget_color}]${mtd_total:.2f}[/{budget_color}] / ${mtd_budget:.2f}{gov_hint}",
        title="Governance",
        border_style=budget_color,
    )

    terminal_total = terminals.get("total", 0)
    terminal_cc = terminals.get("claude_code", 0)
    terminal_panel = Panel(
        f"[bold]Terminals[/bold]\n{terminal_total} panes ({terminal_cc} Claude Code)",
        title="Tmux",
        border_style="blue",
    )

    teammates_data = data.get("teammates", {})
    teammate_panel = Panel(
        f"[bold]Teammates[/bold]\n"
        f"Active: [green]{teammates_data.get('active', 0)}[/green] | "
        f"Total: {teammates_data.get('total', 0)}",
        title="Swarm",
        border_style="yellow",
    )

    panels: list[Panel] = [session_panel, circuit_panel, drift_panel, budget_panel, terminal_panel, teammate_panel]
    if profile == "full":
        for name, widget in data.get("plugin_widgets", {}).items():
            panels.append(
                Panel(
                    widget.get("content", ""),
                    title=widget.get("title", name),
                    border_style=widget.get("border_style", "dim"),
                )
            )
        harness = data.get("harness_status")
        if harness:
            panels.append(
                Panel(
                    harness.get("message", str(harness)),
                    title="Harness",
                    border_style="yellow",
                )
            )
    return panels, data.get("summary", "")
