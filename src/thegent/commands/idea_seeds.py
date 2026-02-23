"""Idea seed scanner: find and manage embedded improvement opportunities.

Scans codebases for embedded idea seeds — improvement opportunities, TODOs
with context, refactoring hints, and similar code-level annotations.

Provides:
- IdeaSeed dataclass representing a found seed with surrounding context
- IdeaSeedScanner for recursive directory and single-file scanning
- Export to markdown and WORK_STREAM.md compatible rows
- Typer CLI sub-application (registered under ``thegent seeds``)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer

try:
    import structlog

    _log: Any = structlog.get_logger(__name__)
except ModuleNotFoundError:
    _log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

SEED_PATTERNS: list[str] = [
    r"#\s*IDEA:\s*(.+)",
    r"#\s*SEED:\s*(.+)",
    r"#\s*REFACTOR:\s*(.+)",
    r"#\s*IMPROVE:\s*(.+)",
    r"#\s*FIXME:\s*(.+)",
    r"#\s*TODO:\s*(.+)",
    r"#\s*HACK:\s*(.+)",
    r"//\s*IDEA:\s*(.+)",  # JS / Rust / Go
    r"//\s*TODO:\s*(.+)",
]

# Map each pattern to the keyword it represents (used for pattern_type)
_PATTERN_KEYWORDS: list[str] = [
    "IDEA",
    "SEED",
    "REFACTOR",
    "IMPROVE",
    "FIXME",
    "TODO",
    "HACK",
    "IDEA",  # JS variant
    "TODO",  # JS variant
]

# Compiled pattern objects (index-matched to SEED_PATTERNS / _PATTERN_KEYWORDS)
_COMPILED: list[re.Pattern[str]] = [re.compile(p) for p in SEED_PATTERNS]

# Default file extensions to scan
DEFAULT_EXTENSIONS: list[str] = [
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".rs",
    ".go",
    ".sh",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
]

# Context lines to capture around each seed
_CONTEXT_LINES = 3


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class IdeaSeed:
    """A single idea seed found in source code.

    Attributes:
        file: Absolute path to the file containing the seed.
        line: 1-based line number of the seed.
        pattern_type: Keyword type (IDEA, TODO, REFACTOR, ...).
        content: The extracted seed text (capture group of the pattern).
        context: Surrounding code context (up to 3 lines before and after).
    """

    file: Path
    line: int
    pattern_type: str
    content: str
    context: str = field(default="")

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary."""
        return {
            "file": str(self.file),
            "line": self.line,
            "pattern_type": self.pattern_type,
            "content": self.content,
            "context": self.context,
        }


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


