"""Install module for managed installation and synchronization of thegent components."""

import json
import os
import platform
import shutil
import subprocess
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

from thegent.infra import copy_file, copy_tree, run_subprocess_optimized

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


def _get_thegent_root() -> Path:
    """Return thegent root (has hooks/, skills/). Works for dev and installed package."""
    # Installed: hooks/skills are force-included at thegent/hooks, thegent/skills
    try:
        import thegent
        pkg = Path(thegent.__file__).resolve().parent
        if (pkg / "hooks").exists() or (pkg / "skills").exists():
            return pkg
    except Exception:
        pass
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
        "pre-commit": "quality-gate.sh",  # Primary; fallback to pre-commit-docs if project has docs
        "pre-push": "quality-gate.sh",
    }

    for hook_name, default_script in hook_map.items():
        dst = git_hooks / hook_name
        hook_script = hooks_src / default_script
        if not hook_script.exists():
            hook_script = next((hooks_src / s for s in ("pre-commit-docs.sh", "quality-gate.sh") if (hooks_src / s).exists()), None)
        if not hook_script or not hook_script.exists():
            continue
        wrapper = f"""#!/bin/sh
# thegent setup --hooks
set -e
exec sh "{hook_script}" "$@"
"""
        if dry_run:
            counts["installed"] += 1
            continue
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

    return counts


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
    skill_json = skills_src / "skill.json"
    if not skill_md.exists():
        skill_md = next(skills_src.glob("*.md"), None)

    for base_dir in [home / ".claude" / "skills", cwd / ".claude" / "skills"]:
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

    # Cursor rules: create thegent.mdc from SKILL.md
    if skill_md and skill_md.exists():
        content = skill_md.read_text()
        mdc_content = f"---\nname: thegent-skills\ndescription: Unified orchestration guidance for thegent\n---\n\n{content}"
        for rules_dir in [home / ".cursor" / "rules", cwd / ".cursor" / "rules"]:
            dst = rules_dir / "thegent.mdc"
            if dry_run:
                counts["copied"] += 1
                continue
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

    return counts


def _service_plist_exists() -> bool:
    """Compatibility helper for wizard preflight paths.

    Some setup paths call this helper directly; keep it available even when
    wizard flow is simplified.
    """
    if platform.system() != "Darwin":
        return False
    plist = Path.home() / "Library" / "LaunchAgents" / "com.thegent.mcp.plist"
    return plist.exists()


# --- System Dependencies Installation ---


def _command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(cmd) is not None


def _run_command(
    cmd: list[str],
    check: bool = False,
    capture_output: bool = True,
    retries: int = 3,
    retry_delay: float = 1.0,
) -> tuple[int, str, str]:
    """Run a shell command with retry logic. Returns (returncode, stdout, stderr)."""
    import time

    last_error = None
    for attempt in range(retries):
        try:
            result = run_subprocess_optimized(
                cmd, check=check, capture_output=capture_output, timeout=300
            )
            stdout_text = result.stdout.strip() if isinstance(result.stdout, str) else (result.stdout.decode("utf-8", errors="replace").strip() if result.stdout else "")
            stderr_text = result.stderr.strip() if isinstance(result.stderr, str) else (result.stderr.decode("utf-8", errors="replace").strip() if result.stderr else "")
            return result.returncode, stdout_text, stderr_text
        except subprocess.TimeoutExpired:
            last_error = "Command timed out"
            if attempt < retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            return 1, "", last_error
        except Exception as e:
            last_error = str(e)
            last_error = str(e)
            # Retry on network errors or temporary failures
            if attempt < retries - 1 and any(keyword in str(e).lower() for keyword in ['network', 'connection', 'timeout', 'temporary']):
                time.sleep(retry_delay * (attempt + 1))
                continue
            return 1, "", last_error

    return 1, "", last_error or "Command failed after retries"


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




def _backup_shell_config(hook_file: Path, console: Console | None = None) -> Path | None:
    """Backup shell config file before modification. Returns backup path or None."""
    if not hook_file.exists():
        return None

    backup_dir = Path.home() / ".thegent" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"{hook_file.name}.{timestamp}.bak"

    try:
        import shutil
        shutil.copy2(hook_file, backup_file)
        if console:
            console.print(f"[dim]Backed up {hook_file.name} to {backup_file}[/dim]")
        return backup_file
    except Exception as e:
        if console:
            console.print(f"[yellow]Could not backup {hook_file.name}: {e}[/yellow]")
        return None

