"""Install module for managed installation and synchronization of thegent components."""

import json
import os
import platform
import shutil
import sys
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

try:
    from thegent.mcp_manage import service_install, service_start, service_uninstall
except ImportError:
    # Handle cases where mcp_manage might not be available
    def service_install() -> tuple[bool, str]:
        return False, "mcp_manage not available"

    def service_start() -> tuple[bool, str]:
        return False, "mcp_manage not available"

    def service_uninstall() -> tuple[bool, str]:
        return False, "mcp_manage not available"

# --- Models ---


class InstallMode(StrEnum):
    SMART = "smart"
    EDITABLE = "editable"
    FORCE = "force"
    INTERACTIVE = "interactive"
    UNDO = "undo"


class FileAction(StrEnum):
    COPIED = "copied"
    SYMLINKED = "symlinked"
    SKIPPED = "skipped"
    BACKED_UP = "backed_up"
    REMOVED = "removed"
    CONFLICT = "conflict"
    ERROR = "error"


class FileManifest(BaseModel):
    source: str
    target: str
    mode: str  # "copy" or "symlink"
    mtime: float
    backup: str | None = None
    checksum: str | None = None


class ConfigManifest(BaseModel):
    file_path: str
    key: str
    original_value: Any = None
    new_value: Any = None


class InstallManifest(BaseModel):
    version: int = 1
    installed_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    files: dict[str, FileManifest] = {}  # target_path -> manifest
    configs: list[ConfigManifest] = []


class BundleItem(BaseModel):
    source: str
    target: str
    mode: str = ""


class BundleManifest(BaseModel):
    """Optional external manifest describing installable third-party bundles."""

    bundles: dict[str, list[BundleItem]] = {}


def get_default_bundle_manifest_path() -> Path:
    """Default location for the third-party bundle manifest."""

    return Path.home() / ".config" / "thegent" / "third_party_bundles.json"


def _coerce_path(value: str) -> Path:
    """Normalize and expand a user path token."""

    return Path(os.path.expandvars(value)).expanduser()


def load_bundle_manifest(path: Path | str | None = None) -> dict[str, list[dict[str, Any]]]:
    """Load third-party bundle definitions from an external JSON manifest.

    Expected schema:
      {
        "bundles": {
          "name": {
            "items": [
              {"source": "...", "target": "...", "mode": "smart|force|editable"}
            ]
          }
        }
      }
    """

    manifest_path = _coerce_path(str(path)) if path is not None else get_default_bundle_manifest_path()

    if not manifest_path.exists():
        return {}

    try:
        data = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError, ValueError):
        return {}

    raw_bundles = data.get("bundles") if isinstance(data, dict) else None
    if not isinstance(raw_bundles, dict):
        return {}

    bundles: dict[str, list[dict[str, Any]]] = {}
    for name, bundle in raw_bundles.items():
        if not isinstance(name, str):
            continue
        raw_items = bundle.get("items") if isinstance(bundle, dict) else bundle

        if not isinstance(raw_items, list):
            continue

        items: list[dict[str, Any]] = []
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue

            source = raw.get("source")
            target = raw.get("target")
            if not isinstance(source, str) or not isinstance(target, str):
                continue

            item: dict[str, Any] = {
                "source": source.strip(),
                "target": target.strip(),
            }
            mode = raw.get("mode")
            if isinstance(mode, str) and mode.strip():
                item["mode"] = mode.strip().lower()
            else:
                item["mode"] = ""
            items.append(item)

        if items:
            bundles[name] = items

    return bundles


def _coerce_bundle_items(raw: dict[str, list[dict[str, Any]]]) -> BundleManifest:
    """Normalize raw manifest payloads into a validated structure."""

    normalized: dict[str, list[BundleItem]] = {}
    for name, items in raw.items():
        if not name or not isinstance(items, list):
            continue
        parsed_items: list[BundleItem] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            source = item.get("source")
            target = item.get("target")
            if not isinstance(source, str) or not isinstance(target, str):
                continue
            parsed_items.append(
                BundleItem(
                    source=source.strip(),
                    target=target.strip(),
                    mode=str(item.get("mode", "")).strip().lower(),
                )
            )
        if parsed_items:
            normalized[name] = parsed_items
    return BundleManifest(bundles=normalized)