class IdeaSeedScanner:
    """Scan source files for embedded idea seeds.

    Args:
        context_lines: Number of surrounding lines to capture (default 3).
    """

    def __init__(self, context_lines: int = _CONTEXT_LINES) -> None:
        self._context_lines = context_lines

    # ------------------------------------------------------------------
    # Core scanning
    # ------------------------------------------------------------------

    def scan_file(self, path: Path) -> list[IdeaSeed]:
        """Scan a single file for idea seeds.

        Args:
            path: Path to the file to scan.

        Returns:
            Ordered list of IdeaSeed objects found in the file.
        """
        seeds: list[IdeaSeed] = []
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            _log.warning("idea_seed_scanner.read_error path=%s", str(path))
            return seeds

        lines = text.splitlines()
        for lineno, raw_line in enumerate(lines, start=1):
            for compiled, keyword in zip(_COMPILED, _PATTERN_KEYWORDS, strict=True):
                match = compiled.search(raw_line)
                if match:
                    content = match.group(1).strip()
                    context = self._extract_context(lines, lineno - 1)
                    seeds.append(
                        IdeaSeed(
                            file=path.resolve(),
                            line=lineno,
                            pattern_type=keyword,
                            content=content,
                            context=context,
                        )
                    )
                    break  # one match per line (first wins)
        return seeds

    def scan_directory(
        self,
        root: Path,
        extensions: list[str] | None = None,
    ) -> list[IdeaSeed]:
        """Recursively scan a directory for idea seeds.

        Args:
            root: Root directory to scan.
            extensions: File extensions to include (e.g. [".py", ".ts"]).
                        Defaults to DEFAULT_EXTENSIONS when None.

        Returns:
            Ordered list of IdeaSeed objects across all matched files.
        """
        exts = set(extensions) if extensions is not None else set(DEFAULT_EXTENSIONS)
        seeds: list[IdeaSeed] = []

        if not root.is_dir():
            _log.warning("idea_seed_scanner.not_a_directory path=%s", str(root))
            return seeds

        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix not in exts:
                continue
            # Skip hidden directories (e.g. .git, .venv)
            if any(part.startswith(".") for part in path.parts):
                continue
            seeds.extend(self.scan_file(path))

        return seeds

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_by_type(
        self,
        seeds: list[IdeaSeed],
        types: list[str],
    ) -> list[IdeaSeed]:
        """Keep only seeds whose pattern_type is in *types*.

        Args:
            seeds: Input seed list.
            types: Pattern type strings to keep (case-insensitive).

        Returns:
            Filtered seed list.
        """
        upper_types = {t.upper() for t in types}
        return [s for s in seeds if s.pattern_type.upper() in upper_types]

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def to_work_stream_items(self, seeds: list[IdeaSeed]) -> list[dict[str, str]]:
        """Convert seeds to WORK_STREAM.md-compatible row dictionaries.

        Each row has keys: id, title, source, priority, depends.

        Args:
            seeds: List of IdeaSeed objects.

        Returns:
            List of dicts ready to be serialised as WORK_STREAM table rows.
        """
        rows: list[dict[str, str]] = []
        for seed in seeds:
            slug = _make_slug(seed.content)
            row_id = f"seed-{seed.pattern_type.lower()}-{slug}"
            title = f"[{seed.pattern_type}] {seed.content[:80]}"
            source_ref = f"{seed.file.name}:{seed.line}"
            rows.append(
                {
                    "id": row_id,
                    "title": title,
                    "source": source_ref,
                    "priority": _priority_for_type(seed.pattern_type),
                    "depends": "-",
                }
            )
        return rows

    def export_markdown(self, seeds: list[IdeaSeed], output: Path) -> None:
        """Export seeds to a markdown file grouped by pattern type.

        Args:
            seeds: Seeds to export.
            output: Destination file path (created / overwritten).
        """
        output.parent.mkdir(parents=True, exist_ok=True)
        md_lines: list[str] = [
            "# Idea Seeds",
            "",
            "> Auto-generated by `thegent seeds export`. Do not edit manually.",
            "",
        ]

        # Group by pattern_type preserving insertion order
        groups: dict[str, list[IdeaSeed]] = {}
        for seed in seeds:
            groups.setdefault(seed.pattern_type, []).append(seed)

        for ptype, group in sorted(groups.items()):
            md_lines += [f"## {ptype}", ""]
            for seed in group:
                rel = _try_relative(seed.file)
                md_lines += [
                    f"### `{rel}:{seed.line}`",
                    "",
                    f"**{seed.content}**",
                    "",
                ]
                if seed.context.strip():
                    md_lines += [
                        "```",
                        seed.context,
                        "```",
                        "",
                    ]

        output.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _extract_context(self, lines: list[str], zero_idx: int) -> str:
        """Return surrounding lines joined as a single string.

        Args:
            lines: All lines of the file (0-indexed).
            zero_idx: Index of the matching line (0-based).

        Returns:
            Joined context string.
        """
        start = max(0, zero_idx - self._context_lines)
        end = min(len(lines), zero_idx + self._context_lines + 1)
        return "\n".join(lines[start:end])


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _make_slug(text: str, max_len: int = 40) -> str:
    """Turn a seed content string into a short URL-safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len].rstrip("-")


def _priority_for_type(pattern_type: str) -> str:
    """Return a default WORK_STREAM priority for a given pattern type."""
    mapping: dict[str, str] = {
        "FIXME": "P1",
        "HACK": "P1",
        "REFACTOR": "P2",
        "IMPROVE": "P2",
        "TODO": "P2",
        "IDEA": "P3",
        "SEED": "P3",
    }
    return mapping.get(pattern_type.upper(), "P3")


def _try_relative(path: Path) -> Path:
    """Return path relative to cwd, falling back to absolute."""
    try:
        return path.relative_to(Path.cwd())
    except ValueError:
        return path


# ---------------------------------------------------------------------------
# CLI (Typer sub-app)
# ---------------------------------------------------------------------------

app = typer.Typer(help="Find and manage embedded idea seeds in source code.")


@app.command("scan")
def seeds_scan(
    directory: Path = typer.Argument(
        Path(),
        help="Directory to scan (default: current working directory).",
    ),
    types: str = typer.Option(
        "",
        "--types",
        "-t",
        help="Comma-separated pattern types to show (e.g. TODO,FIXME). Empty = all.",
    ),
    extensions: str = typer.Option(
        "",
        "--ext",
        "-e",
        help="Comma-separated file extensions to scan (e.g. .py,.ts). Empty = defaults.",
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        help="Output raw JSON instead of rich table.",
    ),
) -> None:
    """Scan a directory for embedded idea seeds and display results."""
    import json
    import sys

    from rich.console import Console
    from rich.table import Table

    console = Console()
    scanner = IdeaSeedScanner()
    ext_list: list[str] | None = [e.strip() for e in extensions.split(",") if e.strip()] or None
    seeds = scanner.scan_directory(directory.resolve(), extensions=ext_list)

    type_list = [t.strip().upper() for t in types.split(",") if t.strip()]
    if type_list:
        seeds = scanner.filter_by_type(seeds, type_list)

    if output_json:
        sys.stdout.write(json.dumps([s.to_dict().decode().decode() for s in seeds], indent=2) + "\n")
        return

    if not seeds:
        console.print("[dim]No idea seeds found.[/dim]")
        return

    table = Table(title=f"Idea Seeds — {directory}", show_lines=True)
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("File:Line", style="yellow")
    table.add_column("Content", style="white")

    for seed in seeds:
        rel = _try_relative(seed.file)
        table.add_row(
            seed.pattern_type,
            f"{rel}:{seed.line}",
            seed.content[:100],
        )

    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {len(seeds)} seed(s) found.")


@app.command("export")
def seeds_export(
    directory: Path = typer.Argument(
        Path(),
        help="Directory to scan.",
    ),
    output: Path = typer.Option(
        Path("seeds.md"),
        "--output",
        "-o",
        help="Output markdown file path.",
    ),
    types: str = typer.Option(
        "",
        "--types",
        "-t",
        help="Comma-separated pattern types to export. Empty = all.",
    ),
    extensions: str = typer.Option(
        "",
        "--ext",
        "-e",
        help="Comma-separated file extensions to scan. Empty = defaults.",
    ),
) -> None:
    """Export found idea seeds to a markdown file."""
    from rich.console import Console

    console = Console()
    scanner = IdeaSeedScanner()
    ext_list: list[str] | None = [e.strip() for e in extensions.split(",") if e.strip()] or None
    seeds = scanner.scan_directory(directory.resolve(), extensions=ext_list)

    type_list = [t.strip().upper() for t in types.split(",") if t.strip()]
    if type_list:
        seeds = scanner.filter_by_type(seeds, type_list)

    scanner.export_markdown(seeds, output.resolve())
    console.print(f"[green]Exported {len(seeds)} seed(s) to {output}[/green]")


@app.command("add-to-workstream")
def seeds_add_to_workstream(
    directory: Path = typer.Argument(
        Path(),
        help="Directory to scan.",
    ),
    workstream: Path = typer.Option(
        Path("docs/reference/WORK_STREAM.md"),
        "--workstream",
        "-w",
        help="Path to WORK_STREAM.md.",
    ),
    types: str = typer.Option(
        "",
        "--types",
        "-t",
        help="Comma-separated pattern types to include. Empty = all.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be added without modifying the file.",
    ),
) -> None:
    """Append unclaimed idea seeds as BACKLOG items in WORK_STREAM.md."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    scanner = IdeaSeedScanner()
    seeds = scanner.scan_directory(directory.resolve())

    type_list = [t.strip().upper() for t in types.split(",") if t.strip()]
    if type_list:
        seeds = scanner.filter_by_type(seeds, type_list)

    rows = scanner.to_work_stream_items(seeds)

    if not rows:
        console.print("[dim]No seeds to add.[/dim]")
        return

    if dry_run:
        table = Table(title="Would add to WORK_STREAM.md (dry run)", show_lines=True)
        table.add_column("ID")
        table.add_column("Title")
        table.add_column("Source")
        table.add_column("Priority")
        for row in rows:
            table.add_row(row["id"], row["title"], row["source"], row["priority"])
        console.print(table)
        return

    ws_path = workstream.resolve()
    if not ws_path.exists():
        console.print(f"[red]WORK_STREAM.md not found at {ws_path}[/red]")
        raise typer.Exit(1)

    existing = ws_path.read_text(encoding="utf-8")
    new_lines: list[str] = []
    for row in rows:
        row_md = f"| {row['id']} | {row['title']} | {row['source']} | {row['priority']} | {row['depends']} |"
        if row["id"] not in existing:
            new_lines.append(row_md)

    if not new_lines:
        console.print("[dim]All seeds already present in WORK_STREAM.md.[/dim]")
        return

    # Append after the BACKLOG header separator row
    backlog_marker = "| ID | Title | Source | Priority | Depends |"
    separator = "|----|-------|--------|----------|---------|"
    if backlog_marker in existing:
        insert_after = separator if separator in existing else backlog_marker
        updated = existing.replace(
            insert_after,
            insert_after + "\n" + "\n".join(new_lines),
            1,
        )
        ws_path.write_text(updated, encoding="utf-8")
        console.print(f"[green]Added {len(new_lines)} seed(s) to {ws_path}[/green]")
    else:
        console.print("[yellow]Could not locate BACKLOG table header; appending at end.[/yellow]")
        with ws_path.open("a", encoding="utf-8") as fh:
            fh.write("\n" + "\n".join(new_lines) + "\n")
        console.print(f"[green]Appended {len(new_lines)} seed(s) to {ws_path}[/green]")
