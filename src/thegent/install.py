"""Install module for managed installation and synchronization of thegent components."""

import orjson as json
import logging
import platform
import shutil
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
import sys
from importlib import import_module
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from thegent.config import ThegentSettings

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from thegent.infra import copy_file, copy_tree, run_subprocess_optimized
from thegent.install_backups import (
    backup_shell_config as _backup_shell_config,
    cleanup_old_backups,
    list_backups,
    restore_shell_config,
)
from thegent.install_bundles import (
    coerce_path as _coerce_path,
    coerce_bundle_items as _coerce_bundle_items,
    get_bundle_manifest_path,
    get_default_bundle_manifest_path,
    list_bundle_names,
    load_bundle_manifest,
    resolve_bundle_mode as _resolve_bundle_mode,
    resolve_bundle_source as _resolve_bundle_source,
    resolve_bundle_target as _resolve_bundle_target,
    source_requires_pin_and_checksum as _source_requires_pin_and_checksum,
    validate_bundle_manifest,
)
from thegent.install_constants import (
    CLAUDE_CODE_FILES,
    CLAUDE_MAPPING,
    CURSOR_FILES,
    EXCLUDE_DIRS,
    FACTORY_FILES,
    FACTORY_MAPPING,
    ROOT_FILES,
    SHELL_FILES,
    SHELL_LOCAL_TEMPLATE,
    THEGENT_TOOLS,
    VALID_TARGETS,
    get_targets_for_install,
)
from thegent.install_models import (
    BundleItem,
    BundleManifest,
    ConfigManifest,
    FileAction,
    FileManifest,
    InstallManifest,
    InstallMode,
)
from thegent.install_powershell import (
    POWERSHELL_HOOK_SENTINEL as _POWERSHELL_HOOK_SENTINEL,
    POWERSHELL_MISE_HOOK,
    detect_powershell_profile,
    is_powershell_environment as _is_powershell_environment,
    write_powershell_mise_hook,
)
from thegent.install_subprocess_utils import command_exists as _command_exists, run_command as _run_command

__all__ = [
    "CLAUDE_MAPPING",
    "FACTORY_MAPPING",
    "POWERSHELL_MISE_HOOK",
    "ROOT_FILES",
    "_POWERSHELL_HOOK_SENTINEL",
    "BundleItem",
    "BundleManifest",
    "InstallMode",
    "_coerce_bundle_items",
    "_coerce_path",
    "_resolve_bundle_mode",
    "_resolve_bundle_source",
    "_resolve_bundle_target",
    "_source_requires_pin_and_checksum",
    "cleanup_old_backups",
    "get_bundle_manifest_path",
    "get_default_bundle_manifest_path",
    "list_backups",
    "list_bundle_names",
    "load_bundle_manifest",
    "restore_shell_config",
    "validate_bundle_manifest",
]

from thegent.mcp.manage import service_install, service_start, service_uninstall

_LOG = logging.getLogger(__name__)


def _get_thegent_root() -> Path:
    """Return thegent root (has hooks/, skills/). Works for dev and installed package."""
    # Installed: hooks/skills are force-included at thegent/hooks, thegent/skills
    try:
        module = import_module("thegent")
    except (ImportError, ModuleNotFoundError) as exc:
        _LOG.warning(
            "install_root_detection_fallback",
            extra={"failure_type": "import_error", "error_type": type(exc).__name__, "error_message": str(exc)[:180]},
        )
    else:
        try:
            module_file = getattr(module, "__file__", None)
            if module_file:
                pkg = Path(module_file).resolve().parent
                if (pkg / "hooks").exists() or (pkg / "skills").exists():
                    return pkg
        except (OSError, RuntimeError, ValueError, TypeError) as exc:
            _LOG.warning(
                "install_root_detection_fallback",
                extra={
                    "failure_type": "path_resolution_error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc)[:180],
                },
            )
    # Dev: install.py is at src/thegent/install.py -> project root is parent.parent.parent
    return Path(__file__).resolve().parent.parent.parent


def setup_hooks(cwd: Path | None = None, dry_run: bool = False, verbose: bool = False) -> dict[str, int]:
    """Install thegent hooks into .git/hooks. Returns counts dict."""
    root = _get_thegent_root()
    hooks_src = root / "hooks"
    cwd = cwd or Path.cwd()
    git_hooks = cwd / ".git" / "hooks"
    counts: dict[str, int] = {"installed": 0, "skipped": 0, "errors": 0}

    if not git_hooks.parent.exists():
        if verbose:
            sys.stdout.write("  Not a git repo; skipping hooks.\n")
        counts["skipped"] += 1
        return counts

    if not hooks_src.exists():
        if verbose:
            sys.stdout.write(f"  Hooks source not found at {hooks_src}\n")
        counts["errors"] += 1
        return counts

    # Map git hook names to thegent hook scripts
    hook_map = {
        "pre-commit": "pre-commit-quality.sh",
        "pre-push": "pre-push-quality.sh",
    }

    for hook_name, default_script in hook_map.items():
        _setup_git_hook(git_hooks, hooks_src, hook_name, default_script, dry_run, counts, verbose)

    return counts


def _setup_git_hook(
    git_hooks: Path,
    hooks_src: Path,
    hook_name: str,
    default_script: str,
    dry_run: bool,
    counts: dict[str, int],
    verbose: bool,
) -> None:
    """Setup a single git hook safely."""
    dst = git_hooks / hook_name
    hook_script = hooks_src / default_script
    if not hook_script.exists():
        fallback_map = {
            "pre-commit": ("pre-commit-docs.sh", "quality-gate.sh"),
            "pre-push": ("quality-gate.sh",),
        }
        candidates = fallback_map.get(hook_name, ("quality-gate.sh",))
        hook_script = next((hooks_src / s for s in candidates if (hooks_src / s).exists()), None)
    if not hook_script or not hook_script.exists():
        return
    wrapper = f"""#!/bin/sh
# thegent setup --hooks
set -e
exec sh "{hook_script}" "$@"
"""
    if dry_run:
        counts["installed"] += 1
        return
    try:
        git_hooks.mkdir(parents=True, exist_ok=True)
        dst.write_text(wrapper)
        dst.chmod(0o755)
        counts["installed"] += 1
        if verbose:
            sys.stdout.write(f"  Installed {hook_name}\n")
    except OSError as e:
        counts["errors"] += 1
        if verbose:
            sys.stdout.write(f"  Failed {hook_name}: {e}\n")