def resolve_bundles(
    bundle_names: list[str] | None,
    bundle_manifest: Path | str | None,
    thegent_root: Path,
    home: Path,
    cwd: Path,
    fallback_mode: InstallMode,
) -> list[tuple[Path, Path, InstallMode]]:
    """Resolve selected bundles to install tuples."""

    selected = list(bundle_names or [])
    if not selected:
        return []

    manifest = _coerce_bundle_items(load_bundle_manifest(bundle_manifest)).bundles
    include_all = "all" in selected

    missing = [name for name in selected if name != "all" and name not in manifest]
    if missing:
        known = ", ".join(sorted(manifest))
        hint = f"Known: {known}" if known else "No bundles available"
        raise ValueError(f"Unknown bundle(s): {', '.join(missing)}. {hint}")

    resolved_items: list[tuple[Path, Path, InstallMode]] = []
    names_to_apply: list[str]
    if include_all:
        names_to_apply = list(manifest.keys())
    else:
        seen: set[str] = set()
        names_to_apply = []
        for name in selected:
            if name in seen:
                continue
            seen.add(name)
            names_to_apply.append(name)

    for name in names_to_apply:
        for item in manifest[name]:
            source = _resolve_bundle_source(item.source, thegent_root)
            target = _resolve_bundle_target(item.target, home=home, cwd=cwd)
            mode = _resolve_bundle_mode(item.mode, fallback_mode)
            resolved_items.append((source, target, mode))
    return resolved_items


def _resolve_bundle_mode(raw_mode: str, fallback: InstallMode) -> InstallMode:
    """Convert a user-defined bundle mode into an InstallMode."""

    normalized = (raw_mode or "").strip().lower()
    if normalized in {"", "copy"}:
        return fallback
    if normalized == "symlink":
        return InstallMode.EDITABLE
    try:
        return InstallMode(normalized)
    except ValueError:
        return fallback


def _resolve_bundle_source(source: str, thegent_root: Path) -> Path:
    """Resolve a bundle source path.

    Supports:
    - thegent:/relative/path -> resolved relative to thegent root
    - home/absolute/env-expanded paths
    - relative paths -> resolved relative to thegent root
    """

    normalized = source.strip()
    if normalized.startswith("thegent:"):
        normalized = normalized.split(":", 1)[1].lstrip("/")
        return thegent_root / normalized

    expanded = _coerce_path(normalized)
    if expanded.is_absolute():
        return expanded
    return thegent_root / expanded


def _resolve_bundle_target(target: str, *, home: Path, cwd: Path) -> Path:
    """Resolve a bundle target path.

    Allows templating with {home}, {cwd}, ${HOME}, ${CWD}.
    Relative destinations are placed under the home directory.
    """

    normalized = target.strip()
    normalized = normalized.replace("{home}", str(home)).replace("{HOME}", str(home))
    normalized = normalized.replace("{cwd}", str(cwd)).replace("{CWD}", str(cwd))
    normalized = normalized.replace("${HOME}", str(home)).replace("${CWD}", str(cwd))
    normalized = os.path.expandvars(normalized)

    expanded = _coerce_path(normalized)
    if expanded.is_absolute():
        return expanded
    return home / expanded


# --- Constants & Mappings ---

# Valid targets
VALID_TARGETS = {"claude-code", "claude-desktop", "cursor", "codex", "droid", "all", "claude", "factory", "both"}

# Exclude list for file sync
EXCLUDE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "history.jsonl",
    "session-env",
    "debug",
    "todos",
    "tasks",
    "teams",
    "shell-snapshots",
    "file-history",
    "paste-cache",
    ".git",
    ".venv",
    "node_modules",
}

