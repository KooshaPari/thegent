"""First-class project tenancy commands: sys setup project and install project.

# @trace FR-TEN-001
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, cast

import typer
from rich.console import Console
from rich.table import Table
from thegent.install_constants import VALID_TARGETS

console = Console()

# ---------------------------------------------------------------------------
# Sub-typer: thegent sys setup project <subcommand>
# ---------------------------------------------------------------------------

setup_project_app = typer.Typer(
    help="Register and manage projects with first-class tenant isolation.",
    no_args_is_help=True,
)

# ---------------------------------------------------------------------------
# Sub-typer: thegent install project
# ---------------------------------------------------------------------------

install_project_app = typer.Typer(
    help="Install Thegent runtime assets into a registered project directory.",
    no_args_is_help=True,
)


install_app = typer.Typer(
    help="Install user/system assets and project runtime assets.",
)
install_app.add_typer(install_project_app, name="project", help="Install Thegent runtime assets into a project.")


scaffold_app = typer.Typer(
    help="Project scaffolding: greenfield bootstrap and brownfield migration.",
    no_args_is_help=True,
)


def _normalize_install_target(raw_target: str) -> str:
    """Normalize legacy install target aliases."""
    return (raw_target or "all").strip().lower()


def _normalize_install_scope(raw_scope: str) -> str:
    """Normalize user/system install scope argument."""
    scope = (raw_scope or "user").strip().lower()
    if scope not in {"user", "system", "both"}:
        raise ValueError(f"Invalid scope: {scope!r}. Valid values: user, system, both")
    return scope


@install_app.callback(invoke_without_command=True)
def install_callback(
    ctx: typer.Context,
    target: str = typer.Option(
        "all",
        "--target",
        "-t",
        help="User-scope install target: all, codex, droid, cursor, harness, shell, etc. or system.",
    ),
    mode: str = typer.Option(
        "smart",
        "--mode",
        "-m",
        help="Install mode: smart, overwrite, skip, undo",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without writing files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print detailed install output"),
    url: str | None = typer.Option(None, "--url", help="MCP URL override"),
    install_service: bool = typer.Option(False, "--install-service", help="Install service hooks where supported"),
    system: bool = typer.Option(False, "--system", help="Install system-wide assets under /opt/thegent"),
    system_prefix: str | None = typer.Option(None, "--system-prefix", help="System install prefix (default: /opt/thegent)"),
    scope: str = typer.Option("user", "--scope", help="Install scope: user, system, or both."),
    setup: bool = typer.Option(False, "--setup", help="Run the setup wizard after install."),
) -> None:
    """Install user/system runtime assets and optionally launch the setup wizard."""
    if ctx.invoked_subcommand is not None:
        return

    try:
        from thegent.install import run_install, run_install_system
    except ImportError as exc:
        console.print(f"[red]Install subsystem unavailable: {exc}[/red]")
        raise typer.Exit(1) from exc

    selected_target = _normalize_install_target(target)
    try:
        selected_scope = _normalize_install_scope(scope)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if system:
        selected_scope = "system" if selected_scope == "user" else "both"

    if selected_target == "system":
        selected_target = "all"

    if selected_scope == "both":
        if selected_target == "user":
            selected_target = "all"
        if selected_target not in VALID_TARGETS:
            console.print(f"[red]Invalid target: {selected_target!r}. Run with --target all or a valid target.")
            raise typer.Exit(1)

        both_result = run_install(
            target=selected_target,
            mode=mode,
            dry_run=dry_run,
            verbose=verbose,
            url=url,
            install_service=install_service,
        )
        if both_result.get("errors"):
            raise typer.Exit(1)

    elif selected_scope == "user":
        if selected_target == "user":
            selected_target = "all"
        if selected_target == "both":
            selected_target = "all"
        if selected_target not in VALID_TARGETS:
            console.print(f"[red]Invalid target: {selected_target!r}. Run with --target all or a valid target.")
            raise typer.Exit(1)

        run_install_result = run_install(
            target=selected_target,
            mode=mode,
            dry_run=dry_run,
            verbose=verbose,
            url=url,
            install_service=install_service,
        )

        if run_install_result.get("errors"):
            raise typer.Exit(1)

    if selected_scope in {"system", "both"}:
        from pathlib import Path as _Path

        prefix = _Path(system_prefix or "/opt/thegent")
        system_result = run_install_system(prefix=prefix, dry_run=dry_run, verbose=verbose)
        if system_result.get("errors"):
            raise typer.Exit(1)

    if setup:
        from thegent.cli.commands.model_cmds import setup_cmd

        setup_cmd(wizard=True)


@scaffold_app.command("greenfield", help="Create a new project from initialize-project presets.")
def scaffold_greenfield(
    destination: Annotated[str | None, typer.Argument(help="Destination directory for generated project scaffold")] = None,
    profile: Annotated[str, typer.Option("--profile", "-p", help="Preset profile name")] = "cli_tool",
    name: Annotated[str, typer.Option("--name", help="Project name (defaults to destination name)")] = "",
    description: Annotated[str, typer.Option("--description", "-d", help="Project description")] = "",
    language: Annotated[str, typer.Option("--language", "-l", help="Primary language")] = "python",
    register: Annotated[bool, typer.Option("--register", help="Register scaffolded project tenancy")] = False,
    install_runtime: Annotated[
        bool,
        typer.Option(
            "--install-runtime",
            help="Install Thegent runtime assets after scaffold (requires --register, skipped for --dry-run)",
        ),
    ] = False,
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override (with --register)")] = "",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview scaffold payload without running Copier")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Top-level greenfield alias for `thegent sys setup project scaffold`."""
    if not destination:
        console.print("[yellow]Usage: thegent project greenfield <destination>[/yellow]")
        return
    project_scaffold(
        destination=destination,
        profile=profile,
        name=name,
        description=description,
        language=language,
        register=register,
        install_runtime=install_runtime,
        tenant=tenant,
        dry_run=dry_run,
        json_output=json_output,
    )