def setup_rust_dispatcher(verbose: bool = False) -> bool:
    """Compile and install the Rust hook-dispatcher if cargo is available."""
    if not _command_exists("cargo"):
        if verbose:
            sys.stdout.write("  Cargo not found; skipping Rust dispatcher compilation.\n")
        return False

    root = _get_thegent_root()
    dispatcher_dir = root / "hooks" / "hook-dispatcher"
    if not dispatcher_dir.exists():
        if verbose:
            sys.stdout.write(f"  Rust dispatcher source not found at {dispatcher_dir}\n")
        return False

    try:
        if verbose:
            sys.stdout.write(f"  Compiling Rust dispatcher in {dispatcher_dir}...\n")
        shim_run(["cargo", "build", "--release"], cwd=str(dispatcher_dir), check=True, capture_output=not verbose)

        # Binary is at target/release/hook-dispatcher
        # Copy or symlink to hooks/bin/hook-dispatcher for easier access
        bin_dir = root / "hooks" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        src_bin = dispatcher_dir / "target" / "release" / "hook-dispatcher"
        dst_bin = bin_dir / "hook-dispatcher"

        if src_bin.exists():
            shutil.copy2(src_bin, dst_bin)
            dst_bin.chmod(0o755)
            if verbose:
                sys.stdout.write(f"  Installed Rust dispatcher to {dst_bin}\n")
            return True
    except subprocess.CalledProcessError as e:
        if verbose:
            sys.stdout.write(f"  Rust dispatcher compilation failed: {e}\n")
        return False
    except Exception as e:
        if verbose:
            sys.stdout.write(f"  Failed to install Rust dispatcher: {e}\n")
        return False
    return False


