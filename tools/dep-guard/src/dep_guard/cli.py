import click
from rich.console import Console
from dep_guard.resolver import DependencyResolver
from dep_guard.triage import TriageEngine
from dep_guard.agent import AgenticAnalyzer

console = Console()

@click.group()
def main():
    """Phenotype Dependency Guard - Malicious code detection in dependencies."""
    pass

@main.command()
@click.argument('path', type=click.Path(exists=True))
def scan(path):
    """Scan a project for malicious dependencies."""
    console.print(f"[bold blue]Scanning project at:[/bold blue] {path}")
    
    resolver = DependencyResolver(path)
    triage = TriageEngine()
    agent = AgenticAnalyzer()

    # 1. Dependency Resolution
    with console.status("[cyan]Resolving dependencies...[/cyan]"):
        deps = resolver.get_all_dependencies()
    console.print(f"Found [bold green]{len(deps)}[/bold green] dependencies.")

    # 2. Heuristic Triage
    findings_count = 0
    for dep in deps:
        # For simulation, we scan the project directory itself as if it were a dependency
        dep_path = path # Use current path for testing triage logic
        with console.status(f"[cyan]Triaging {dep['name']}...[/cyan]"):
            findings = triage.triage_dependency(dep_path)
        
        if findings:
            findings_count += len(findings)
            console.print(f"[bold yellow]Found {len(findings)} suspicious patterns in {dep['name']}[/bold yellow]")
            
            # 3. Agentic Deep Analysis for high severity
            high_severity = [f for f in findings if f['severity'] == 'high']
            if high_severity:
                with console.status(f"[bold red]Invoking Agentic Deep Dive for {dep['name']}...[/bold red]"):
                    analysis = agent.analyze_dependency(dep['name'], findings, dep_path)
                
                console.print(f"[bold red]Agent Analysis Result ({dep['name']}):[/bold red] {analysis['status']}")
                console.print(f"  [italic]Reasoning:[/italic] {analysis.get('reasoning')}")
                console.print(f"  [italic]Confidence:[/italic] {analysis.get('confidence')}")
                console.print(f"  [italic]Action:[/italic] {analysis.get('action')}")

    if findings_count == 0:
        console.print("[bold green]No suspicious patterns detected.[/bold green]")
    else:
        console.print(f"\n[bold red]Total findings: {findings_count}[/bold red]")

if __name__ == "__main__":
    main()