# Bundle definitions
CLAUDE_CODE_FILES = {
    "skills/agent-orchestra": "skills/agent-orchestra",
    "skills/sitback-agent": "skills/sitback-agent",
    "hooks": "hooks",
    "templates": "templates",
    "agents": "agents",
    "commands": "commands",
    "contracts": "contracts",
    "CLAUDE.md": "CLAUDE.md",
    "mcp_servers.json": "mcp_servers.json",
    "qa-config.json": "qa-config.json",
}

# Cursor specific files
CURSOR_FILES = {
    "skills/agent-orchestra": "skills-cursor/agent-orchestra",
}

FACTORY_FILES = {
    ".factory/hooks": "hooks",
    ".factory/skills": "skills",
    ".factory/commands": "commands",
    ".factory/droids": "droids",
    ".factory/plugins": "plugins",
    ".factory/mcp.json": "mcp.json",
    ".factory/config.json": "config.json",
    ".factory/settings.json": "settings.json",
}

# MCP tools to auto-approve in Cursor
THEGENT_TOOLS = [
    "thegent_run",
    "thegent_bg",
    "thegent_ps",
    "thegent_status",
    "thegent_logs",
    "thegent_inspect",
    "thegent_stop",
    "thegent_wait",
    "thegent_list_agents",
    "thegent_list_droids",
    "thegent_list_models",
    "thegent_dag_list",
    "thegent_observe_summary",
    "thegent_sitback_dashboard",
    "thegent_session_contracts",
    "thegent_session_contract_health_gate",
    "thegent_session_contract_health_report",
    "thegent_session_contract_health_trend",
    "thegent_resolve_model_route",
    "thegent_suggest_prompt",
]

CLAUDE_MAPPING = CLAUDE_CODE_FILES
FACTORY_MAPPING = FACTORY_FILES

ROOT_FILES = {"CLAUDE.md", "mcp_servers.json", "qa-config.json"}

# --- Legacy Shims for Tests ---


def should_exclude(path: Path | str) -> bool:
    """Legacy shim for tests."""
    p = Path(path)
    return any(part in EXCLUDE_DIRS for part in p.parts)


def create_symlink(source: Path, target: Path, dry_run: bool = False) -> str:
    """Legacy shim for tests."""
    if target.is_symlink() and target.exists() and target.resolve() == source.resolve():
        return "existed"
    mgr = InstallManager(dry_run=dry_run)
    action = mgr.install_file(source, target, mode=InstallMode.EDITABLE)
    if action == FileAction.SYMLINKED:
        return "created"
    return "existed"


def smart_copy_file(source: Path, target: Path, dry_run: bool = False) -> str:
    """Legacy shim for tests."""
    mgr = InstallManager(dry_run=dry_run)
    action = mgr.install_file(source, target, mode=InstallMode.SMART)
    if action == FileAction.COPIED:
        return "copied"
    return "skipped"


def get_source_dest_mapping(thegent_root: Path, bundle: str) -> dict[Path, Path]:
    """Legacy shim for tests."""
    mapping = {}
    if bundle not in ("claude", "factory", "both", "claude-code"):
        raise ValueError(f"Invalid bundle: {bundle}")

    home = get_home_dir()
    if bundle in ("claude", "claude-code", "both"):
        claude_dir = home / ".claude"
        for src_rel, dst_rel in CLAUDE_CODE_FILES.items():
            mapping[thegent_root / src_rel] = claude_dir / dst_rel
    if bundle in ("factory", "both"):
        factory_dir = Path.cwd() / ".factory"  # Default for tests
        for src_rel, dst_rel in FACTORY_FILES.items():
            mapping[thegent_root / src_rel] = factory_dir / dst_rel
    return mapping


# --- Paths ---


def get_home_dir() -> Path:
    return Path.home()


def get_manifest_path() -> Path:
    p = Path.home() / ".cache" / "thegent" / "install_manifest.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def get_backup_dir() -> Path:
    p = Path.home() / ".cache" / "thegent" / "backups"
    p.mkdir(parents=True, exist_ok=True)
    return p


# --- Core Logic ---