@scaffold_app.command("brownfield", help="Adopt an existing project into the Thegent tenant/runtime model.")
def scaffold_brownfield(
    project: Annotated[str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (defaults to directory name).")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override.")] = "",
    template: Annotated[
        str,
        typer.Option(
            "--template",
            help="Template adoption mode: auto|ag-dd|none (default auto). auto infers from existing metadata.",
        ),
    ] = "auto",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry template metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Top-level brownfield alias for `thegent sys setup project migrate`."""
    if not project:
        console.print("[yellow]Usage: thegent project brownfield <project>[/yellow]")
        return
    project_migrate(
        project=project,
        name=name,
        tenant=tenant,
        template=template,
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )


@scaffold_app.command("ag-dd", help="Brownfield alias to migrate an existing project as AG-DD template mode.")
def scaffold_brownfield_agdd(
    project: Annotated[
        str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")
    ] = None,
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Project name (defaults to directory name)."),
    ] = "",
    tenant: Annotated[
        str,
        typer.Option("--tenant", "-t", help="Tenant ID override."),
    ] = "",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Brownfield variant that fixes template mode to AG-DD."""
    if not project:
        console.print("[yellow]Usage: thegent project ag-dd <project>[/yellow]")
        return
    scaffold_brownfield(
        project=project,
        name=name,
        tenant=tenant,
        template="ag-dd",
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )


@scaffold_app.command("none", help="Brownfield alias to migrate an existing project without template overlay.")
def scaffold_brownfield_none(
    project: Annotated[
        str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")
    ] = None,
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Project name (defaults to directory name)."),
    ] = "",
    tenant: Annotated[
        str,
        typer.Option("--tenant", "-t", help="Tenant ID override."),
    ] = "",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Brownfield variant that fixes template mode to none."""
    if not project:
        console.print("[yellow]Usage: thegent project none <project>[/yellow]")
        return
    scaffold_brownfield(
        project=project,
        name=name,
        tenant=tenant,
        template="none",
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )


@setup_project_app.command("brownfield", help="Top-level brownfield migration alias for project setup workflows.")
def setup_project_brownfield(
    project: Annotated[str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (defaults to directory name).")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override.")] = "",
    template: Annotated[
        str,
        typer.Option(
            "--template",
            help="Template adoption mode: auto|ag-dd|none (default auto). auto infers from existing metadata.",
        ),
    ] = "auto",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Top-level brownfield alias for `thegent setup project migrate`."""
    if not project:
        console.print("[yellow]Usage: thegent sys setup project brownfield <project>[/yellow]")
        return
    project_migrate(
        project=project,
        name=name,
        tenant=tenant,
        template=template,
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )


@setup_project_app.command("greenfield", help="Top-level greenfield scaffold alias for project setup workflows.")
def setup_project_greenfield(
    destination: Annotated[
        str | None, typer.Argument(help="Destination directory for generated project scaffold")
    ] = None,
    profile: Annotated[
        str,
        typer.Option(
            "--profile",
            help="Preset profile: cli_tool|service_api|event_worker|web_app|library_sdk",
        ),
    ] = "service_api",
    name: Annotated[str, typer.Option("--name", help="Project name (defaults to destination name)")] = "",
    description: Annotated[str, typer.Option("--description", "-d", help="Project description")] = "",
    language: Annotated[str, typer.Option("--language", "-l", help="Primary language")] = "python",
    register: Annotated[bool, typer.Option("--register", help="Register scaffolded project tenancy")] = False,
    install_runtime: Annotated[
        bool,
        typer.Option(
            "--install-runtime",
            help="Install Thegent runtime assets after scaffold (requires --register, skipped for --dry-run)",
        ),
    ] = False,
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override (with --register)")] = "",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview scaffold payload without running Copier")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Top-level greenfield alias for `thegent setup project scaffold`."""
    if not destination:
        console.print("[yellow]Usage: thegent sys setup project greenfield <destination>[/yellow]")
        return
    project_scaffold(
        destination=destination,
        profile=profile,
        name=name,
        description=description,
        language=language,
        register=register,
        install_runtime=install_runtime,
        tenant=tenant,
        dry_run=dry_run,
        json_output=json_output,
    )


@setup_project_app.command("ag-dd", help="Top-level brownfield variant forcing AG-DD template mode.")
def setup_project_brownfield_agdd(
    project: Annotated[
        str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")
    ] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (defaults to directory name).")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override.")] = "",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Top-level brownfield variant that fixes template mode to AG-DD."""
    if not project:
        console.print("[yellow]Usage: thegent sys setup project ag-dd <project>[/yellow]")
        return
    setup_project_brownfield(
        project=project,
        name=name,
        tenant=tenant,
        template="ag-dd",
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )


