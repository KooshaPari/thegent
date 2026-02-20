"""
Document Queue CLI Commands for thegent

Integrates document queue management into thegent's typer-based CLI.
Uses centralized path utilities for cross-platform consistency.
"""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from thegent.agents.document import (
    DocumentAnalyzer,
    DocumentProcessor,
    MarkdownScanner,
    ProcessingPipeline,
    QueueManager,
    ScanConfig,
)
from thegent.agents.document.processor import (
    compute_file_hash,
    count_lines,
    extract_metadata,
)

# Import path utilities for normalized path handling
try:
    from scripts.path_utils import normalize_path, safe_join
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
    from path_utils import normalize_path, safe_join

console = Console()

# Default queue file location using normalized paths
DEFAULT_QUEUE_FILE = safe_join(normalize_path("~/.thegent"), "scans", "MARKDOWN_SCAN_QUEUE.json")

# Create typer app for document queue commands
doc_queue_app = typer.Typer(name="doc-queue", help="Document queue management commands")


@doc_queue_app.command("scan")
def scan_cmd(
    config: Path | None = typer.Option(None, "--config", "-c", help="Config file path"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    min_date: str | None = typer.Option(None, "--min-date", help="Minimum date (YYYY-MM)"),
    location: str | None = typer.Option(None, "--location", help="Location config (name:path:recursive:max_depth)"),
):
    """Scan for markdown files and create queue."""
    if config and config.exists():
        with open(config) as f:
            config_data = json.load(f)
        scan_config = ScanConfig(
            locations=config_data.get("locations", {}),
            exclude_patterns=set(config_data.get("exclude_patterns", [])),
            min_date=min_date or config_data.get("min_date"),
            # Use normalize_path for output_dir
            output_dir=normalize_path(config_data.get("output_dir", "~/.thegent/scans")),
        )
    else:
        # Use default or command-line location
        locations = {}
        if location:
            parts = location.split(":")
            if len(parts) >= 2:
                name = parts[0]
                path = parts[1]
                recursive = parts[2].lower() == "true" if len(parts) > 2 else True
                max_depth = int(parts[3]) if len(parts) > 3 and parts[3] else None
                # Use normalize_path for user-provided location paths
                locations[name] = {
                    "path": normalize_path(path),
                    "recursive": recursive,
                    "max_depth": max_depth,
                }

        if not locations:
            # Default locations using normalized paths
            locations = {
                "kush": {"path": safe_join(normalize_path("~"), "kush"), "recursive": True},
                "temp-PRODVERCEL": {"path": safe_join(normalize_path("~"), "temp-PRODVERCEL"), "recursive": True},
            }

        scan_config = ScanConfig(
            locations=locations,
            min_date=min_date,
        )

    console.print("[bold cyan]Scanning for markdown files...[/bold cyan]")
    scanner = MarkdownScanner(scan_config)
    scanner.scan()

    output_path = output.expanduser() if output else None
    result_path = scanner.save_results(output_path)

    summary = scanner.get_summary()
    console.print("\n[bold green]Scan complete![/bold green]")
    console.print(f"Total files: [cyan]{summary['total_files']}[/cyan]")
    console.print(f"Months: [cyan]{summary['months']}[/cyan]")
    console.print(f"Results saved to: [yellow]{result_path}[/yellow]")


@doc_queue_app.command("list")
def list_cmd(
    queue_file: Path | None = typer.Option(None, "--queue-file", "-q", help="Queue file path"),
):
    """List all months in the queue."""
    if queue_file:
        queue_manager = QueueManager(queue_file.expanduser())
    else:
        queue_file_path = DEFAULT_QUEUE_FILE
        if not queue_file_path.exists():
            from thegent.errors import print_error

            print_error(f"Queue file not found: {queue_file_path}")
            raise typer.Exit(1)
        queue_manager = QueueManager(queue_file_path)

    months = queue_manager.list_months()
    table = Table(title="Document Queue - Months")
    table.add_column("Month", style="bold cyan")
    table.add_column("Total Files", style="green")
    table.add_column("Locations", style="yellow")

    for month_entry in months:
        month = month_entry["month"]
        total = month_entry["total_files"]
        locations = ", ".join([f"{loc['location']}({loc['file_count']})" for loc in month_entry["locations"]])
        table.add_row(month, str(total), locations)

    console.print(table)


@doc_queue_app.command("next")
def next_cmd(
    queue_file: Path | None = typer.Option(None, "--queue-file", "-q", help="Queue file path"),
    files: bool = typer.Option(False, "--files", help="Show file list"),
):
    """Get next month to process."""
    if queue_file:
        queue_manager = QueueManager(queue_file.expanduser())
    else:
        queue_file_path = DEFAULT_QUEUE_FILE
        if not queue_file_path.exists():
            from thegent.errors import print_error

            print_error(f"Queue file not found: {queue_file_path}")
            raise typer.Exit(1)
        queue_manager = QueueManager(queue_file_path)

    next_month = queue_manager.get_next_month()
    if next_month:
        console.print(f"[bold]Next month:[/bold] [cyan]{next_month['month']}[/cyan]")
        console.print(f"Total files: [green]{next_month['total_files']}[/green]")

        if files:
            for loc_entry in next_month["locations"]:
                console.print(
                    f"\n[bold yellow][{loc_entry['location']}][/bold yellow] ({loc_entry['file_count']} files):"
                )
                for filepath in loc_entry["files"][:10]:
                    console.print(f"  {filepath}")
                if loc_entry["file_count"] > 10:
                    console.print(f"  ... and [dim]{loc_entry['file_count'] - 10} more[/dim]")
    else:
        console.print("[yellow]No more months to process![/yellow]")


@doc_queue_app.command("files")
def files_cmd(
    month: str = typer.Argument(..., help="Month (YYYY-MM)"),
    location: str | None = typer.Option(None, "--location", help="Filter by location"),
    queue_file: Path | None = typer.Option(None, "--queue-file", "-q", help="Queue file path"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Get files for a specific month."""
    if queue_file:
        queue_manager = QueueManager(queue_file.expanduser())
    else:
        queue_file_path = DEFAULT_QUEUE_FILE
        if not queue_file_path.exists():
            from thegent.errors import print_error

            print_error(f"Queue file not found: {queue_file_path}")
            raise typer.Exit(1)
        queue_manager = QueueManager(queue_file_path)

    files = queue_manager.get_month_files(month, location)

    if output:
        with open(output.expanduser(), "w") as f:
            f.writelines(f"{filepath}\n" for filepath in files)
        console.print(f"[green]Wrote {len(files)} files to {output}[/green]")
    else:
        for filepath in files:
            console.print(filepath)


@doc_queue_app.command("summary")
def summary_cmd(
    queue_file: Path | None = typer.Option(None, "--queue-file", "-q", help="Queue file path"),
):
    """Get queue summary statistics."""
    if queue_file:
        queue_manager = QueueManager(queue_file.expanduser())
    else:
        queue_file_path = DEFAULT_QUEUE_FILE
        if not queue_file_path.exists():
            from thegent.errors import print_error

            print_error(f"Queue file not found: {queue_file_path}")
            raise typer.Exit(1)
        queue_manager = QueueManager(queue_file_path)

    summary_data = queue_manager.get_summary()

    table = Table(title="Queue Summary")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="cyan")

    table.add_row("Total files", str(summary_data["total_files"]))
    table.add_row("Total months", str(summary_data["total_months"]))
    table.add_row("Processed", f"[green]{summary_data['processed']}[/green]")
    table.add_row("Skipped", f"[yellow]{summary_data['skipped']}[/yellow]")
    table.add_row("Failed", f"[red]{summary_data['failed']}[/red]")
    table.add_row("Remaining", f"[cyan]{summary_data['remaining']}[/cyan]")

    if summary_data["last_processed_month"]:
        table.add_row("Last processed month", summary_data["last_processed_month"])
        if summary_data["last_processed_location"]:
            table.add_row("Last processed location", summary_data["last_processed_location"])

    console.print(table)


@doc_queue_app.command("process")
def process_cmd(
    filepath: Path = typer.Argument(..., help="File to process"),
    queue_file: Path | None = typer.Option(None, "--queue-file", "-q", help="Queue file path"),
    analyze: bool = typer.Option(False, "--analyze", help="Also analyze the document"),
):
    """Process a single file."""
    path = filepath.expanduser()
    if not path.exists():
        from thegent.errors import print_error

        print_error(f"File not found: {filepath}")
        raise typer.Exit(1)

    # Create processing pipeline
    pipeline = ProcessingPipeline()
    pipeline.add_stage(extract_metadata)
    pipeline.add_stage(compute_file_hash)
    pipeline.add_stage(count_lines)

    processor = DocumentProcessor(pipeline)
    console.print(f"[cyan]Processing:[/cyan] {filepath}")
    result = processor.process_file(str(path))

    if result.status.value == "completed":
        console.print("[green]✓ Processed successfully[/green]")
        console.print(f"  Processing time: [dim]{result.processing_time:.2f}s[/dim]")
        if result.metadata:
            console.print(f"  Metadata: {json.dumps(result.metadata, indent=2)}")

        # Mark as processed in queue
        if queue_file:
            queue_manager = QueueManager(queue_file.expanduser())
            queue_manager.mark_file_processed(str(path))
    else:
        console.print("[red]✗ Failed[/red]")
        if result.error:
            console.print(f"  Error: [red]{result.error}[/red]")

    if analyze:
        analyzer = DocumentAnalyzer()
        analysis = analyzer.analyze(path)
        console.print("\n[bold]Analysis:[/bold]")
        console.print(f"  Category: [cyan]{analysis.category.value}[/cyan]")
        console.print(f"  Word count: [green]{analysis.word_count}[/green]")
        console.print(f"  Estimated reading time: [yellow]{analysis.estimated_reading_time:.1f} minutes[/yellow]")
        console.print(f"  Sections: [cyan]{analysis.section_count}[/cyan]")


@doc_queue_app.command("analyze")
def analyze_cmd(
    filepath: Path = typer.Argument(..., help="File to analyze"),
):
    """Analyze a document."""
    path = filepath.expanduser()
    if not path.exists():
        from thegent.errors import print_error

        print_error(f"File not found: {filepath}")
        raise typer.Exit(1)

    analyzer = DocumentAnalyzer()
    console.print(f"[cyan]Analyzing:[/cyan] {filepath}")
    analysis = analyzer.analyze(path)

    table = Table(title=f"Analysis: {filepath.name}")
    table.add_column("Property", style="bold")
    table.add_column("Value", style="cyan")

    table.add_row("Category", analysis.category.value)
    table.add_row("Word count", str(analysis.word_count))
    table.add_row("Estimated reading time", f"{analysis.estimated_reading_time:.1f} minutes")
    table.add_row("Sections", str(analysis.section_count))
    table.add_row("Has code blocks", "✓" if analysis.has_code_blocks else "✗")
    table.add_row("Has images", "✓" if analysis.has_images else "✗")
    table.add_row("Has links", "✓" if analysis.has_links else "✗")
    if analysis.keywords:
        table.add_row("Keywords", ", ".join(list(analysis.keywords)[:10]))

    console.print(table)
