"""Helios CLI - Unified command line interface"""

import os
import asyncio
import httpx
import typer
from typing import Optional
from pathlib import Path
from rich.console import Console

console = Console()

CLIPROXY_URL = os.environ.get("CLIPROXY_URL", "http://localhost:8317")
HARNESS = os.environ.get("HARNESS", "cliproxy")


app = typer.Typer(
    name="helios",
    help="Helios Harness - Unified Benchmark Execution",
    add_completion=False,
)


@app.command()
def version():
    """Show version"""
    console.print(f"Helios CLI version: 0.1.0")


@app.command()
def run(
    dataset: str = typer.Option(..., "-d", "--dataset", help="Dataset to run"),
    agent: str = typer.Option(..., "-a", "--agent", help="Agent to use"),
    environment: str = typer.Option("docker", "-e", "--env", help="Environment type"),
    parallel: int = typer.Option(1, "-p", "--parallel", help="Parallel tasks"),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """Run a benchmark"""
    console.print(f"[bold]Running benchmark[/bold]")
    console.print(f"  Dataset: {dataset}")
    console.print(f"  Agent: {agent}")
    console.print(f"  Environment: {environment}")
    console.print(f"  Parallel: {parallel}")
    console.print(f"  Harness: {HARNESS}")
    console.print(f"  Cliproxy: {CLIPROXY_URL}")
    
    # TODO: Implement actual benchmark execution
    console.print("[yellow]Not yet implemented - requires helios-core integration[/yellow]")


@app.command()
def task(
    prompt: str = typer.Option(..., "-p", "--prompt", help="Task prompt"),
    model: str = typer.Option("minimax-m2.5", "-m", "--model", help="Model to use"),
    max_tokens: int = typer.Option(100, "-t", "--max-tokens", help="Max tokens"),
):
    """Execute a task via cliproxy"""
    console.print(f"[bold]Executing task via {HARNESS}[/bold]")
    console.print(f"  Model: {model}")
    console.print(f"  Prompt: {prompt[:50]}...")
    
    async def execute():
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                start = asyncio.get_event_loop().time()
                r = await client.post(
                    f"{CLIPROXY_URL}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                    }
                )
                elapsed = (asyncio.get_event_loop().time() - start) * 1000
                
                if r.status_code == 200:
                    data = r.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    console.print(f"[green]Success[/green] ({elapsed:.0f}ms)")
                    console.print(f"  Response: {content[:100]}...")
                else:
                    console.print(f"[red]Error: {r.status_code}[/red]")
                    console.print(f"  {r.text[:200]}")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(execute())


@app.command()
def run(
    dataset: str = typer.Option(..., "-d", "--dataset", help="Dataset to run"),
    agent: str = typer.Option(..., "-a", "--agent", help="Agent to use"),
    environment: str = typer.Option("docker", "-e", "--env", help="Environment type"),
    parallel: int = typer.Option(1, "-p", "--parallel", help="Parallel tasks"),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """Run a benchmark"""
    console.print(f"[bold]Running benchmark[/bold]")
    console.print(f"  Dataset: {dataset}")
    console.print(f"  Agent: {agent}")
    console.print(f"  Environment: {environment}")
    console.print(f"  Parallel: {parallel}")
    
    # TODO: Implement actual benchmark execution
    console.print("[yellow]Not yet implemented - requires helios-core integration[/yellow]")


@app.command()
def eval(
    results: Path = typer.Argument(..., help="Results directory"),
    format: str = typer.Option("auto", "-f", "--format", help="Format"),
):
    """Evaluate results"""
    console.print(f"[bold]Evaluating results from: {results}[/bold]")
    # TODO: Implement evaluation
    console.print("[yellow]Not yet implemented[/yellow]")


@app.command()
def analyze(
    results: Path = typer.Argument(..., help="Results directory"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file"),
    format: str = typer.Option("report", "-f", "--format", help="Output format"),
):
    """Analyze results"""
    console.print(f"[bold]Analyzing results from: {results}[/bold]")
    # TODO: Implement analysis
    console.print("[yellow]Not yet implemented[/yellow]")


@app.command()
def config(
    action: str = typer.Argument(..., help="Action: get, set, list"),
    key: Optional[str] = typer.Option(None, help="Config key"),
    value: Optional[str] = typer.Option(None, help="Config value"),
):
    """Manage configuration"""
    if action == "list":
        console.print("[bold]Current configuration:[/bold]")
        console.print("  registry_url: https://registry.helios.ai")
        console.print("  storage_path: ~/.helios/storage")
    elif action == "get" and key:
        console.print(f"  {key}: <value>")
    elif action == "set" and key and value:
        console.print(f"  Set {key} = {value}")
    else:
        console.print("[red]Usage: helios config <get|set|list> [key] [value][/red]")


@app.command()
def registry(
    action: str = typer.Argument(..., help="Action: list, search, download"),
    query: Optional[str] = typer.Option(None, help="Search query"),
):
    """Manage registry"""
    if action == "list":
        console.print("[bold]Available benchmarks:[/bold]")
        console.print("  terminal-bench@2.0")
        console.print("  swe-bench")
        console.print("  live-code-bench")
    elif action == "search" and query:
        console.print(f"[bold]Searching for: {query}[/bold]")
        # TODO: Implement search
    else:
        console.print("[red]Usage: helios registry <list|search> [query][/red]")


if __name__ == "__main__":
    app()
