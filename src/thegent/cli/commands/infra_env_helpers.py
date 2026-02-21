"""Helpers for infra command .env updates."""

from __future__ import annotations

from pathlib import Path


def resolve_env_file(cwd: Path, module_file: Path) -> Path:
    """Resolve .env path from cwd or fallback project root relative to module file."""
    env_file = cwd / ".env"
    if env_file.exists():
        return env_file
    return module_file.parent.parent.parent / ".env"


def rewrite_max_concurrency_lines(env_lines: list[str], limit: int) -> tuple[list[str], bool]:
    """Rewrite/add THGENT_MAX_CONCURRENCY assignment."""
    updated = False
    new_lines: list[str] = []
    for line in env_lines:
        if line.strip().startswith("THGENT_MAX_CONCURRENCY="):
            new_lines.append(f"THGENT_MAX_CONCURRENCY={limit}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        if new_lines and not new_lines[-1].strip():
            new_lines.append(f"THGENT_MAX_CONCURRENCY={limit}")
        else:
            new_lines.append("")
            new_lines.append("# --- Concurrency ---")
            new_lines.append(f"THGENT_MAX_CONCURRENCY={limit}")
    return new_lines, updated