class InstallManager:
    def __init__(self, dry_run: bool = False, verbose: bool = False) -> None:
        self.dry_run = dry_run
        self.verbose = verbose
        self.manifest_path = get_manifest_path()
        self.backup_dir = get_backup_dir()
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> InstallManifest:
        if self.manifest_path.exists():
            try:
                return InstallManifest.model_validate_json(self.manifest_path.read_text())
            except (json.JSONDecodeError, ValueError):
                return InstallManifest()
        return InstallManifest()

    def save_manifest(self) -> None:
        if not self.dry_run:
            self.manifest_path.write_text(self.manifest.model_dump_json(indent=2))

    def _backup_file(self, target: Path) -> Path | None:
        if not target.exists():
            return None
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        rel_path = target.relative_to(Path.home()) if target.is_relative_to(Path.home()) else target.name
        backup_path = self.backup_dir / timestamp / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup_path)
        return backup_path

    def install_file(self, source: Path, target: Path, mode: InstallMode) -> FileAction:
        if not source.exists():
            return FileAction.ERROR

        target.parent.mkdir(parents=True, exist_ok=True)

        # Check for conflict
        if target.exists() or target.is_symlink():
            if mode == InstallMode.FORCE:
                pass  # Proceed to overwrite
            elif mode == InstallMode.EDITABLE:
                pass  # Proceed to symlink
            elif mode == InstallMode.SMART:
                src_mtime = source.stat().st_mtime
                dst_mtime = target.stat().st_mtime
                if dst_mtime >= src_mtime:
                    if self.verbose:
                        sys.stdout.write(f"  Skipped (up to date or user modified): {target}\n")
                    return FileAction.SKIPPED
            elif mode == InstallMode.INTERACTIVE:
                # In non-interactive shells, this might hang. We should check if sys.stdin.isatty()
                if not sys.stdin.isatty():
                    if self.verbose:
                        sys.stderr.write(f"  Non-interactive shell, skipping conflict: {target}\n")
                    return FileAction.CONFLICT

                choice = Prompt.ask(
                    f"Conflict detected for {target}. [o]verwrite, [s]kip, [b]ackup & overwrite?",
                    choices=["o", "s", "b"],
                    default="s",
                )
                if choice == "s":
                    return FileAction.SKIPPED
                mode = InstallMode.SMART if choice == "b" else InstallMode.FORCE

        # Perform action
        backup_path = None
        if not self.dry_run:
            if target.exists() or target.is_symlink():
                backup_path = self._backup_file(target)
                if target.is_symlink() or target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)

            if mode == InstallMode.EDITABLE:
                target.symlink_to(source)
                action = FileAction.SYMLINKED
            else:
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
                action = FileAction.COPIED

            # Register in manifest
            self.manifest.files[str(target)] = FileManifest(
                source=str(source),
                target=str(target),
                mode="symlink" if mode == InstallMode.EDITABLE else "copy",
                mtime=target.stat().st_mtime if target.exists() else 0,
                backup=str(backup_path) if backup_path else None,
            )
        else:
            action = FileAction.COPIED if mode != InstallMode.EDITABLE else FileAction.SYMLINKED
            if self.verbose:
                sys.stdout.write(f"  Would {'symlink' if mode == InstallMode.EDITABLE else 'copy'}: {target}\n")

        return action

    def update_config(self, config_path: Path, key_path: str, value: Any) -> bool:
        """Update a JSON config file at a specific key path (e.g. 'mcpServers.thegent')."""
        if self.dry_run:
            if self.verbose:
                sys.stdout.write(f"  Would update {config_path}: {key_path} = {value}\n")
            return True

        config_path.parent.mkdir(parents=True, exist_ok=True)
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
            except Exception:
                config = {}
        else:
            config = {}

        # Backup original value for manifest
        parts = key_path.split(".")
        curr = config
        original_value = None
        for part in parts[:-1]:
            if part not in curr:
                curr[part] = {}
            curr = curr[part]

        if parts[-1] in curr:
            original_value = curr[parts[-1]]

        curr[parts[-1]] = value

        config_path.write_text(json.dumps(config, indent=2))

        # Register in manifest
        self.manifest.configs.append(
            ConfigManifest(file_path=str(config_path), key=key_path, original_value=original_value, new_value=value)
        )
        return True

    def uninstall(self) -> dict[str, int]:
        counts = {"removed": 0, "restored": 0, "reverted": 0, "errors": 0}

        # 1. Revert Configs (Reverse order)
        for cfg in reversed(self.manifest.configs):
            path = Path(cfg.file_path)
            if path.exists():
                try:
                    data = json.loads(path.read_text())
                    parts = cfg.key.split(".")
                    curr = data
                    for part in parts[:-1]:
                        curr = curr.get(part, {})

                    if cfg.original_value is None:
                        if parts[-1] in curr:
                            del curr[parts[-1]]
                    else:
                        curr[parts[-1]] = cfg.original_value

                    if not self.dry_run:
                        path.write_text(json.dumps(data, indent=2))
                    counts["reverted"] += 1
                except Exception:
                    counts["errors"] += 1

        # 2. Revert Files
        for target_str, m in list(self.manifest.files.items()):
            target = Path(target_str)
            if not target.exists() and not target.is_symlink():
                continue

            try:
                if not self.dry_run:
                    if target.is_symlink() or target.is_file():
                        target.unlink()
                    else:
                        shutil.rmtree(target)

                    if m.backup and Path(m.backup).exists():
                        # Restore backup
                        backup = Path(m.backup)
                        if backup.is_dir():
                            shutil.copytree(backup, target)
                        else:
                            shutil.copy2(backup, target)
                        counts["restored"] += 1
                    else:
                        counts["removed"] += 1

                    del self.manifest.files[target_str]
                else:
                    counts["removed"] += 1
            except Exception:
                counts["errors"] += 1

        self.save_manifest()
        return counts