def setup_harness(verbose: bool = False) -> bool:
    """WP-11006: Install/update heliosShield harness."""
    # Check if heliosShield/install.sh exists relative to thegent
    root = _get_thegent_root()
    # If root is 'thegent' (installed package), we look for it in parent of project root
    # If root is project root (dev), we look for it in root.parent
    install_sh = root.parent / "heliosShield" / "install.sh"

    if not install_sh.exists():
        # Try one more location: workspace root
        install_sh = Path.cwd().parent / "heliosShield" / "install.sh"

    if not install_sh.exists():
        if verbose:
            sys.stdout.write(f"  Harness install script not found at {install_sh}\n")
        return False

    try:
        if verbose:
            sys.stdout.write(f"  Running harness install: {install_sh}\n")
        shim_run(["bash", str(install_sh)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        if verbose:
            sys.stdout.write(f"  Harness install failed: {e}\n")
        return False


def setup_skills(
    cwd: Path | None = None,
    template: str = "thegent-skills",
    dry_run: bool = False,
    verbose: bool = False,
) -> dict[str, int]:
    """Sync skills template to project. Returns counts dict."""
    root = _get_thegent_root()
    skills_src = root / "skills" / template
    cwd = cwd or Path.cwd()
    counts: dict[str, int] = {"copied": 0, "skipped": 0, "errors": 0}

    if not skills_src.exists():
        if verbose:
            sys.stdout.write(f"  Skills template '{template}' not found at {skills_src}\n")
        counts["errors"] += 1
        return counts

    # Targets: ~/.claude/skills, ~/.cursor/rules, project .claude/skills, .cursor/rules
    home = Path.home()
    skill_md = skills_src / "SKILL.md"
    if not skill_md.exists():
        skill_md = next(skills_src.glob("*.md"), None)

    for base_dir in [home / ".claude" / "skills", cwd / ".claude" / "skills"]:
        _sync_base_dir_skills(base_dir, skills_src, dry_run, counts, verbose)

    # Cursor rules: create thegent.mdc from SKILL.md
    if skill_md and skill_md.exists():
        content = skill_md.read_text()
        mdc_content = (
            f"---\nname: thegent-skills\ndescription: Unified orchestration guidance for thegent\n---\n\n{content}"
        )
        for rules_dir in [home / ".cursor" / "rules", cwd / ".cursor" / "rules"]:
            _sync_cursor_rules(rules_dir, mdc_content, dry_run, counts, verbose)

    return counts


def _sync_base_dir_skills(
    base_dir: Path,
    skills_src: Path,
    dry_run: bool,
    counts: dict[str, int],
    verbose: bool,
) -> None:
    """Sync skills to a base directory safely."""
    for name in ["SKILL.md", "skill.json"]:
        src_file = skills_src / name
        if not src_file.exists():
            continue
        dst = base_dir / name
        if dry_run:
            counts["copied"] += 1
            continue
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst)
            counts["copied"] += 1
            if verbose:
                sys.stdout.write(f"  Synced {name} to {base_dir}\n")
        except OSError as e:
            counts["errors"] += 1
            if verbose:
                sys.stdout.write(f"  Failed {dst}: {e}\n")


def _sync_cursor_rules(
    rules_dir: Path,
    mdc_content: str,
    dry_run: bool,
    counts: dict[str, int],
    verbose: bool,
) -> None:
    """Sync cursor rules safely."""
    dst = rules_dir / "thegent.mdc"
    if dry_run:
        counts["copied"] += 1
        return
    try:
        rules_dir.mkdir(parents=True, exist_ok=True)
        dst.write_text(mdc_content)
        counts["copied"] += 1
        if verbose:
            sys.stdout.write(f"  Synced thegent.mdc to {rules_dir}\n")
    except OSError as e:
        counts["errors"] += 1
        if verbose:
            sys.stdout.write(f"  Failed {dst}: {e}\n")


# --- System Dependencies Installation ---


def install_homebrew(console: Console | None = None, dry_run: bool = False) -> tuple[bool, str]:
    """Install Homebrew if not present. Returns (success, message)."""
    if _command_exists("brew"):
        return True, "Homebrew already installed"

    if dry_run:
        return True, "Would install Homebrew"

    if console:
        console.print("[cyan]Installing Homebrew...[/cyan]")

    # Official Homebrew installation script
    install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    rc, stdout, stderr = _run_command(["bash", "-c", install_script], check=False, capture_output=False)

    if rc == 0 or _command_exists("brew"):
        # Note: Avoid global PATH mutation. If brew_path is needed for subprocess calls,
        # construct env dict locally: env = os.environ.copy(); env["PATH"] = ...
        return True, "Homebrew installed successfully"
    return False, f"Homebrew installation failed: {stderr or stdout}"


def install_mise(
    console: Console | None = None,
    dry_run: bool = False,
    use_nix: bool = False,
    settings: "ThegentSettings | None" = None,
) -> tuple[bool, str]:
    """Install mise (formerly rtx) via Homebrew or Nix. Returns (success, message)."""
    if settings is None:
        from thegent.config import ThegentSettings

        settings = ThegentSettings()

    if _command_exists("mise"):
        return True, "mise already installed"

    if dry_run:
        return True, "Would install mise"

    if use_nix:
        if not _command_exists("nix"):
            return False, "Nix not found. Install Nix first or use Homebrew."
        if console:
            console.print("[cyan]Installing mise via Nix...[/cyan]")
        rc, stdout, stderr = _run_command(["nix", "profile", "install", "nixpkgs#mise"])
        if rc == 0:
            return True, "mise installed via Nix"
        return False, f"mise Nix installation failed: {stderr or stdout}"

    # Try Homebrew
    if not _command_exists("brew"):
        installed, msg = install_homebrew(console, dry_run)
        if not installed:
            return False, f"Cannot install mise: {msg}"

    if console:
        console.print("[cyan]Installing mise via Homebrew...[/cyan]")
    rc, stdout, stderr = _run_command(["brew", "install", "mise"])
    if rc == 0:
        # Setup shell hooks automatically
        shell = settings.shell_path
        shell_config_file = None
        hook_cmd = None

        if "zsh" in shell:
            hook_cmd = 'eval "$(mise activate zsh)"'
            # Check for .zshenv first (loaded earlier, better for mise)
            zshenv = Path.home() / ".zshenv"
            if zshenv.exists():
                shell_config_file = zshenv
        elif "fish" in shell:
            hook_cmd = "mise activate fish | source"
            fish_config = Path.home() / ".config" / "fish" / "config.fish"
            shell_config_file = fish_config if fish_config.exists() else fish_config  # noqa: RUF034 -- explicit conditional for clarity
        elif "tcsh" in shell or "csh" in shell:
            hook_cmd = "eval `mise activate tcsh`"
            tcsh_config = Path.home() / ".tcshrc"
            shell_config_file = tcsh_config if tcsh_config.exists() else Path.home() / ".cshrc"
        elif "bash" in shell:
            hook_cmd = 'eval "$(mise activate bash)"'
            shell_config_file = Path.home() / ".bashrc"
        else:
            hook_cmd = 'eval "$(mise activate)"'
            shell_config_file = Path.home() / f".{shell.split('/')[-1]}rc"

        # Add hook if not already present
        if shell_config_file:
            try:
                if not shell_config_file.exists():
                    # Create shell config file if it doesn't exist (especially for .zshenv)
                    shell_config_file.parent.mkdir(parents=True, exist_ok=True)
                    initial_content = (
                        f"# mise hook (fast alternative to direnv)\n# Auto-installed by thegent\n{hook_cmd}\n"
                    )
                    shell_config_file.write_text(initial_content)
                    if console:
                        console.print(f"[green]✓[/green] Created {shell_config_file.name} with mise hook")
                else:
                    # File exists, read and update
                    # Backup before modification
                    _backup_shell_config(shell_config_file, console)
                    # File exists, read and update
                    content = shell_config_file.read_text()
                    if "mise activate" not in content:
                        # Add mise hook before direnv hook if direnv exists
                        if "direnv hook" in content:
                            # Insert before direnv
                            content = content.replace(
                                'eval "$(direnv hook',
                                f"{hook_cmd}\n# direnv hook",
                            )
                        else:
                            # Append at end
                            content = f"{content}\n\n# mise hook (fast alternative to direnv)\n{hook_cmd}\n"
                        shell_config_file.write_text(content)
                        if console:
                            console.print(f"[green]✓[/green] Added mise hook to {shell_config_file.name}")
                    elif console:
                        console.print(f"[dim]mise hook already in {shell_config_file.name}[/dim]")
            except Exception as e:
                if console:
                    console.print(f"[yellow]Could not auto-add mise hook: {e}[/yellow]")
                    console.print(f"[dim]Manually add to {shell_config_file}: {hook_cmd}[/dim]")
        elif console:
            console.print(f"[dim]Add to your shell config: {hook_cmd}[/dim]")

        # PowerShell / Windows: also write pwsh activation hook when detected.
        if _is_powershell_environment():
            ps_profile = detect_powershell_profile()
            write_powershell_mise_hook(ps_profile, console=console, dry_run=dry_run)

        return True, "mise installed via Homebrew"
    return False, f"mise installation failed: {stderr or stdout}"


def verify_mise_installation(
    console: Console | None = None, settings: "ThegentSettings | None" = None
) -> tuple[bool, list[str]]:
    """Verify mise installation and configuration. Returns (success, messages)."""
    if settings is None:
        from thegent.config import ThegentSettings

        settings = ThegentSettings()

    messages = []
    success = True

    # Check if mise is in PATH
    if not _command_exists("mise"):
        messages.append("mise not found in PATH")
        success = False
    else:
        messages.append("mise found in PATH")
        # Get version
        rc, stdout, stderr = _run_command(["mise", "--version"])
        if rc == 0:
            version = stdout.split()[0] if stdout else "unknown"
            messages.append(f"mise version: {version}")
        else:
            messages.append("Could not get mise version")

    # Check if shell hooks are configured
    shell = settings.shell_path
    hook_files = []
    if "zsh" in shell:
        hook_files = [Path.home() / ".zshenv", Path.home() / ".zshrc"]
    if "zsh" in shell:
        hook_files = [Path.home() / ".bashrc"]

    hook_found = False
    for hook_file in hook_files:
        if hook_file.exists():
            try:
                hook_content = hook_file.read_text()
                if "mise activate" in hook_content:
                    messages.append(f"mise hook found in {hook_file.name}")
                    hook_found = True
                    break
            except Exception:
                pass

    if not hook_found:
        messages.append("Warning: mise hook not found in shell config files")
        # Not a failure, just a warning

    # Run mise doctor if available
    if _command_exists("mise"):
        rc, stdout, stderr = _run_command(["mise", "doctor"], capture_output=True)
        if rc == 0:
            messages.append("mise doctor: OK")
        else:
            messages.append(f"mise doctor warnings: {stderr[:200] if stderr else 'unknown'}")

    return success, messages


def uninstall_mise_hooks(
    console: Console | None = None, dry_run: bool = False, settings: "ThegentSettings | None" = None
) -> tuple[bool, list[str]]:
    """Remove mise hooks from shell config files. Returns (success, messages)."""
    if settings is None:
        from thegent.config import ThegentSettings

        settings = ThegentSettings()

    messages = []
    success = True

    shell = settings.shell_path
    hook_files = []
    if "zsh" in shell:
        hook_files = [Path.home() / ".zshenv", Path.home() / ".zshrc"]
    if "zsh" in shell:
        hook_files = [Path.home() / ".bashrc"]
    elif "fish" in shell:
        hook_files = [Path.home() / ".config" / "fish" / "config.fish"]
    elif "tcsh" in shell or "csh" in shell:
        hook_files = [Path.home() / ".tcshrc", Path.home() / ".cshrc"]

    removed_count = 0
    for hook_file in hook_files:
        if hook_file.exists():
            try:
                content = hook_file.read_text()
                if "mise activate" in content:
                    if dry_run:
                        messages.append(f"Would remove mise hook from {hook_file.name}")
                    else:
                        # Remove mise hook lines
                        lines = content.splitlines()
                        new_lines = []
                        skip_next = False
                        for _i, line in enumerate(lines):
                            if "mise activate" in line or "mise hook" in line.lower():
                                skip_next = True
                                continue
                            if skip_next and line.strip() == "":
                                skip_next = False
                                continue
                            skip_next = False
                            new_lines.append(line)

                        hook_file.write_text("\n".join(new_lines) + "\n")
                        messages.append(f"Removed mise hook from {hook_file.name}")
                        removed_count += 1
            except Exception as e:
                messages.append(f"Error removing hook from {hook_file.name}: {e}")
                success = False

    if removed_count == 0:
        messages.append("No mise hooks found to remove")

    return success, messages


def uninstall_system_dependencies(
    console: Console | None = None,
    dry_run: bool = False,
    uninstall_mise_pkg: bool = False,
    remove_hooks: bool = True,
) -> dict[str, Any]:
    """Uninstall system dependencies: remove hooks, optionally uninstall mise.

    Args:
        console: Rich console for output
        dry_run: If True, only show what would be done
        uninstall_mise_pkg: Also uninstall mise package (via brew/nix)
        remove_hooks: Remove shell hooks (default: True)

    Returns:
        dict with uninstall status
    """
    results: dict[str, Any] = {
        "hooks_removed": False,
        "mise_uninstalled": False,
        "messages": [],
    }

    if remove_hooks:
        success, msgs = uninstall_mise_hooks(console, dry_run)
        results["hooks_removed"] = success
        results["messages"].extend(msgs)
        if console:
            for msg in msgs:
                console.print(f"[dim]{msg}[/dim]")

    if uninstall_mise_pkg and not dry_run:
        if _command_exists("brew"):
            if console:
                console.print("[cyan]Uninstalling mise via Homebrew...[/cyan]")
            rc, stdout, stderr = _run_command(["brew", "uninstall", "mise"])
            if rc == 0:
                results["mise_uninstalled"] = True
                results["messages"].append("mise uninstalled via Homebrew")
            else:
                results["messages"].append(f"Failed to uninstall mise: {stderr or stdout}")
        elif _command_exists("nix"):
            if console:
                console.print("[cyan]Uninstalling mise via Nix...[/cyan]")
            rc, stdout, stderr = _run_command(["nix", "profile", "remove", "mise"])
            if rc == 0:
                results["mise_uninstalled"] = True
                results["messages"].append("mise uninstalled via Nix")
            else:
                results["messages"].append(f"Failed to uninstall mise: {stderr or stdout}")
        else:
            results["messages"].append("Neither Homebrew nor Nix found - cannot uninstall mise")

    return results


def clone_git_repo(
    repo_url: str,
    target_dir: Path,
    console: Console | None = None,
    dry_run: bool = False,
    branch: str | None = None,
) -> tuple[bool, str]:
    """Clone a git repository. Returns (success, message)."""
    if not _command_exists("git"):
        return False, "git not found. Install git first."

    if target_dir.exists():
        if (target_dir / ".git").exists():
            return True, f"Repository already exists at {target_dir}"
        return False, f"Directory exists but is not a git repository: {target_dir}"

    if dry_run:
        return True, f"Would clone {repo_url} to {target_dir}"

    if console:
        console.print(f"[cyan]Cloning {repo_url}...[/cyan]")

    cmd = ["git", "clone", repo_url, str(target_dir)]
    if branch:
        cmd.extend(["-b", branch])

    rc, stdout, stderr = _run_command(cmd)
    if rc == 0:
        return True, f"Cloned {repo_url} to {target_dir}"
    return False, f"Git clone failed: {stderr or stdout}"


def install_system_dependencies(
    console: Console | None = None,
    dry_run: bool = False,
    install_homebrew_pkg: bool = True,
    install_mise_pkg: bool = True,
    use_nix: bool = False,
    git_repos: list[dict[str, str]] | None = None,
    install_powershell: bool = False,
) -> dict[str, Any]:
    """Install system-wide dependencies: Homebrew, mise, git repos.

    Args:
        console: Rich console for output
        dry_run: If True, only show what would be done
        install_homebrew_pkg: Install Homebrew if missing
        install_mise_pkg: Install mise if missing
        use_nix: Use Nix instead of Homebrew for mise
        git_repos: List of dicts with 'url', 'target', optional 'branch'
        install_powershell: Write PowerShell mise activation hook explicitly.
            When False (default), the hook is still written automatically
            whenever ``_is_powershell_environment()`` returns True during
            ``install_mise``.  Pass ``True`` to force the write regardless of
            the detected environment (e.g. via ``thegent install --powershell``).

    Returns:
        dict with 'homebrew', 'mise', 'git_repos', 'powershell' status
    """
    results: dict[str, Any] = {
        "homebrew": {"installed": False, "message": ""},
        "mise": {"installed": False, "message": ""},
        "git_repos": [],
        "powershell": {"installed": False, "message": ""},
    }

    if install_homebrew_pkg:
        installed, msg = install_homebrew(console, dry_run)
        results["homebrew"] = {"installed": installed, "message": msg}
        if console and not dry_run:
            status = "[green]✓[/green]" if installed else "[red]✗[/red]"
            console.print(f"{status} Homebrew: {msg}")

    if install_mise_pkg:
        installed, msg = install_mise(console, dry_run, use_nix=use_nix)
        results["mise"] = {"installed": installed, "message": msg}
        if console and not dry_run:
            status = "[green]✓[/green]" if installed else "[red]✗[/red]"
            console.print(f"{status} mise: {msg}")

        # Verify mise installation
        if installed and not dry_run:
            _verify_success, verify_msgs = verify_mise_installation(console)
            if console and verify_msgs:
                console.print("[dim]Verification:[/dim]")
                for verify_msg in verify_msgs:
                    console.print(f"  [dim]{verify_msg}[/dim]")

    if install_powershell:
        ps_profile = detect_powershell_profile()
        ps_ok, ps_msg = write_powershell_mise_hook(ps_profile, console=console, dry_run=dry_run)
        results["powershell"] = {"installed": ps_ok, "message": ps_msg}
        if console and not dry_run:
            status = "[green]✓[/green]" if ps_ok else "[red]✗[/red]"
            console.print(f"{status} PowerShell: {ps_msg}")

    if git_repos:
        for repo_info in git_repos:
            url = repo_info.get("url", "")
            target = repo_info.get("target", "")
            branch = repo_info.get("branch")
            if not url or not target:
                continue
            target_path = Path(target).expanduser()
            installed, msg = clone_git_repo(url, target_path, console, dry_run, branch)
            results["git_repos"].append({"url": url, "target": target, "installed": installed, "message": msg})
            if console and not dry_run:
                status = "[green]✓[/green]" if installed else "[red]✗[/red]"
                console.print(f"{status} Git repo {url}: {msg}")

    return results


def resolve_bundles(
    bundle_names: list[str] | None,
    bundle_manifest: Path | str | None,
    thegent_root: Path,
    home: Path,
    cwd: Path,
    fallback_mode: InstallMode,
) -> list[tuple[Path, Path, InstallMode]]:
    """Resolve selected bundles to install tuples.

    Kept local to preserve test patch points in ``thegent.install``.
    """
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
        copy_file(target, backup_path)
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
                    return cast("FileAction", FileAction.SKIPPED)
            elif mode == InstallMode.INTERACTIVE:
                # In non-interactive shells, this might hang. We should check if sys.stdin.isatty()
                if not sys.stdin.isatty():
                    if self.verbose:
                        sys.stderr.write(f"  Non-interactive shell, skipping conflict: {target}\n")
                    return cast("FileAction", FileAction.CONFLICT)

                choice = Prompt.ask(
                    f"Conflict detected for {target}. [o]verwrite, [s]kip, [b]ackup & overwrite?",
                    choices=["o", "s", "b"],
                    default="s",
                )
                if choice == "s":
                    return cast("FileAction", FileAction.SKIPPED)
                mode = cast("InstallMode", InstallMode.SMART if choice == "b" else InstallMode.FORCE)

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
                action = cast("FileAction", FileAction.SYMLINKED)
            else:
                if source.is_dir():
                    copy_tree(source, target)
                else:
                    copy_file(source, target)
                action = cast("FileAction", FileAction.COPIED)

            # Register in manifest
            self.manifest.files[str(target)] = FileManifest(
                source=str(source),
                target=str(target),
                mode="symlink" if mode == InstallMode.EDITABLE else "copy",
                mtime=target.stat().st_mtime if target.exists() else 0,
                backup=str(backup_path) if backup_path else None,
            )
        else:
            action = cast("FileAction", FileAction.COPIED if mode != InstallMode.EDITABLE else FileAction.SYMLINKED)
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

        config_path.write_text(json.dumps(config, indent=2).decode().decode())

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
                        path.write_text(json.dumps(data, indent=2).decode().decode())
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
                            copy_tree(backup, target)
                        else:
                            copy_file(backup, target)
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


def _update_compatible_mcp_servers(
    mgr: "InstallManager",
    config_path: Path,
    mcp_cfg: dict[str, Any],
) -> None:
    """Write canonical and compatibility MCP keys to the same MCP config."""
    mgr.update_config(config_path, "mcpServers.thegent", mcp_cfg)
    mgr.update_config(config_path, "mcpServers.codex_apps", mcp_cfg)


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
        "6": ("envrc", "~/.envrc (direnv fix)"),
        "7": ("shell", "Shell config (~/.zshenv, .zshrc, etc.)"),
        "8": ("harness", "Harness (Claude Code, Codex, Droid, Cursor + login)"),
    }

    # Simple detection
    home = Path.home()
    detection = {
        "cursor": (home / "Library/Application Support/Cursor").exists() or (home / ".cursor").exists(),
        "claude-code": (home / ".claude").exists(),
        "claude-desktop": (home / "Library/Application Support/Claude").exists(),
        "codex": (home / ".codex").exists(),
        "droid": (home / ".factory").exists(),
        "envrc": True,  # Always relevant for direnv/FUNCNEST fix
        "shell": True,  # Shell config always relevant for optimized startup
        "harness": True,  # CLIProxy config always relevant for provider routing
    }

    for k, (code, name) in targets_map.items():
        detected = detection.get(code, False)
        status = "[green]detected[/green]" if detected else "[dim]not found[/dim]"
        console.print(f"  [cyan]{k}[/cyan]) {name:16} {status}")

    selected_input = Prompt.ask("\nTargets to configure (e.g. 1,2 or 'all')", default="all")

    if selected_input.lower() == "all" or selected_input.lower() == "a":
        selected_targets = [v[0] for v in targets_map.values()]
    else:
        selected_targets = []
        for part in selected_input.replace(",", " ").split():
            if part in targets_map:
                selected_targets.append(targets_map[part][0])
            elif part.lower() == "all" or part.lower() == "a":
                selected_targets = [v[0] for v in targets_map.values()]
                break

    if not selected_targets:
        console.print("[yellow]No targets selected. Exiting.[/yellow]")
        return

    # 2. Mode selection
    console.print("\n[bold]2. Select Mode[/bold]")
    console.print("  [cyan]s[/cyan]) [bold]smart[/bold]    [dim]Copy only if newer (safe, recommended)[/dim]")
    console.print("  [cyan]e[/cyan]) [bold]editable[/bold] [dim]Symlink (best for dev, bi-directional sync)[/dim]")
    console.print("  [cyan]f[/cyan]) [bold]force[/bold]    [dim]Overwrite everything[/dim]")

    mode_input = Prompt.ask("\nChoose mode", choices=["s", "e", "f", "smart", "editable", "force"], default="s")
    mode_map = {
        "s": "smart",
        "e": "editable",
        "f": "force",
        "smart": "smart",
        "editable": "editable",
        "force": "force",
    }
    mode = mode_map[mode_input.lower()]

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

    # 6. Optional: Configure providers (harness login)
    if Confirm.ask("\n[bold]Configure AI providers now?[/bold] (thegent setup / cliproxy login)", default=True):
        try:
            run_subprocess_optimized([sys.executable, "-m", "thegent", "setup"], check=False)
        except Exception:
            console.print(
                "[dim]Run [bold]thegent setup[/bold] or [bold]thegent cliproxy login <provider>[/bold] to configure providers.[/dim]"
            )
    else:
        console.print(
            "[dim]Run [bold]thegent setup[/bold] or [bold]thegent cliproxy login <provider>[/bold] to configure providers.[/dim]"
        )

    console.print("\n[dim]Happy orchestrating![/dim]")