@setup_project_app.command("none", help="Top-level brownfield variant forcing no template overlay.")
def setup_project_brownfield_none(
    project: Annotated[
        str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")
    ] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (defaults to directory name).")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override.")] = "",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Top-level brownfield variant that fixes template mode to none."""
    if not project:
        console.print("[yellow]Usage: thegent sys setup project none <project>[/yellow]")
        return
    setup_project_brownfield(
        project=project,
        name=name,
        tenant=tenant,
        template="none",
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slug(name: str) -> str:
    """Convert a project name to a safe tenant_id slug."""
    return "".join(c if (c.isalnum() or c in "-_") else "-" for c in name.lower()).strip("-")



_SCAFFOLD_PROFILES: dict[str, dict[str, object]] = {
    "cli_tool": {
        "project_type": "cli_tool",
        "runtime_profile": "balanced",
        "governance_mode": "standard",
        "observability_stack": "minimal_logs",
        "interfaces": ["cli", "docs"],
        "deployment_target": "local_only",
        "quality_profile": "strict",
        "questionnaire_summary_hints": ["primary_user_flow", "biggest_risk"],
    },
    "service_api": {
        "project_type": "service_api",
        "runtime_profile": "low_latency",
        "governance_mode": "standard",
        "observability_stack": "otel_prometheus",
        "interfaces": ["http_api", "docs"],
        "deployment_target": "container_platform",
        "quality_profile": "strict",
        "questionnaire_summary_hints": ["primary_user_flow", "biggest_risk", "rollback_plan"],
    },
    "event_worker": {
        "project_type": "event_worker",
        "runtime_profile": "throughput",
        "governance_mode": "strict",
        "observability_stack": "otel_prometheus",
        "interfaces": ["events", "docs"],
        "deployment_target": "serverless",
        "quality_profile": "critical",
        "questionnaire_summary_hints": ["biggest_risk", "rollback_plan", "cost_guardrails"],
    },
    "web_app": {
        "project_type": "web_app",
        "runtime_profile": "low_latency",
        "governance_mode": "standard",
        "observability_stack": "sentry_first",
        "interfaces": ["web_ui", "http_api", "docs"],
        "deployment_target": "edge",
        "quality_profile": "strict",
        "questionnaire_summary_hints": ["primary_user_flow", "biggest_risk", "onboarding"],
    },
    "library_sdk": {
        "project_type": "library_sdk",
        "runtime_profile": "cost_optimized",
        "governance_mode": "strict",
        "observability_stack": "minimal_logs",
        "interfaces": ["sdk", "docs"],
        "deployment_target": "package_registry",
        "quality_profile": "critical",
        "questionnaire_summary_hints": ["primary_user_flow", "onboarding", "rollback_plan"],
    },
}


_DEFAULT_TEMPLATE_VERSION = "1.0.0"


def _build_scaffold_data(profile: str, name: str, description: str, language: str) -> dict[str, object]:
    """Return Copier data-file payload for a scaffold preset profile."""
    if profile not in _SCAFFOLD_PROFILES:
        valid = ", ".join(sorted(_SCAFFOLD_PROFILES))
        raise ValueError(f"Unknown scaffold profile: {profile}. Valid: {valid}")
    profile_defaults = _SCAFFOLD_PROFILES[profile]
    return {
        "project_name": name,
        "project_description": description,
        "language": language,
        "author": "thegent",
        "include_docs": True,
        "include_ci": True,
        "include_hooks": True,
        **profile_defaults,
    }


def _read_templates_lock_state(project_path: Path) -> tuple[str, str] | None:
    """Read existing ``.thegent/templates.lock`` metadata if present and valid."""
    lock_path = project_path / ".thegent" / "templates.lock"
    if not lock_path.exists():
        return None
    raw = lock_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid templates.lock format (expected object): {lock_path}")
    template = data.get("template")
    version = data.get("version")
    if not isinstance(template, str) or not template:
        return None
    if not isinstance(version, str):
        version = _DEFAULT_TEMPLATE_VERSION
    return template.strip(), version.strip() or _DEFAULT_TEMPLATE_VERSION


def _agents_md_looks_thematic(path: Path) -> bool:
    """Conservative AGENTS.md marker check used only when lock markers are absent."""
    agents_md = path / "AGENTS.md"
    if not agents_md.exists():
        return False
    try:
        text = agents_md.read_text(encoding="utf-8").lower()
    except OSError:
        return False
    return "thegent" in text and "migration" in text


def _resolve_migration_template(
    requested_template: str,
    project_path: Path,
    fallback_template: str | None = None,
    *,
    ignore_lock_errors: bool = False,
) -> str:
    """Resolve requested template mode for migration flow."""
    requested = requested_template.strip().lower()
    if requested == "auto":
        try:
            lock_state = _read_templates_lock_state(project_path)
        except ValueError:
            if ignore_lock_errors:
                return fallback_template or "none"
            raise
        if lock_state:
            return lock_state[0]

        thegent_dir = project_path / ".thegent"
        existing_markers = [
            thegent_dir / "config.yaml",
            thegent_dir / "ownership.json",
            thegent_dir / "templates.lock",
        ]
        if _agents_md_looks_thematic(project_path):
            existing_markers.append(project_path / "AGENTS.md")
        if any(marker.exists() for marker in existing_markers):
            return "ag-dd"
        return fallback_template or "none"

    if requested in {"ag-dd", "none"}:
        return requested

    raise ValueError("template must be one of: auto, ag-dd, none")


def _resolve_migration_mode(requested_mode: str) -> str:
    """Validate migration install mode."""
    mode = requested_mode.strip().lower()
    if mode not in {"smart", "overwrite", "skip"}:
        raise ValueError("mode must be one of: smart, overwrite, skip")
    return mode


def _project_migrate_snapshot(project_path: Path) -> dict[str, object]:
    """Collect lightweight project state for migration diagnostics."""
    thegent_dir = project_path / ".thegent"
    return {
        "project_path": str(project_path),
        "exists": project_path.exists(),
        "is_dir": project_path.is_dir(),
        "has_git": (project_path / ".git").is_dir(),
        "has_thegent_dir": thegent_dir.is_dir(),
        "has_thegent_config": (thegent_dir / "config.yaml").exists(),
        "has_ownership": (thegent_dir / "ownership.json").exists(),
        "has_templates_lock": (thegent_dir / "templates.lock").exists(),
        "has_agdd_agents_md": (project_path / "AGENTS.md").exists(),
    }


def _scaffold_profile_names() -> list[str]:
    """Sorted list of supported scaffold presets."""
    return sorted(_SCAFFOLD_PROFILES)


@setup_project_app.command("migrate", help="Convert or reconcile an existing repo into the thegent tenant/runtime model.")
def project_migrate(
    project: Annotated[str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (defaults to directory name).")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override.")] = "",
    template: Annotated[
        str,
        typer.Option(
            "--template",
            help="Template adoption mode: auto|ag-dd|none (default auto). auto infers from existing metadata.",
        ),
    ] = "auto",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry template metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Migrate a brownfield/new partial project and align it with registry and runtime assets."""
    if not project:
        console.print("[yellow]Usage: thegent project migrate <project>[/yellow]")
        return
    import thegent.infra.project_tenancy as pt_module

    project_path = Path(project).expanduser().resolve()
    if not project_path.exists() or not project_path.is_dir():
        console.print(f"[red]Error: project path is not a directory: {project_path}[/red]")
        raise typer.Exit(1)

    try:
        resolved_mode = _resolve_migration_mode(mode)
        resolved_template = _resolve_migration_template(template, project_path, ignore_lock_errors=True)
    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise typer.Exit(1) from exc

    tenancy = pt_module._DEFAULT_TENANCY
    existing = tenancy.get_project(path=project_path)
    warnings: list[str] = []

    try:
        lock_state = _read_templates_lock_state(project_path)
    except ValueError as exc:
        warnings.append(f"templates.lock parse warning: {exc}")
        lock_state = None
    detected_template = lock_state[0] if lock_state else resolved_template
    if existing:
        template_version = existing.template_version
        if template == "auto" and existing.template != "none":
            resolved_template = existing.template
        elif template == "auto":
            if detected_template in {"ag-dd", "none"}:
                resolved_template = detected_template
    else:
        template_version = lock_state[1] if lock_state else _DEFAULT_TEMPLATE_VERSION

    reconcile_updates: dict[str, str] = {}
    if existing and template == "auto":
        if existing.template == "none" and detected_template != existing.template:
            reconcile_updates["template"] = detected_template
        elif existing.template != "ag-dd" and detected_template == "ag-dd":
            reconcile_updates["template"] = detected_template
        if lock_state and lock_state[1] != existing.template_version:
            reconcile_updates["template_version"] = lock_state[1]
        if existing.name == project_path.name and name and name != existing.name:
            reconcile_updates["name"] = name.strip()
        if existing.tenant_id == _slug(project_path.name) and tenant and tenant.strip() != existing.tenant_id:
            reconcile_updates["tenant_id"] = tenant.strip()
    else:
        if existing and lock_state and lock_state[1] != existing.template_version:
            reconcile_updates["template_version"] = lock_state[1]
        if template != "auto" and template != existing.template:
            reconcile_updates["template"] = template

    registration: dict[str, object] = {}
    if existing is None:
        if not register:
            console.print(
                f"[red]Error: project is not registered. Use --register to adopt this brownfield project[/red]",
            )
            raise typer.Exit(1)
        project_name = name.strip() or project_path.name
        tenant_id = tenant.strip() or _slug(project_name)
        if dry_run:
            conflict = False
            try:
                name_record = tenancy.get_project(name=project_name)
            except ValueError as exc:
                warnings.append(f"Conflict on name: {exc}")
                name_record = None
                conflict = True
            if name_record is not None and name_record.path != str(project_path):
                warnings.append(f"Conflict on name: {name_record.path}")
                conflict = True
            try:
                tenant_record = tenancy.get_project(tenant_id=tenant_id)
            except ValueError as exc:
                warnings.append(f"Conflict on tenant: {exc}")
                tenant_record = None
                conflict = True
            if tenant_record is not None:
                warnings.append(f"Conflict on tenant: {tenant_record.tenant_id}")
                conflict = True
            if conflict:
                for warning in warnings:
                    console.print(f"[yellow]Warning:[/yellow] {warning}")
                raise typer.Exit(1)
            registration.update(
                {
                    "status": "adopted (dry-run)",
                    "project_id": "pending",
                    "tenant_id": tenant_id,
                    "name": project_name,
                },
            )
            existing = None
        else:
            try:
                record = tenancy.init_project(
                    name=project_name,
                    tenant_id=tenant_id,
                    path=project_path,
                    template=resolved_template,
                    template_version=template_version,
                )
            except Exception as exc:
                console.print(f"[red]Error: cannot register project: {exc}[/red]")
                raise typer.Exit(1) from exc
            existing = record
            registration.update(
                {
                    "status": "adopted",
                    "project_id": record.project_id,
                    "tenant_id": record.tenant_id,
                    "name": record.name,
                },
            )
    else:
        if name and name != existing.name:
            console.print(
                f"[yellow]Info: project name {name!r} differs from registry name {existing.name!r}; keeping registry record[/yellow]"
            )
        if tenant and tenant.strip() != existing.tenant_id:
            console.print(
                f"[yellow]Info: tenant override {tenant!r} differs from registry tenant {existing.tenant_id!r}; keeping registry record[/yellow]"
            )
        registration.update(
            {
                "status": "already_registered",
                "project_id": existing.project_id,
                "tenant_id": existing.tenant_id,
                "name": existing.name,
            },
        )
        if reconcile_updates:
            if dry_run:
                registration["planned_reconcile"] = True
                registration["reconcile_changes"] = reconcile_updates
            elif reconcile:
                try:
                    existing = tenancy.sync_project(path=project_path, **reconcile_updates)
                except Exception as exc:
                    console.print(f"[red]Error: cannot reconcile existing project: {exc}[/red]")
                    raise typer.Exit(1) from exc
                registration.update(
                    {
                        "status": "reconciled",
                        "project_id": existing.project_id,
                        "tenant_id": existing.tenant_id,
                        "name": existing.name,
                    }
                )
                warnings.append("Registry metadata reconciled from detected project state.")

    runtime_result: dict[str, object] = {
        "project_selector": str(project_path),
        "template": resolved_template,
        "mode": resolved_mode,
        "installed": [],
        "skipped": [],
        "errors": [],
        "status": "not_run",
    }
    if install_runtime and not (dry_run and existing is None):
        from thegent.install import run_install_project

        try:
            runtime_result = run_install_project(
                project_selector=str(project_path),
                template=resolved_template,
                mode=resolved_mode,
                dry_run=dry_run,
                registry_path=tenancy._registry_path,  # noqa: SLF001
            )
            runtime_result["status"] = "applied" if not dry_run else "dry_run"
        except Exception as exc:
            console.print(f"[red]Error: runtime migration failed: {exc}[/red]")
            raise typer.Exit(1) from exc
    elif install_runtime and dry_run and existing is None:
        runtime_result["status"] = "deferred"
        runtime_result["notes"] = ["Dry-run for unregistered project: runtime install is planned after registration."]

    snapshot = _project_migrate_snapshot(project_path)
    snapshot["detected_template"] = detected_template
    snapshot["target_template"] = resolved_template
    snapshot["mode"] = resolved_mode
    snapshot["registry_template"] = existing.template if existing else resolved_template
    snapshot["template_version"] = template_version
    snapshot["warnings"] = warnings
    snapshot["lock_state"] = "valid" if lock_state else ("invalid" if warnings else "absent")

    if json_output:
        payload = {
            "project": {
                "name": existing.name if existing else name.strip() or project_path.name,
                "tenant_id": existing.tenant_id if existing else (tenant.strip() or _slug(name.strip() or project_path.name)),
                "path": str(project_path),
                "registered": existing is not None,
            },
            "registration": registration,
            "runtime": runtime_result,
            "snapshot": snapshot,
        }
        typer.echo(json.dumps(payload, indent=2))
        raise typer.Exit(0 if not runtime_result.get("errors") else 1)

    baseline_label = (
        "adopted"
        if registration.get("status") in {"adopted", "adopted (dry-run)"}
        else "reconciled"
    )
    console.print(f"[green]Migration baseline: {baseline_label}[/green]")
    console.print(f"  path: {project_path}")
    if existing:
        console.print(f"  project: {existing.name}")
        console.print(f"  tenant : {existing.tenant_id}")
        console.print(f"  template: {existing.template} (v{existing.template_version})")
    else:
        console.print(f"  project: {name or project_path.name}")
        console.print(f"  tenant: {tenant or _slug(name or project_path.name)}")
    console.print(f"  detected_template: {detected_template}")
    console.print(f"  target_template: {resolved_template}")
    console.print(f"  mode: {resolved_mode}")
    console.print(f"  install_runtime: {install_runtime}")
    if registration.get("status") == "adopted (dry-run)":
        console.print("[yellow]Dry-run mode: project registration is planned but not persisted.[/yellow]")
    if warnings:
        for warning in warnings:
            console.print(f"[yellow]Warning:[/yellow] {warning}")
    if install_runtime and runtime_result:
        installed = list(cast(Iterable[object], runtime_result.get("installed", [])))
        skipped = list(cast(Iterable[object], runtime_result.get("skipped", [])))
        errors = list(cast(Iterable[object], runtime_result.get("errors", [])))
        for note in cast(Iterable[object], runtime_result.get("notes", [])):
            console.print(f"  [yellow]runtime note:[/yellow] {note}")
        if dry_run:
            console.print("[yellow]Dry-run mode for runtime migration enabled[/yellow]")
        if installed:
            console.print(f"  runtime: installed {len(installed)} file(s)")
        if skipped:
            console.print(f"  runtime: skipped {len(skipped)} file(s)")
        if errors:
            for err in errors:
                console.print(f"  [red]runtime error:[/red] {err}")
    if not snapshot["has_thegent_dir"]:
        console.print("[yellow]Tip: .thegent dir missing before migration; runtime install will create it when --install-runtime is enabled.[/yellow]")

    if runtime_result.get("errors"):
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# sys setup project init
# ---------------------------------------------------------------------------