def _get_mcp_config(url: str, client: str = "generic") -> dict[str, Any]:
    if client == "cursor":
        return {
            "url": url,
            "transport": "http",
            "description": "Thegent agent orchestration (run, bg, ps, logs, dag, etc.)",
            "autoApprove": THEGENT_TOOLS,
            "transportType": "stdio" if "stdio" in url else "http",  # Hint for cursor
        }
    if client == "claude-desktop":
        return {"url": url}

    return {
        "url": url,
        "transport": "http",
        "description": "Thegent agent orchestration (run, bg, ps, logs, dag, etc.)",
    }


def run_wizard(url: str | None = None) -> None:
    """Interactive installation wizard using rich."""
    console = Console()
    console.clear()

    # Header
    console.print(
        Panel(
            "[bold cyan]Thegent[/bold cyan] [dim]Installation Wizard[/dim]\n"
            "[dim]Agentic orchestration & MCP management[/dim]",
            border_style="cyan",
            expand=False,
            padding=(1, 2),
        )
    )

    # 1. Target Detection & Selection
    console.print("\n[bold]1. Select Targets[/bold]")
    targets_map = {
        "1": ("cursor", "Cursor"),
        "2": ("claude-code", "Claude Code"),
        "3": ("claude-desktop", "Claude Desktop"),
        "4": ("codex", "Codex"),
        "5": ("droid", "Droid / Factory"),
    }

    # Simple detection
    home = Path.home()
    detection = {
        "cursor": (home / "Library/Application Support/Cursor").exists() or (home / ".cursor").exists(),
        "claude-code": (home / ".claude").exists(),
        "claude-desktop": (home / "Library/Application Support/Claude").exists(),
        "codex": (home / ".codex").exists(),
        "droid": (home / ".factory").exists(),
    }

    for k, (code, name) in targets_map.items():
        detected = detection.get(code, False)
        status = "[green]detected[/green]" if detected else "[dim]not found[/dim]"
        console.print(f"  {k}) {name:16} {status}")

    selected_input = Prompt.ask("\nTargets to configure (e.g. 1,2 or 'all')", default="all")

    if selected_input.lower() == "all":
        selected_targets = [v[0] for v in targets_map.values()]
    else:
        selected_targets = []
        for part in selected_input.replace(",", " ").split():
            if part in targets_map:
                selected_targets.append(targets_map[part][0])

    if not selected_targets:
        console.print("[yellow]No targets selected. Exiting.[/yellow]")
        return

    # 2. Mode selection
    console.print("\n[bold]2. Select Mode[/bold]")
    console.print("  [cyan]smart[/cyan]    [dim]Copy only if newer (safe, recommended)[/dim]")
    console.print("  [cyan]editable[/cyan] [dim]Symlink (best for dev, bi-directional sync)[/dim]")
    console.print("  [cyan]force[/cyan]    [dim]Overwrite everything[/dim]")

    mode = Prompt.ask("\nChoose mode", choices=["smart", "editable", "force"], default="smart")

    # 3. Service setup
    install_service = False
    if platform.system() == "Darwin":
        console.print("\n[bold]3. Service Setup[/bold]")
        install_service = Confirm.ask("Install background MCP service (launchd)?", default=True)

    # 4. Confirmation Summary
    console.print("\n[bold]Summary[/bold]")
    summary_table = Table(box=None, show_header=False, padding=(0, 2))
    summary_table.add_row("[dim]Targets[/dim]", ", ".join(selected_targets))
    summary_table.add_row("[dim]Mode[/dim]", f"[bold cyan]{mode}[/bold cyan]")
    summary_table.add_row("[dim]Service[/dim]", "[green]Yes[/green]" if install_service else "[red]No[/red]")
    if url:
        summary_table.add_row("[dim]MCP URL[/dim]", f"[cyan]{url}[/cyan]")
    console.print(summary_table)

    if not Confirm.ask("\nProceed with installation?", default=True):
        console.print("[yellow]Installation cancelled.[/yellow]")
        return

    # 5. Execution
    console.print()
    with console.status("[bold cyan]Installing...[/bold cyan]", spinner="dots"):
        results = []
        for t in selected_targets:
            res = run_install(target=t, mode=mode, install_service=install_service, verbose=False, url=url)
            results.append((t, res))

    # Final Result Table
    console.print("\n[bold green]✓ Installation Complete[/bold green]")
    res_table = Table(box=None, padding=(0, 2))
    res_table.add_column("Target", style="cyan")
    res_table.add_column("Status", style="green")
    res_table.add_column("Notes", style="dim")

    for t, counts in results:
        status = "Success" if counts.get("errors", 0) == 0 else "Warnings"
        notes = f"{counts.get('copied', 0)} files, {counts.get('skipped', 0)} skipped"
        res_table.add_row(t, status, notes)

    console.print(res_table)

    console.print("\n[bold]Next Steps[/bold]")
    console.print("  → Restart your AI agent (Cursor, Claude Desktop, etc.)")
    console.print("  → Run [bold]thegent serve[/bold] (if not using service)")
    console.print("  → Try [bold]thegent ps[/bold] in your terminal")
    console.print("\n[dim]Happy orchestrating![/dim]")