def run_install_project(
    project_selector: str | None = None,
    template: str = "none",
    mode: str = "smart",
    dry_run: bool = False,
    registry_path: Path | None = None,
) -> dict:
    """Install Thegent runtime assets into a registered project directory.

    # @trace FR-TEN-001

    Args:
        project_selector: Project name, tenant_id, or path. If None, uses cwd.
        template: Template overlay ("ag-dd" or "none").
        mode: Install mode ("smart", "overwrite", "skip").
        dry_run: If True, only show what would be changed.
        registry_path: Optional custom registry path (used in tests for isolation).

    Returns:
        dict with keys: project_name, path, template, installed, skipped, errors.
    """
    from thegent.infra.project_tenancy import ProjectTenancy

    if mode not in {"smart", "overwrite", "skip"}:
        raise ValueError(f"Invalid install mode: {mode!r}. Must be: smart, overwrite, skip")

    tenancy = ProjectTenancy(registry_path=registry_path) if registry_path is not None else ProjectTenancy()
    record = None

    if project_selector:
        sel = project_selector.strip()
        # Try name, then tenant_id, then path
        record = tenancy.get_project(name=sel)
        if record is None:
            record = tenancy.get_project(tenant_id=sel)
        if record is None:
            candidate = Path(sel).expanduser().resolve()
            if candidate.exists():
                record = tenancy.get_project(path=candidate)
        if record is None:
            raise KeyError(f"No registered project found for selector: {sel!r}")
    else:
        cwd = Path.cwd()
        record = tenancy.get_project(path=cwd)
        if record is None:
            raise KeyError(f"No registered project found for current directory: {cwd}")

    project_path = Path(record.path)
    thegent_dir = project_path / ".thegent"
    errors: list[str] = []
    installed: list[str] = []
    skipped: list[str] = []

    # Files to install into .thegent/
    assets = {
        "config.yaml": (
            f"# Thegent project config\n"
            f"tenant_id: {record.tenant_id}\n"
            f"project_id: {record.project_id}\n"
            f"project_name: {record.name}\n"
        ),
        "ownership.json": json.dumps(
            {"tenant_id": record.tenant_id, "owner": "default", "project_id": record.project_id},
            indent=2,
        ).decode()
        + "\n",
        "templates.lock": json.dumps(
            {
                "template": record.template,
                "version": record.template_version,
                "locked_at": record.created_at,
            },
            indent=2,
        ).decode()
        + "\n",
    }

    if not dry_run:
        thegent_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in assets.items():
        dest = thegent_dir / filename
        rel = f".thegent/{filename}"
        if dry_run:
            installed.append(f"(dry-run) {rel}")
            continue

        if dest.exists():
            if mode == "skip":
                skipped.append(rel)
                continue
            if mode == "smart":
                existing = dest.read_text(encoding="utf-8")
                if existing == content:
                    skipped.append(rel)
                    continue

        dest.write_text(content, encoding="utf-8")
        installed.append(rel)

    # Optional AG-DD template overlay
    template_installed: list[str] = []
    template_skipped: list[str] = []
    if template == "ag-dd" and not dry_run:
        template_mode_map = {"smart": "smart", "overwrite": "overwrite", "skip": "skip"}
        agdd_result = tenancy.spawn_template_agdd(project_path, mode=template_mode_map[mode])  # type: ignore[arg-type]
        template_installed = agdd_result.installed
        template_skipped = agdd_result.skipped + agdd_result.unchanged

    return {
        "project_name": record.name,
        "path": record.path,
        "template": template,
        "installed": installed + template_installed,
        "skipped": skipped + template_skipped,
        "errors": errors,
    }


