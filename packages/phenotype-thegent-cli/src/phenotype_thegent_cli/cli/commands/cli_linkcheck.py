"""CLI command for link checking."""

import logging
from pathlib import Path

import typer

from phenotype_thegent_core.utils.link_checker import LinkChecker

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command("check")
def check_links(
    path: str = typer.Argument(".", help="Path to check (file or directory)"),
    pattern: str = typer.Option("**/*.md", "--pattern", "-p", help="File pattern to match"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Check links in markdown files."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    checker = LinkChecker()

    path_obj = Path(path)
    if path_obj.is_file():
        results = checker.check_file(path_obj)
        console.print(f"[bold]Checking {path}[/bold]")
    else:
        summary = checker.check_directory(path_obj, pattern)
        results = summary["results"]
        console.print(f"[bold]Checking directory {path}[/bold]")
        console.print(f"Total links: {summary['total_links']}")
        console.print(f"Broken links: {summary['broken_links']}")
        console.print(f"External links: {summary['external_links']}")

    if results:
        table = Table(show_header=True, header_style="bold")
        table.add_column("File", style="cyan")
        table.add_column("Line", style="yellow")
        table.add_column("Link", style="green")
        table.add_column("Status", style="magenta")
        table.add_column("Valid", style="red")

        for result in results:
            if "line" in result:
                table.add_row(
                    str(result.get("file", "")),
                    str(result["line"]),
                    result["url"],
                    result.get("status", "unknown"),
                    "✓" if result.get("valid") else "✗" if result.get("valid") is False else "?",
                )

        console.print(table)
    else:
        console.print("[yellow]No links found[/yellow]")


if __name__ == "__main__":
    app()