def run_install(
    target: str = "all",
    mode: str = "smart",
    dry_run: bool = False,
    verbose: bool = False,
    url: str | None = None,
    install_service: bool = False,
    bundles: list[str] | None = None,
    bundle_manifest: Path | str | None = None,
) -> dict:
    if target != "all" and target not in VALID_TARGETS:
        raise ValueError(f"Invalid target: {target}. Valid targets: {VALID_TARGETS}")

    mgr = InstallManager(dry_run=dry_run, verbose=verbose)
    if mode == "undo":
        res = mgr.uninstall()
        if platform.system() == "Darwin":
            ok, msg = service_uninstall()
            if ok:
                res["reverted"] += 1
        return res

    install_mode = InstallMode(mode)
    thegent_root = Path(__file__).parent.parent.parent.resolve()
    mcp_url = url or "http://127.0.0.1:3847/mcp"

    counts: dict[str, int] = {"copied": 0, "skipped": 0, "conflicts": 0, "errors": 0}
    home = get_home_dir()
    cwd = Path.cwd()

    targets = [target] if target != "all" else ["claude-code", "claude-desktop", "cursor", "codex", "droid"]

    # Optional: Install launchd service on macOS
    if install_service and platform.system() == "Darwin" and not dry_run:
        ok, msg = service_install()
        if ok:
            if verbose:
                sys.stdout.write(f"  {msg}\n")
            service_start()
            if verbose:
                sys.stdout.write("  Service started.\n")
        else:
            if verbose:
                sys.stdout.write(f"  Service install failed: {msg}\n")
            counts["errors"] += 1

    for t in targets:
        if verbose:
            sys.stdout.write(f"Installing to {t}...\n")

        mcp_cfg = _get_mcp_config(mcp_url, client=t)

        if t == "claude-code":
            # Files to ~/.claude/
            claude_dir = home / ".claude"
            for src_rel, dst_rel in CLAUDE_CODE_FILES.items():
                src = thegent_root / src_rel
                dst = claude_dir / dst_rel
                if src.exists():
                    res = mgr.install_file(src, dst, install_mode)
                    key = res.value if hasattr(res, "value") else str(res)
                    counts[key] = counts.get(key, 0) + 1

            # MCP to ~/.claude.json
            mgr.update_config(home / ".claude.json", "mcpServers.thegent", mcp_cfg)

        elif t == "claude-desktop":
            if platform.system() == "Darwin":
                p = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
            elif platform.system() == "Windows":
                p = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
            else:
                p = home / ".config" / "Claude" / "claude_desktop_config.json"

            if p.parent.exists():
                mgr.update_config(p, "mcpServers.thegent", mcp_cfg)

        elif t == "cursor":
            # Files to ~/.cursor/
            cursor_dir = home / ".cursor"
            for src_rel, dst_rel in CURSOR_FILES.items():
                src = thegent_root / src_rel
                dst = cursor_dir / dst_rel
                if src.exists():
                    res = mgr.install_file(src, dst, install_mode)
                    key = res.value if hasattr(res, "value") else str(res)
                    counts[key] = counts.get(key, 0) + 1

            # Workspace level
            mgr.update_config(Path.cwd() / ".cursor" / "mcp.json", "mcpServers.thegent", mcp_cfg)
            # Global level
            mgr.update_config(home / ".cursor" / "mcp.json", "mcpServers.thegent", mcp_cfg)

        elif t == "codex":
            mgr.update_config(home / ".codex" / "mcp.json", "mcpServers.thegent", mcp_cfg)

        elif t == "droid":
            # Files to ~/.factory/
            factory_dir = home / ".factory"
            for src_rel, dst_rel in FACTORY_FILES.items():
                src = thegent_root / src_rel
                dst = factory_dir / dst_rel
                if src.exists():
                    res = mgr.install_file(src, dst, install_mode)
                    key = res.value if hasattr(res, "value") else str(res)
                    counts[key] = counts.get(key, 0) + 1

            # MCP to .factory/mcp.json in CWD
            mgr.update_config(Path.cwd() / ".factory" / "mcp.json", "mcpServers.thegent", mcp_cfg)

    # Optional third-party bundles to install
    for src, dst, bundle_mode in resolve_bundles(
        bundle_names=bundles,
        bundle_manifest=bundle_manifest,
        thegent_root=thegent_root,
        home=home,
        cwd=cwd,
        fallback_mode=install_mode,
    ):
        if verbose:
            sys.stdout.write(f"Installing bundle item: {src} -> {dst}\n")
        res = mgr.install_file(src, dst, bundle_mode)
        key = res.value if hasattr(res, "value") else str(res)
        counts[key] = counts.get(key, 0) + 1

    mgr.save_manifest()

    # Normalize counts for return
    return {
        "copied": counts.get("copied", 0) + counts.get("symlinked", 0),
        "skipped": counts.get("skipped", 0),
        "conflicts": counts.get("conflict", 0),
        "errors": counts.get("errors", 0),
    }