def install_mise(console: Console | None = None, dry_run: bool = False, use_nix: bool = False, settings: "ThegentSettings | None" = None) -> tuple[bool, str]:
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
            hook_cmd = 'mise activate fish | source'
            fish_config = Path.home() / ".config" / "fish" / "config.fish"
            shell_config_file = fish_config if fish_config.exists() else fish_config
        elif "tcsh" in shell or "csh" in shell:
            hook_cmd = 'eval `mise activate tcsh`'
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
                    initial_content = f"# mise hook (fast alternative to direnv)\n# Auto-installed by thegent\n{hook_cmd}\n"
                    shell_config_file.write_text(initial_content)
                    if console:
                        console.print(f"[green]✓[/green] Created {shell_config_file.name} with mise hook")
                else:
                    # File exists, read and update
                    # Backup before modification
                    backup_path = _backup_shell_config(shell_config_file, console)
                    # File exists, read and update
                    content = shell_config_file.read_text()
                    if "mise activate" not in content:
                        # Add mise hook before direnv hook if direnv exists
                        if "direnv hook" in content:
                            # Insert before direnv
                            content = content.replace(
                                'eval "$(direnv hook',
                                f'{hook_cmd}\n# direnv hook',
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
        return True, "mise installed via Homebrew"
    return False, f"mise installation failed: {stderr or stdout}"



def verify_mise_installation(console: Console | None = None, settings: "ThegentSettings | None" = None) -> tuple[bool, list[str]]:
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



def uninstall_mise_hooks(console: Console | None = None, dry_run: bool = False, settings: "ThegentSettings | None" = None) -> tuple[bool, list[str]]:
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



def restore_shell_config(backup_path: Path, console: Console | None = None) -> tuple[bool, str]:
    """Restore shell config from backup. Returns (success, message)."""
    if not backup_path.exists():
        return False, f"Backup file not found: {backup_path}"

    # Determine original file path from backup name
    # Format: .zshenv.20260218_123456.bak
    backup_name = backup_path.name
    if '.bak' not in backup_name:
        return False, "Invalid backup file format"

    original_name = backup_name.rsplit('.', 2)[0]  # Remove .timestamp.bak
    original_path = Path.home() / original_name

    try:
        import shutil
        shutil.copy2(backup_path, original_path)
        if console:
            console.print(f"[green]✓[/green] Restored {original_name} from backup")
        return True, f"Restored {original_name} from {backup_path.name}"
    except Exception as e:
        return False, f"Restore failed: {e}"


def list_backups(console: Console | None = None) -> list[Path]:
    """List all available backups. Returns list of backup paths."""
    backup_dir = Path.home() / ".thegent" / "backups"
    if not backup_dir.exists():
        return []

    backups = sorted(backup_dir.glob("*.bak"), key=lambda p: p.stat().st_mtime, reverse=True)
    return backups


def cleanup_old_backups(keep_count: int = 10, console: Console | None = None) -> tuple[int, list[str]]:
    """Remove old backups, keeping only the most recent ones.

    Args:
        keep_count: Number of backups to keep (default: 10)
        console: Rich console for output

    Returns:
        (removed_count, removed_files)
    """
    backups = list_backups(console)
    if len(backups) <= keep_count:
        return 0, []

    to_remove = backups[keep_count:]
    removed_files = []

    for backup in to_remove:
        try:
            backup.unlink()
            removed_files.append(backup.name)
            if console:
                console.print(f"[dim]Removed old backup: {backup.name}[/dim]")
        except Exception as e:
            if console:
                console.print(f"[yellow]Could not remove {backup.name}: {e}[/yellow]")

    return len(removed_files), removed_files

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
) -> dict[str, Any]:
    """Install system-wide dependencies: Homebrew, mise, git repos.

    Args:
        console: Rich console for output
        dry_run: If True, only show what would be done
        install_homebrew_pkg: Install Homebrew if missing
        install_mise_pkg: Install mise if missing
        use_nix: Use Nix instead of Homebrew for mise
        git_repos: List of dicts with 'url', 'target', optional 'branch'

    Returns:
        dict with 'homebrew', 'mise', 'git_repos' status
    """
    results: dict[str, Any] = {
        "homebrew": {"installed": False, "message": ""},
        "mise": {"installed": False, "message": ""},
        "git_repos": [],
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


def get_bundle_manifest_path(bundle_manifest: Path | str | None = None) -> Path:
    """Get the bundle manifest path.

    Args:
        bundle_manifest: Optional path to a bundle manifest file.

    Returns:
        The path to the bundle manifest file.
    """
    if bundle_manifest is not None:
        return _coerce_path(str(bundle_manifest))
    return get_default_bundle_manifest_path()


def list_bundle_names(bundle_manifest: Path | str | None = None) -> list[str]:
    """List available bundle names from the bundle manifest.

    Args:
        bundle_manifest: Optional path to a bundle manifest file.

    Returns:
        List of bundle names available in the bundle manifest.
    """
    manifest = load_bundle_manifest(bundle_manifest)
    return list(manifest.keys())


def validate_bundle_manifest(bundle_manifest: Path | str | None = None) -> tuple[bool, list[str]]:
    """Validate a bundle manifest file.

    Args:
        bundle_manifest: Optional path to a bundle manifest file.

    Returns:
        Tuple of (is_valid, list of issues).
    """
    issues: list[str] = []
    manifest_path = bundle_manifest or get_default_bundle_manifest_path()

    if manifest_path and isinstance(manifest_path, (str, Path)):
        path = Path(manifest_path) if not isinstance(manifest_path, Path) else manifest_path
        if not path.exists():
            issues.append(f"Bundle manifest not found: {path}")
            return False, issues

        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError, ValueError) as e:
            issues.append(f"Failed to parse bundle manifest: {e}")
            return False, issues

        if not isinstance(data, dict):
            issues.append("Bundle manifest must be a JSON object")
            return False, issues

        bundles = data.get("bundles")
        if not isinstance(bundles, dict):
            issues.append("Bundle manifest must have a 'bundles' object")
            return False, issues

        for name, bundle in bundles.items():
            if not isinstance(name, str):
                issues.append("Bundle name must be a string")
                continue
            if not isinstance(bundle, dict):
                issues.append(f"Bundle '{name}' must be an object")
                continue
            items = bundle.get("items")
            if not isinstance(items, list):
                issues.append(f"Bundle '{name}' must have an 'items' array")
                continue
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    issues.append(f"Bundle '{name}' item {i} must be an object")
                    continue
                if "source" not in item:
                    issues.append(f"Bundle '{name}' item {i} missing 'source'")
                if "target" not in item:
                    issues.append(f"Bundle '{name}' item {i} missing 'target'")

    return len(issues) == 0, issues


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
VALID_TARGETS = {
    "claude-code",
    "claude-desktop",
    "cursor",
    "codex",
    "droid",
    "envrc",
    "shell",
    "system",
    "git-lock-cleanup",
    "all",
    "claude",
    "factory",
    "both",
}

