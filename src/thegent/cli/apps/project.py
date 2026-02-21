"""First-class project tenancy commands: sys setup project and install project.

# @trace FR-TEN-001
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slug(name: str) -> str:
    """Convert a project name to a safe tenant_id slug."""
    return "".join(c if (c.isalnum() or c in "-_") else "-" for c in name.lower()).strip("-")


def _resolve_project_selector(selector: str) -> str:
    """Resolve --project selector to a project name or path.

    Accepts: name string, tenant_id, or absolute/relative path.
    Returns the raw selector for lookup (the callers use multi-field lookup).
    """
    return selector.strip()


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


def _scaffold_profile_names() -> list[str]:
    """Sorted list of supported scaffold presets."""
    return sorted(_SCAFFOLD_PROFILES)


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
        str, typer.Argument(help="Destination directory for generated project scaffold")
    ],
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


@install_project_app.command("project", help="Install Thegent runtime assets into a registered project.")
def install_project_cmd(
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
