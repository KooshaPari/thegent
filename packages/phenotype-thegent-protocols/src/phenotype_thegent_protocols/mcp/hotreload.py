"""Production hot-reload supervisor for MCP + proxy.

Watches project source/config files and triggers a process-compose restart
when relevant files change.
"""

from __future__ import annotations

import time
from pathlib import Path

from rich.console import Console

from phenotype_thegent_protocols.mcp.manage import mcp_restart

console = Console()

_IGNORE_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".thegent"}
_RELOAD_SUFFIXES = {".py", ".yaml", ".yml", ".json", ".toml"}
_RELOAD_BASENAMES = {"process-compose.yaml", "pyproject.toml"}


def _default_watch_paths(project_root: Path) -> list[Path]:
    candidates = [
        project_root / "src" / "thegent",
        project_root / "scripts",
        project_root / "process-compose.yaml",
        project_root / "pyproject.toml",
    ]
    return [path for path in candidates if path.exists()]


def _is_relevant_change(path: Path) -> bool:
    if any(part in _IGNORE_PARTS for part in path.parts):
        return False
    return path.suffix in _RELOAD_SUFFIXES or path.name in _RELOAD_BASENAMES


def run_prod_hotreload(project_root: Path | None = None, debounce_s: float = 1.5) -> None:
    """Run a blocking watch loop and restart MCP stack on relevant changes."""
    if debounce_s <= 0:
        raise ValueError("debounce_s must be > 0")

    try:
        from watchfiles import watch
    except ImportError as exc:
        raise RuntimeError("watchfiles is required for production hot-reload") from exc

    root = (project_root or Path.cwd()).expanduser().resolve()
    watch_paths = _default_watch_paths(root)
    if not watch_paths:
        raise RuntimeError(f"No watch paths found under {root}")

    console.print(f"[cyan]Hot-reload watching:[/cyan] {', '.join(str(p) for p in watch_paths)}")
    console.print("[dim]Press Ctrl+C to stop.[/dim]")

    last_restart = 0.0
    for changes in watch(*watch_paths, recursive=True):
        relevant = sorted(
            {Path(changed_path) for _, changed_path in changes if _is_relevant_change(Path(changed_path))}
        )
        if not relevant:
            continue

        now = time.monotonic()
        if now - last_restart < debounce_s:
            continue

        last_restart = now
        console.print(f"[yellow]Hot-reload restart triggered by {len(relevant)} file(s).[/yellow]")
        ok, message = mcp_restart()
        if not ok:
            raise RuntimeError(f"Hot-reload restart failed: {message}")
        console.print(f"[green]{message}[/green]")