@setup_project_app.command("init", help="Register a project and create its tenant root.")
def project_init(
    name: Annotated[str, typer.Option("--name", "-n", help="Logical project name")] = "",
    path: Annotated[str, typer.Option("--path", "-p", help="Project path (default: cwd)")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID (default: slug(name))")] = "",
    template: Annotated[str, typer.Option("--template", help="Scaffold template: ag-dd or none")] = "none",
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Register project in the tenancy registry and create tenant root directory."""
    import thegent.infra.project_tenancy as pt_module

    if not name:
        console.print("[red]Error: --name is required[/red]")
        raise typer.Exit(1)

    effective_path = Path(path).expanduser().resolve() if path else Path.cwd()
    effective_tenant = tenant.strip() or _slug(name)  # noqa: FURB110 - intentional fallback

    if not effective_path.exists():
        console.print(f"[red]Error: project path does not exist: {effective_path}[/red]")
        raise typer.Exit(1)

    # Ensure tenant root under ~/.thegent/tenants/<tenant_id>/
    tenant_root = Path.home() / ".thegent" / "tenants" / effective_tenant
    tenant_root.mkdir(parents=True, exist_ok=True)

    tenancy = pt_module._DEFAULT_TENANCY
    record = tenancy.init_project(
        name=name,
        tenant_id=effective_tenant,
        path=effective_path,
        template=template if template != "none" else "none",
    )

    if template == "ag-dd":
        result = tenancy.spawn_template_agdd(effective_path, mode="smart")
        installed_count = len(result.installed)
        skipped_count = len(result.skipped) + len(result.unchanged)
    else:
        installed_count = 0
        skipped_count = 0

    if json_output:
        payload: dict[str, str | int] = {
            "project_id": record.project_id,
            "name": record.name,
            "tenant_id": record.tenant_id,
            "path": record.path,
            "template": record.template,
            "created_at": record.created_at,
        }
        if template == "ag-dd":
            payload["template_files_installed"] = installed_count
            payload["template_files_skipped"] = skipped_count
        typer.echo(json.dumps(payload, indent=2))
        return

    console.print(f"[green]Project registered:[/green] {record.name}")
    console.print(f"  project_id : {record.project_id}")
    console.print(f"  tenant_id  : {record.tenant_id}")
    console.print(f"  path       : {record.path}")
    console.print(f"  tenant_root: {tenant_root}")
    console.print(f"  template   : {record.template}")
    if template == "ag-dd":
        console.print(f"  [dim]AG-DD files installed: {installed_count}, skipped: {skipped_count}[/dim]")


@setup_project_app.command("scaffold", help="Bootstrap a new project from initialize-project presets.")
def project_scaffold(
    destination: Annotated[
        str | None, typer.Argument(help="Destination directory for generated project scaffold")
    ] = None,
    profile: Annotated[
        str,
        typer.Option(
            "--profile",
            help="Preset profile: cli_tool|service_api|event_worker|web_app|library_sdk",
        ),
    ] = "service_api",
    name: Annotated[str, typer.Option("--name", "-n", help="Project name override")] = "",
    description: Annotated[str, typer.Option("--description", "-d", help="Project description")] = "",
    language: Annotated[str, typer.Option("--language", "-l", help="Primary language")] = "python",
    register: Annotated[bool, typer.Option("--register", help="Register scaffolded project tenancy")] = False,
    install_runtime: Annotated[
        bool,
        typer.Option(
            "--install-runtime",
            help="Install Thegent runtime assets after scaffold (requires --register, skipped for --dry-run)",
        ),
    ] = False,
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override (with --register)")] = "",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview scaffold payload without running Copier")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Run Copier with a curated profile preset and deterministic defaults."""
    if destination is None:
        console.print("[yellow]Usage: thegent project scaffold <destination>[/yellow]")
        return
    dest_path = Path(destination).expanduser().resolve()
    if dest_path.exists() and any(dest_path.iterdir()):
        console.print(f"[red]Error: destination is not empty: {dest_path}[/red]")
        raise typer.Exit(1)
    if not dry_run and not dest_path.exists():
        dest_path.mkdir(parents=True, exist_ok=True)

    project_name = name.strip() or dest_path.name
    project_description = description.strip() or f"Generated {profile} project scaffold"

    try:
        data = _build_scaffold_data(
            profile=profile,
            name=project_name,
            description=project_description,
            language=language,
        )
    except ValueError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise typer.Exit(1) from exc

    if install_runtime and not register and not dry_run:
        console.print("[red]Error: --install-runtime requires --register (unless --dry-run)[/red]")
        raise typer.Exit(1)

    template_dir = Path(__file__).resolve().parents[4] / "templates" / "initialize-project"
    if not template_dir.exists():
        console.print(f"[red]Error: initialize-project template not found: {template_dir}[/red]")
        raise typer.Exit(1)

    cmd = []
    if not dry_run:
        with tempfile.TemporaryDirectory(prefix="thegent-scaffold-") as td:
            data_file = Path(td) / "copier-data.json"
            data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            cmd = [
                "uvx",
                "copier",
                "copy",
                "--defaults",
                "--data-file",
                str(data_file),
                str(template_dir),
                str(dest_path),
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as exc:
                console.print(f"[red]Error: scaffold command failed with exit code {exc.returncode}[/red]")
                raise typer.Exit(exc.returncode) from exc

    registered_project_id = ""
    effective_tenant = ""
    registry_path: Path | None = None
    if register and not dry_run:
        import thegent.infra.project_tenancy as pt_module

        effective_tenant = tenant.strip() or _slug(project_name)
        record = pt_module._DEFAULT_TENANCY.init_project(
            name=project_name,
            tenant_id=effective_tenant,
            path=dest_path,
            template="none",
        )
        registered_project_id = record.project_id
        registry_path = pt_module._DEFAULT_TENANCY._registry_path

    install_runtime_applied = False
    install_runtime_status = "not_requested"
    install_runtime_result: dict[str, list[str] | str | list[dict[str, str]]] = {}
    if install_runtime:
        if dry_run:
            install_runtime_status = "skipped_dry_run"
        else:
            from thegent.install import run_install_project

            try:
                install_runtime_result = run_install_project(
                    project_selector=str(dest_path),
                    template="none",
                    mode="smart",
                    dry_run=False,
                    registry_path=registry_path,
                )
            except Exception as exc:
                console.print(f"[red]Error: runtime install failed: {exc}[/red]")
                raise typer.Exit(1) from exc

            install_runtime_applied = True
            install_runtime_status = "applied"
            if install_runtime_result.get("errors"):
                console.print("[red]Error: runtime install reported errors[/red]")
                raise typer.Exit(1)

    payload = {
        "destination": str(dest_path),
        "profile": profile,
        "project_name": project_name,
        "language": language,
        "dry_run": dry_run,
        "register": register,
        "tenant_id": effective_tenant,
        "project_id": registered_project_id,
        "template": str(template_dir),
        "copier_data": data,
        "copier_cmd": cmd,
        "install_runtime_requested": install_runtime,
        "install_runtime_applied": install_runtime_applied,
        "install_runtime_status": install_runtime_status,
        "install_runtime_result": install_runtime_result,
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2))
        return

    if dry_run:
        console.print("[yellow]Scaffold dry-run complete (no files written)[/yellow]")
    else:
        console.print("[green]Scaffold generated[/green]")
    console.print(f"  destination : {payload['destination']}")
    console.print(f"  profile     : {payload['profile']}")
    console.print(f"  name        : {payload['project_name']}")
    console.print(f"  language    : {payload['language']}")
    if register and not dry_run:
        console.print(f"  project_id  : {registered_project_id}")
        console.print(f"  tenant_id   : {effective_tenant}")
    if install_runtime_status == "applied":
        installed_count = len(install_runtime_result.get("installed", []))
        skipped_count = len(install_runtime_result.get("skipped", []))
        console.print(f"  runtime     : installed ({installed_count} installed, {skipped_count} skipped)")
    elif install_runtime_status == "skipped_dry_run":
        console.print("  runtime     : skipped (dry-run)")


@setup_project_app.command("scaffold-profiles", help="List available scaffold preset profiles.")
def project_scaffold_profiles(
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Show all scaffold presets and their project_type target."""
    profile_names = _scaffold_profile_names()
    if json_output:
        typer.echo(json.dumps(profile_names, indent=2))
        return

    table = Table(title="Scaffold Preset Profiles")
    table.add_column("Profile", style="cyan")
    table.add_column("Project Type", style="green")
    table.add_column("Deployment", style="dim")
    table.add_column("Quality", style="yellow")

    for profile in profile_names:
        spec = _SCAFFOLD_PROFILES[profile]
        table.add_row(
            profile,
            str(spec["project_type"]),
            str(spec["deployment_target"]),
            str(spec["quality_profile"]),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# sys setup project list
# ---------------------------------------------------------------------------


@setup_project_app.command("list", help="List all registered projects.")
def project_list(
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Display all projects in the tenancy registry."""
    import thegent.infra.project_tenancy as pt_module

    tenancy = pt_module._DEFAULT_TENANCY
    projects = tenancy.list_projects()

    if json_output:
        payload = [
            {
                "project_id": p.project_id,
                "name": p.name,
                "tenant_id": p.tenant_id,
                "path": p.path,
                "template": p.template,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            for p in projects
        ]
        typer.echo(json.dumps(payload, indent=2))
        return

    if not projects:
        console.print("[dim]No projects registered.[/dim]")
        return

    table = Table(title="Registered Projects")
    table.add_column("Name", style="cyan")
    table.add_column("Tenant ID", style="green")
    table.add_column("Path", style="dim")
    table.add_column("Template", style="yellow")
    table.add_column("Created", style="dim")

    for p in projects:
        table.add_row(
            p.name,
            p.tenant_id,
            p.path,
            p.template,
            p.created_at[:19],  # trim microseconds
        )

    console.print(table)


# ---------------------------------------------------------------------------
# sys setup project show
# ---------------------------------------------------------------------------


@setup_project_app.command("show", help="Show detailed info for a specific project.")
def project_show(
    name: Annotated[str, typer.Argument(help="Project name (or tenant_id)")],
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Show detailed view of one project including tenancy paths and registry linkage."""
    import thegent.infra.project_tenancy as pt_module

    tenancy = pt_module._DEFAULT_TENANCY

    # Try lookup by name first, then by tenant_id
    record = tenancy.get_project(name=name)
    if record is None:
        record = tenancy.get_project(tenant_id=name)
    if record is None:
        console.print(f"[red]Error: project not found: {name!r}[/red]")
        raise typer.Exit(1)

    tenant_root = Path.home() / ".thegent" / "tenants" / record.tenant_id

    if json_output:
        payload = {
            "project_id": record.project_id,
            "name": record.name,
            "tenant_id": record.tenant_id,
            "path": record.path,
            "product_id": record.product_id,
            "template": record.template,
            "template_version": record.template_version,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "tenant_root": str(tenant_root),
            "tenant_root_exists": tenant_root.exists(),
            "thegent_config": str(Path(record.path) / ".thegent" / "config.yaml"),
        }
        typer.echo(json.dumps(payload, indent=2))
        return

    console.print(f"\n[bold cyan]{record.name}[/bold cyan]")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("project_id", record.project_id)
    table.add_row("tenant_id", record.tenant_id)
    table.add_row("path", record.path)
    table.add_row("product_id", record.product_id or "(none)")
    table.add_row("template", record.template)
    table.add_row("template_version", record.template_version)
    table.add_row("created_at", record.created_at)
    table.add_row("updated_at", record.updated_at)
    table.add_row("tenant_root", str(tenant_root))
    table.add_row("tenant_root_exists", str(tenant_root.exists()))
    table.add_row(".thegent/config.yaml", str(Path(record.path) / ".thegent" / "config.yaml"))

    console.print(table)


# ---------------------------------------------------------------------------
# sys setup project doctor
# ---------------------------------------------------------------------------


def _doctor_check(
    record_path: str,
    tenant_id: str,
    template: str,
) -> list[tuple[str, str, bool, bool]]:
    """Return list of (check_name, message, passed, fixable) tuples."""
    checks: list[tuple[str, str, bool, bool]] = []
    project_path = Path(record_path)
    tenant_root = Path.home() / ".thegent" / "tenants" / tenant_id
    thegent_config = project_path / ".thegent" / "config.yaml"
    ownership_json = project_path / ".thegent" / "ownership.json"
    templates_lock = project_path / ".thegent" / "templates.lock"

    checks.append(("project_path_exists", str(project_path), project_path.exists(), False))
    checks.append(("tenant_root_exists", str(tenant_root), tenant_root.exists(), True))
    checks.append(("thegent_config_exists", str(thegent_config), thegent_config.exists(), True))
    checks.append(("ownership_json_exists", str(ownership_json), ownership_json.exists(), True))
    checks.append(("templates_lock_exists", str(templates_lock), templates_lock.exists(), True))

    if template == "ag-dd":
        agents_md = project_path / "AGENTS.md"
        checks.append(("agents_md_exists", str(agents_md), agents_md.exists(), False))

    return checks


def _doctor_fix(record_path: str, tenant_id: str) -> list[str]:
    """Auto-repair fixable issues. Returns list of actions taken."""
    actions: list[str] = []
    project_path = Path(record_path)
    tenant_root = Path.home() / ".thegent" / "tenants" / tenant_id

    if not tenant_root.exists():
        tenant_root.mkdir(parents=True, exist_ok=True)
        actions.append(f"created tenant_root: {tenant_root}")

    thegent_dir = project_path / ".thegent"
    if not thegent_dir.exists():
        thegent_dir.mkdir(parents=True, exist_ok=True)
        actions.append(f"created .thegent dir: {thegent_dir}")

    thegent_config = thegent_dir / "config.yaml"
    if not thegent_config.exists():
        thegent_config.write_text(
            f"# Thegent project config\ntenant_id: {tenant_id}\n",
            encoding="utf-8",
        )
        actions.append(f"created config.yaml: {thegent_config}")

    ownership_json = thegent_dir / "ownership.json"
    if not ownership_json.exists():
        ownership_json.write_text(
            json.dumps({"tenant_id": tenant_id, "owner": "default"}, indent=2) + "\n",
            encoding="utf-8",
        )
        actions.append(f"created ownership.json: {ownership_json}")

    templates_lock = thegent_dir / "templates.lock"
    if not templates_lock.exists():
        templates_lock.write_text(
            json.dumps({"template": "none", "version": "unset", "locked_at": ""}, indent=2) + "\n",
            encoding="utf-8",
        )
        actions.append(f"created templates.lock: {templates_lock}")

    return actions


@setup_project_app.command("doctor", help="Health-check a project; use --fix to auto-repair.")
def project_doctor(
    name: Annotated[str, typer.Argument(help="Project name to check")] = "",
    fix: Annotated[bool, typer.Option("--fix", help="Auto-repair fixable issues")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Validate project health: path exists, config valid, tenant consistent."""
    import thegent.infra.project_tenancy as pt_module

    tenancy = pt_module._DEFAULT_TENANCY

    if name:
        record = tenancy.get_project(name=name)
        if record is None:
            record = tenancy.get_project(tenant_id=name)
        if record is None:
            console.print(f"[red]Error: project not found: {name!r}[/red]")
            raise typer.Exit(1)
        candidates = [record]
    else:
        candidates = tenancy.list_projects()

    if not candidates:
        console.print("[dim]No projects to check.[/dim]")
        return

    all_passed = True
    report: list[dict] = []

    for rec in candidates:
        checks = _doctor_check(rec.path, rec.tenant_id, rec.template)
        fixes_applied: list[str] = []

        if fix:
            fixes_applied = _doctor_fix(rec.path, rec.tenant_id)
            # Re-run checks after fix
            checks = _doctor_check(rec.path, rec.tenant_id, rec.template)

        project_passed = all(passed for _, _, passed, _ in checks)
        all_passed = all_passed and project_passed
        report.append(
            {
                "project": rec.name,
                "tenant_id": rec.tenant_id,
                "checks": [
                    {"check": chk, "detail": detail, "passed": passed, "fixable": fixable}
                    for chk, detail, passed, fixable in checks
                ],
                "fixes_applied": fixes_applied,
                "passed": project_passed,
            }
        )

    if json_output:
        typer.echo(json.dumps(report, indent=2))
        raise typer.Exit(0 if all_passed else 1)

    for entry in report:
        status_icon = "[green]PASS[/green]" if entry["passed"] else "[red]FAIL[/red]"
        console.print(f"\n[bold]{entry['project']}[/bold] ({entry['tenant_id']}) -- {status_icon}")

        tbl = Table(show_header=True, box=None, padding=(0, 2))
        tbl.add_column("Check", style="cyan")
        tbl.add_column("Result")
        tbl.add_column("Detail", style="dim")

        for chk_entry in entry["checks"]:
            icon = "[green]ok[/green]" if chk_entry["passed"] else "[red]FAIL[/red]"
            if not chk_entry["passed"] and chk_entry["fixable"] and not fix:
                icon += " [yellow](fixable)[/yellow]"
            tbl.add_row(chk_entry["check"], icon, chk_entry["detail"])

        console.print(tbl)

        if entry["fixes_applied"]:
            console.print("[dim]Fixes applied:[/dim]")
            for action in entry["fixes_applied"]:
                console.print(f"  [green]+[/green] {action}")

    if not all_passed and not fix:
        console.print("\n[yellow]Run with --fix to auto-repair fixable issues.[/yellow]")

    raise typer.Exit(0 if all_passed else 1)


# ---------------------------------------------------------------------------
# install project
# ---------------------------------------------------------------------------


@install_project_app.callback(invoke_without_command=True)
def install_project_cmd(
    ctx: typer.Context,
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project name, tenant_id, or path (default: cwd)"),
    ] = "",
    template: Annotated[str, typer.Option("--template", help="Template overlay: ag-dd or none")] = "none",
    mode: Annotated[str, typer.Option("--mode", "-m", help="Install mode: smart, overwrite, skip")] = "smart",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Install .thegent/config.yaml, ownership.json, and templates.lock into a project."""
    if ctx.invoked_subcommand is not None:
        return

    import thegent.infra.project_tenancy as pt_module
    from thegent.install import run_install_project

    if mode not in {"smart", "overwrite", "skip"}:
        console.print(f"[red]Error: invalid mode {mode!r}. Must be: smart, overwrite, skip[/red]")
        raise typer.Exit(1)

    result = run_install_project(
        project_selector=project or None,
        template=template,
        mode=mode,
        dry_run=dry_run,
        registry_path=pt_module._DEFAULT_TENANCY._registry_path,
    )

    if json_output:
        typer.echo(json.dumps(result, indent=2))
        if result.get("errors"):
            raise typer.Exit(1)
        return

    if dry_run:
        console.print("[dim](dry-run mode -- no files written)[/dim]")

    console.print(f"[bold]Project:[/bold] {result.get('project_name', '(unknown)')}")
    console.print(f"  path     : {result.get('path', '')}")
    console.print(f"  template : {result.get('template', 'none')}")
    console.print(f"  mode     : {mode}")

    installed = result.get("installed", [])
    skipped = result.get("skipped", [])
    errors = result.get("errors", [])

    if installed:
        console.print(f"  [green]installed ({len(installed)}):[/green] {', '.join(installed)}")
    if skipped:
        console.print(f"  [dim]skipped ({len(skipped)}):[/dim] {', '.join(skipped)}")
    if errors:
        for err in errors:
            console.print(f"  [red]error:[/red] {err}")
        raise typer.Exit(1)


@install_project_app.command("brownfield", help="Adopt and install an unregistered or partial brownfield project.")
def install_project_brownfield(
    project: Annotated[
        str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")
    ] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (defaults to directory name).")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override.")] = "",
    template: Annotated[
        str,
        typer.Option(
            "--template",
            help="Template adoption mode: auto|ag-dd|none (default auto). auto infers from existing metadata.",
        ),
    ] = "auto",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Brownfield install entrypoint that includes migration + runtime install."""
    if not project:
        console.print("[yellow]Usage: thegent install project brownfield <project>[/yellow]")
        return
    project_migrate(
        project=project,
        name=name,
        tenant=tenant,
        template=template,
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )


@install_project_app.command("ag-dd", help="Adopt and install a project using AG-DD brownfield template mode.")
def install_project_brownfield_agdd(
    project: Annotated[
        str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")
    ] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (defaults to directory name).")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override.")] = "",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Brownfield install variant that fixes template mode to AG-DD."""
    if not project:
        console.print("[yellow]Usage: thegent install project ag-dd <project>[/yellow]")
        return
    install_project_brownfield(
        project=project,
        name=name,
        tenant=tenant,
        template="ag-dd",
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )


@install_project_app.command("none", help="Adopt and install a project without template overlay.")
def install_project_none(
    project: Annotated[
        str | None, typer.Argument(help="Existing project directory to migrate or reconcile.")
    ] = None,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (defaults to directory name).")] = "",
    tenant: Annotated[str, typer.Option("--tenant", "-t", help="Tenant ID override.")] = "",
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Install/apply mode for template assets: smart|overwrite|skip."),
    ] = "smart",
    reconcile: Annotated[
        bool,
        typer.Option("--reconcile/--no-reconcile", help="Synchronize registry metadata with detected state."),
    ] = True,
    register: Annotated[
        bool,
        typer.Option("--register", help="Register the project before migration if it is not already registered."),
    ] = True,
    install_runtime: Annotated[
        bool,
        typer.Option("--install-runtime", "--runtime", help="Run Thegent runtime asset install/update."),
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing changes.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Brownfield install variant that fixes template mode to none."""
    if not project:
        console.print("[yellow]Usage: thegent install project none <project>[/yellow]")
        return
    install_project_brownfield(
        project=project,
        name=name,
        tenant=tenant,
        template="none",
        mode=mode,
        reconcile=reconcile,
        register=register,
        install_runtime=install_runtime,
        dry_run=dry_run,
        json_output=json_output,
    )