def run_install_system(
    prefix: Path = Path("/opt/thegent"),
    dry_run: bool = False,
    verbose: bool = False,
) -> dict:
    """Install thegent for agent-as-system-user. Layout: bin, share/thegent/hooks, etc/thegent, var/lib/thegent."""
    counts: dict[str, int] = {"copied": 0, "skipped": 0, "conflicts": 0, "errors": 0}
    thegent_root = Path(__file__).parent.parent.parent.resolve()
    bin_dir = prefix / "bin"
    hooks_dir = prefix / "share" / "thegent" / "hooks"
    etc_dir = prefix / "etc" / "thegent"
    var_dir = Path("/var/lib/thegent")

    if not dry_run:
        try:
            bin_dir.mkdir(parents=True, exist_ok=True)
            hooks_dir.mkdir(parents=True, exist_ok=True)
            etc_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            counts["errors"] = 1
            sys.stderr.write(f"Permission denied: Cannot create system directories under {prefix}.\n")
            sys.stderr.write(f"  Error: {e}\n")
            sys.stderr.write("  Hint: Use --scope user for user-local installation, or run with sudo for system-wide install.\n")
            return counts
        try:  # noqa: SIM105 -- explicit try/except preferred for clarity
            var_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass  # May need root for /var/lib

    # Copy hooks (exclude build artifacts)
    hooks_src = thegent_root / "hooks"
    if hooks_src.exists():
        for f in hooks_src.iterdir():
            if f.name in ("hook-dispatcher", "__pycache__", ".git") or f.suffix == ".pyc":
                continue
            dst = hooks_dir / f.name
            if f.is_dir() and f.name == "lib":
                if not dry_run:
                    shutil.copytree(f, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                counts["copied"] += 1
            elif f.is_file():
                if not dry_run:
                    shutil.copy2(f, dst)
                counts["copied"] += 1

    # Create bin/thegent wrapper
    thegent_script = """#!/usr/bin/env bash
exec python3 -m thegent.main "$@"
"""
    thegent_bin = bin_dir / "thegent"
    if not dry_run:
        thegent_bin.write_text(thegent_script)
        thegent_bin.chmod(0o755)
    counts["copied"] += 1

    # Placeholder config
    config_file = etc_dir / "config.yaml"
    if not config_file.exists() and not dry_run:
        config_file.write_text("# thegent system config (agent-as-system-user)\n")
    counts["copied"] += 1

    if verbose:
        sys.stdout.write(f"  System install to {prefix} complete.\\n")
        sys.stdout.write(f"  bin: {bin_dir}\\n")
        sys.stdout.write(f"  hooks: {hooks_dir}\\n")
        sys.stdout.write(f"  Run: thegent install-shims --prefix {prefix} for git wrapper\\n")
    return counts


def run_install(
    target: str = "all",
    mode: str = "smart",
    dry_run: bool = False,
    verbose: bool = False,
    url: str | None = None,
    install_service: bool = False,
    bundles: list[str] | None = None,
    bundle_manifest: Path | str | None = None,
    bundle_conflict_policy: str | None = None,
    settings: "ThegentSettings | None" = None,
) -> dict:
    if settings is None:
        from thegent.config import ThegentSettings

        settings = ThegentSettings()

    if target not in VALID_TARGETS and not target.startswith("claude") and target not in ("auto", "all"):
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

    # Use get_targets_for_install to resolve "all", "auto", or comma-separated lists
    targets = get_targets_for_install(target, auto_detect=True)

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

    # WP-S2: Compile and install Rust hook-dispatcher
    if not dry_run:
        setup_rust_dispatcher(verbose=verbose)

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
            _update_compatible_mcp_servers(mgr, home / ".claude.json", mcp_cfg)

        elif t == "claude-desktop":
            if platform.system() == "Darwin":
                p = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
            elif platform.system() == "Windows":
                # Use settings.appdata_path for Windows APPDATA detection
                if settings.appdata_path:
                    p = settings.appdata_path / "Claude" / "claude_desktop_config.json"
                else:
                    p = home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
            else:
                p = home / ".config" / "Claude" / "claude_desktop_config.json"

            if p.parent.exists():
                _update_compatible_mcp_servers(mgr, p, mcp_cfg)

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
            _update_compatible_mcp_servers(mgr, Path.cwd() / ".cursor" / "mcp.json", mcp_cfg)
            # Global level
            _update_compatible_mcp_servers(mgr, home / ".cursor" / "mcp.json", mcp_cfg)

        elif t == "codex":
            for codex_path in [
                home / ".codex" / "mcp.json",
                home / ".config" / "codex" / "mcp.json",
                home / ".codex" / "config.json",
            ]:
                _update_compatible_mcp_servers(mgr, codex_path, mcp_cfg)

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
            _update_compatible_mcp_servers(mgr, Path.cwd() / ".factory" / "mcp.json", mcp_cfg)

        elif t == "envrc":
            # ~/.envrc: guarded direnv config to prevent FUNCNEST recursion in home
            # (use flake only when flake.nix exists; in $HOME there is none)
            src = thegent_root / "shell" / "envrc.home.template"
            dst = home / ".envrc"
            if src.exists():
                res = mgr.install_file(src, dst, install_mode)
                key = res.value if hasattr(res, "value") else str(res)
                counts[key] = counts.get(key, 0) + 1

        elif t == "harness":
            # Harness: set up Claude Code, Codex, Droid, Cursor + ensure-config + run login
            # 1. Install harness configs (claude-code, codex, droid, cursor)
            harness_targets = ["claude-code", "codex", "droid", "cursor"]
            if target == "harness":
                # When harness-only: install the harness configs first
                for ht in harness_targets:
                    if ht == "claude-code":
                        claude_dir = home / ".claude"
                        for src_rel, dst_rel in CLAUDE_CODE_FILES.items():
                            src = thegent_root / src_rel
                            dst = claude_dir / dst_rel
                            if src.exists() and not dry_run:
                                res = mgr.install_file(src, dst, install_mode)
                                key = res.value if hasattr(res, "value") else str(res)
                                counts[key] = counts.get(key, 0) + 1
                        _update_compatible_mcp_servers(
                            mgr,
                            home / ".claude.json",
                            _get_mcp_config(mcp_url, client="claude-code"),
                        )
                    elif ht == "codex":
                        for codex_path in [
                            home / ".codex" / "mcp.json",
                            home / ".config" / "codex" / "mcp.json",
                            home / ".codex" / "config.json",
                        ]:
                            _update_compatible_mcp_servers(
                                mgr,
                                codex_path,
                                _get_mcp_config(mcp_url, client="codex"),
                            )
                    elif ht == "droid":
                        factory_dir = home / ".factory"
                        for src_rel, dst_rel in FACTORY_FILES.items():
                            src = thegent_root / src_rel
                            dst = factory_dir / dst_rel
                            if src.exists() and not dry_run:
                                res = mgr.install_file(src, dst, install_mode)
                                key = res.value if hasattr(res, "value") else str(res)
                                counts[key] = counts.get(key, 0) + 1
                        _update_compatible_mcp_servers(
                            mgr,
                            Path.cwd() / ".factory" / "mcp.json",
                            _get_mcp_config(mcp_url, client="droid"),
                        )
                    elif ht == "cursor":
                        cursor_dir = home / ".cursor"
                        for src_rel, dst_rel in CURSOR_FILES.items():
                            src = thegent_root / src_rel
                            dst = cursor_dir / dst_rel
                            if src.exists() and not dry_run:
                                res = mgr.install_file(src, dst, install_mode)
                                key = res.value if hasattr(res, "value") else str(res)
                                counts[key] = counts.get(key, 0) + 1
                        _update_compatible_mcp_servers(
                            mgr,
                            Path.cwd() / ".cursor" / "mcp.json",
                            _get_mcp_config(mcp_url, client="cursor"),
                        )
                        _update_compatible_mcp_servers(
                            mgr,
                            home / ".cursor" / "mcp.json",
                            _get_mcp_config(mcp_url, client="cursor"),
                        )

            # 2. ensure-config (cliproxy harness config)
            if not dry_run:
                try:
                    from thegent.agents.cliproxy_manager import _ensure_config
                    from thegent.config import ThegentSettings

                    config_path = _ensure_config(ThegentSettings())
                    if verbose:
                        sys.stdout.write(f"  Harness config: {config_path}\n")
                    counts["copied"] = counts.get("copied", 0) + 1
                except Exception as e:
                    counts["errors"] = counts.get("errors", 0) + 1
                    if verbose:
                        sys.stdout.write(f"  Harness ensure-config: {e}\n")
            elif verbose:
                sys.stdout.write("  Would run cliproxy ensure-config\n")

            # 3. Run login for harness providers (Claude Code, Codex, Droid, Cursor)
            # Providers: claude, codex (OAuth); minimax, glm, antigravity, cursor, roo, kilo (API/OAuth)
            if not dry_run and sys.stdin.isatty():
                try:
                    run_subprocess_optimized(
                        [
                            sys.executable,
                            "-m",
                            "thegent",
                            "setup",
                            "--agents",
                            "claude,codex,minimax,glm,antigravity,cursor,roo,kilo",
                            "--no-wizard",
                        ],
                        check=False,
                    )
                except Exception:
                    if verbose:
                        sys.stdout.write("  Run thegent cliproxy login <provider> to configure providers.\n")

        elif t == "shell":
            # Shell config: zshenv, zsh_bundle, safeguards, optimization, advanced, zshrc
            shell_dir = thegent_root / "shell"
            for name in SHELL_FILES:
                src = shell_dir / name
                dst = home / name
                if src.exists():
                    res = mgr.install_file(src, dst, install_mode)
                    key = res.value if hasattr(res, "value") else str(res)
                    counts[key] = counts.get(key, 0) + 1
            # zshrc.local: copy only if missing (never overwrite user customizations)
            src_local = shell_dir / SHELL_LOCAL_TEMPLATE
            dst_local = home / ".zshrc.local"
            if src_local.exists() and not dst_local.exists():
                res = mgr.install_file(src_local, dst_local, cast("InstallMode", InstallMode.SMART))
                key = res.value if hasattr(res, "value") else str(res)
                counts[key] = counts.get(key, 0) + 1

        elif t == "git-lock-cleanup":
            from thegent.git_lock_manage import lock_cleanup_install, lock_cleanup_start

            ok, msg = lock_cleanup_install()
            if ok:
                if verbose:
                    sys.stdout.write(f"  {msg}\n")
                lock_cleanup_start()
                counts["copied"] += 1
            else:
                counts["errors"] += 1
                if verbose:
                    sys.stdout.write(f"  Failed: {msg}\n")

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