# Shell config: source (in shell/) -> target (in home)
SHELL_FILES = {
    ".zshenv": ".zshenv",
    ".zsh_bundle.zsh": ".zsh_bundle.zsh",
    ".zsh_safeguards.zsh": ".zsh_safeguards.zsh",
    ".zsh_optimization.zsh": ".zsh_optimization.zsh",
    ".zsh_advanced.zsh": ".zsh_advanced.zsh",
    ".zshrc": ".zshrc",
}
SHELL_LOCAL_TEMPLATE = "zshrc.local.template"  # Copy only if ~/.zshrc.local missing

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
    "skills/thegent-skills": "skills/thegent-skills",
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
    "skills/thegent-skills": "skills-cursor/thegent-skills",
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
                    copy_tree(source, target)
                else:
                    copy_file(source, target)
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
        bin_dir.mkdir(parents=True, exist_ok=True)
        hooks_dir.mkdir(parents=True, exist_ok=True)
        etc_dir.mkdir(parents=True, exist_ok=True)
        try:
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

    targets = [target] if target != "all" else ["claude-code", "claude-desktop", "cursor", "codex", "droid", "envrc", "shell", "git-lock-cleanup"]

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
                # Use settings.appdata_path for Windows APPDATA detection
                if settings.appdata_path:
                    p = settings.appdata_path / "Claude" / "claude_desktop_config.json"
                else:
                    p = home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
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

        elif t == "envrc":
            # ~/.envrc: guarded direnv config to prevent FUNCNEST recursion in home
            # (use flake only when flake.nix exists; in $HOME there is none)
            src = thegent_root / "shell" / "envrc.home.template"
            dst = home / ".envrc"
            if src.exists():
                res = mgr.install_file(src, dst, install_mode)
                key = res.value if hasattr(res, "value") else str(res)
                counts[key] = counts.get(key, 0) + 1

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
                res = mgr.install_file(src_local, dst_local, InstallMode.SMART)
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
