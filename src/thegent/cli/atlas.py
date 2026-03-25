"""Atlas CLI commands for thegent."""
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(help="Codebase atlas generation and visualization")

ATLAS_DIR = ".atlas"


@app.command()
def generate(
    repo: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    format: str = typer.Option("all", "--format", "-f", help="Output format: all, json, markdown"),
):
    """Generate codebase atlas for repository."""
    import subprocess
    import sys

    script_path = Path(__file__).parent.parent.parent / "scripts" / "generate_codebase_atlas.sh"

    if not script_path.exists():
        typer.echo(f"[ERROR] Atlas script not found: {script_path}", err=True)
        raise typer.Exit(1)

    cmd = ["bash", str(script_path)]
    if quiet:
        cmd.append("--quiet")

    result = subprocess.run(cmd, cwd=repo)
    if result.returncode != 0:
        typer.echo("[ERROR] Atlas generation failed", err=True)
        raise typer.Exit(result.returncode)

    if not quiet:
        typer.echo("[SUCCESS] Atlas generated at .atlas/")


@app.command()
def view(
    atlas_type: Optional[str] = typer.Argument(
        None, help="Atlas type: readme, file, folder, tech, feature, user"
    ),
    repo: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
):
    """View generated atlas files."""
    import webbrowser

    atlas_dir = repo / ATLAS_DIR

    if not atlas_dir.exists():
        typer.echo(f"[ERROR] Atlas not found. Run 'thegent atlas generate' first.", err=True)
        raise typer.Exit(1)

    files = {
        "readme": "README.md",
        "file": "file_tree.md",
        "folder": "folder_tree.md",
        "tech": "tech_tree.md",
        "technology": "tech_tree.md",
        "feature": "feature_tree.md",
        "user": "user_tree.md",
    }

    if atlas_type is None:
        atlas_type = "readme"

    atlas_type = atlas_type.lower()

    if atlas_type not in files:
        typer.echo(f"[ERROR] Unknown atlas type: {atlas_type}", err=True)
        typer.echo("Available types: " + ", ".join(files.keys()))
        raise typer.Exit(1)

    file_path = atlas_dir / files[atlas_type]

    if not file_path.exists():
        typer.echo(f"[ERROR] Atlas file not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Print to console
    typer.echo(file_path.read_text())


@app.command()
def install_hooks(
    repo: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
):
    """Install git hooks for auto-atlas generation."""
    import subprocess
    import sys

    script_path = Path(__file__).parent.parent.parent / "scripts" / "install_hooks.sh"

    if not script_path.exists():
        typer.echo(f"[ERROR] Install script not found: {script_path}", err=True)
        raise typer.Exit(1)

    # Make executable
    script_path.chmod(0o755)

    result = subprocess.run(
        ["bash", str(script_path), str(repo / ".git" / "hooks")],
        cwd=repo,
    )

    if result.returncode != 0:
        typer.echo("[ERROR] Hook installation failed", err=True)
        raise typer.Exit(result.returncode)

    typer.echo("[SUCCESS] Git hooks installed!")


@app.command()
def stats(
    repo: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
):
    """Show quick statistics from atlas."""
    import json

    atlas_dir = repo / ATLAS_DIR

    if not atlas_dir.exists():
        typer.echo(f"[ERROR] Atlas not found. Run 'thegent atlas generate' first.", err=True)
        raise typer.Exit(1)

    stats_file = atlas_dir / "stats.json"

    if not stats_file.exists():
        typer.echo(f"[ERROR] Stats file not found: {stats_file}", err=True)
        raise typer.Exit(1)

    stats = json.loads(stats_file.read_text())

    if format == "json":
        typer.echo(json.dumps(stats, indent=2))
    else:
        typer.echo("\n📊 Codebase Statistics\n")
        typer.echo(f"  Total LOC:     {stats.get('total_loc', 0):,}")
        typer.echo(f"  Total Files:   {stats.get('total_files', 0):,}")
        typer.echo(f"  Languages:     {stats.get('total_languages', 0)}")

        languages = stats.get("by_language", {})
        if languages:
            typer.echo("\n  Top Languages:")
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            for lang, loc in sorted_langs:
                typer.echo(f"    - {lang}: {loc:,} LOC")


@app.command()
def serve(
    port: int = typer.Option(8080, "--port", "-p", help="Port to serve on"),
    repo: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
):
    """Start an interactive web server for the atlas."""
    import http.server
    import threading
    import webbrowser

    atlas_dir = repo / ATLAS_DIR

    if not atlas_dir.exists():
        typer.echo(f"[ERROR] Atlas not found. Run 'thegent atlas generate' first.", err=True)
        raise typer.Exit(1)

    # Create simple HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    handler.directory = str(atlas_dir)

    with http.server.HTTPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/README.md"
        typer.echo(f"🌐 Serving atlas at {url}")
        typer.echo("Press Ctrl+C to stop")

        # Open browser
        webbrowser.open(url)

        # Serve
        httpd.serve_forever()


if __name__ == "__main__":
    app()
