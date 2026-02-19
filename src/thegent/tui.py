from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from thegent.cli_impl import ps_impl
from thegent.tools.terminal import is_claude_code_pane, list_tmux_panes

console = Console()


def run_explorer_tui():
    """Simple TUI to explore and take over sessions."""
    with Live(render_explorer(), refresh_per_second=1, screen=True) as live:
        # This is a bit limited since we can't easily handle input in this environment
        # without a full TUI library like textual, but we can show the state.
        import time

        try:
            while True:
                live.update(render_explorer())
                time.sleep(1)
        except KeyboardInterrupt:
            pass


def render_explorer() -> Layout:
    layout = Layout()
    layout.split_column(Layout(name="header", size=3), Layout(name="main"), Layout(name="footer", size=3))

    # Header
    layout["header"].update(Panel("[bold cyan]thegent Terminal Explorer[/bold cyan]", border_style="blue"))

    # Main content - split into Terminals, Background Sessions, and Discovered
    layout["main"].split_column(Layout(name="top"), Layout(name="bottom"))
    layout["top"].split_row(Layout(name="terminals"), Layout(name="sessions"))
    layout["bottom"].split_row(Layout(name="discovered"))

    # Terminals (tmux)
    term_table = Table(title="Active Terminals (tmux)", expand=True)
    term_table.add_column("ID", style="cyan")
    term_table.add_column("Session", style="green")
    term_table.add_column("Path", style="yellow")
    term_table.add_column("Type")

    panes = list_tmux_panes()
    for p in panes:
        is_cc = is_claude_code_pane(p)
        type_str = "[bold blue]Claude Code[/bold blue]" if is_cc else "Shell"
        term_table.add_row(p.pane_id, p.session_name, p.path, type_str)

    layout["terminals"].update(Panel(term_table, border_style="cyan"))

    # Sessions (thegent bg)
    sess_table = Table(title="thegent Background Sessions", expand=True)
    sess_table.add_column("ID", style="cyan")
    sess_table.add_column("Agent", style="magenta")
    sess_table.add_column("Status")

    sessions = ps_impl(all=False)  # Only active ones
    for s in sessions:
        status = s.get("status", "unknown")
        color = "green" if status == "running" else "yellow"
        sess_table.add_row(s.get("id", "—")[:8], s.get("agent", "—"), f"[{color}]{status}[/{color}]")

    layout["sessions"].update(Panel(sess_table, border_style="magenta"))

    # Discovered Agents (sharecli)
    disc_table = Table(title="Discovered Agents (via sharecli)", expand=True)
    disc_table.add_column("PPID", style="cyan")
    disc_table.add_column("Agent", style="magenta")
    disc_table.add_column("CWD", style="yellow")
    disc_table.add_column("Last Command", style="dim")
    disc_table.add_column("Tmux Pane", style="green")

    from thegent.discovery import list_discovered_agents

    discovered = list_discovered_agents()
    for d in discovered:
        cmd_preview = f"{d.get('command', '')} {d.get('args_preview', '')}".strip()
        disc_table.add_row(
            str(d.get("ppid")),
            d.get("agent", "?"),
            d.get("cwd", "—"),
            cmd_preview[:40] + ("..." if len(cmd_preview) > 40 else ""),
            d.get("tmux_pane", "—"),
        )

    layout["discovered"].update(Panel(disc_table, border_style="green"))

    # Footer
    layout["footer"].update(
        Panel("[dim]Ctrl+C to exit | Use 'thegent takeover <id|pane|ppid>' to attach[/dim]", border_style="blue")
    )

    return layout
