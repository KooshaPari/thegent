"""System installation functions for thegent.

Handles Homebrew, mise, and system dependency installation.
Extracted from install.py for maintainability.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Console

if TYPE_CHECKING:
    from thegent.config import ThegentSettings

logger = logging.getLogger(__name__)


def _command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(cmd) is not None


def _run_command(
    cmd: list[str],
    *,
    check: bool = True,
    capture_output: bool = True,
    cwd: Path | str | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    
    result = subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        cwd=cwd,
        env=run_env,
    )
    
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, stdout, stderr
        )
    
    return result.returncode, stdout, stderr


def install_homebrew(
    console: Console | None = None,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """Install Homebrew if not present.
    
    Args:
        console: Rich console for output
        dry_run: If True, don't make changes
        
    Returns:
        Tuple of (success, message)
    """
    if _command_exists("brew"):
        return True, "Homebrew already installed"

    if dry_run:
        return True, "Would install Homebrew"

    if console:
        console.print("[cyan]Installing Homebrew...[/cyan]")

    # Official Homebrew installation script
    install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    rc, stdout, stderr = _run_command(
        ["bash", "-c", install_script],
        check=False,
        capture_output=False,
    )

    if rc == 0 or _command_exists("brew"):
        return True, "Homebrew installed successfully"
    return False, f"Homebrew installation failed: {stderr or stdout}"


def install_mise(
    console: Console | None = None,
    dry_run: bool = False,
    use_nix: bool = False,
    settings: "ThegentSettings | None" = None,
) -> tuple[bool, str]:
    """Install mise (formerly rtx) via Homebrew or Nix.
    
    Args:
        console: Rich console for output
        dry_run: If True, don't make changes
        use_nix: If True, use Nix instead of Homebrew
        settings: Thegent settings
        
    Returns:
        Tuple of (success, message)
    """
    if settings is None:
        from thegent.config import ThegentSettings
        settings = ThegentSettings()

    if _command_exists("mise"):
        return True, "mise already installed"

    if dry_run:
        return True, "Would install mise"

    if use_nix:
        return _install_mise_nix(console)
    
    return _install_mise_homebrew(console, settings)


def _install_mise_nix(console: Console | None) -> tuple[bool, str]:
    """Install mise via Nix."""
    if not _command_exists("nix"):
        return False, "Nix not found. Install Nix first or use Homebrew."
    
    if console:
        console.print("[cyan]Installing mise via Nix...[/cyan]")
    
    rc, stdout, stderr = _run_command(
        ["nix", "profile", "install", "nixpkgs#mise"]
    )
    
    if rc == 0:
        return True, "mise installed via Nix"
    return False, f"mise Nix installation failed: {stderr or stdout}"


def _install_mise_homebrew(
    console: Console | None,
    settings: "ThegentSettings",
) -> tuple[bool, str]:
    """Install mise via Homebrew."""
    if not _command_exists("brew"):
        installed, msg = install_homebrew(console, dry_run=False)
        if not installed:
            return False, f"Cannot install mise: {msg}"

    if console:
        console.print("[cyan]Installing mise via Homebrew...[/cyan]")
    
    rc, stdout, stderr = _run_command(["brew", "install", "mise"])
    
    if rc != 0:
        return False, f"mise installation failed: {stderr or stdout}"
    
    # Setup shell hooks
    _setup_mise_shell_hooks(settings)
    
    return True, "mise installed via Homebrew"


def _setup_mise_shell_hooks(settings: "ThegentSettings") -> None:
    """Setup mise shell hooks in the appropriate config file."""
    shell = getattr(settings, "shell_path", "/bin/zsh")
    shell_config_file = None
    hook_cmd = None

    if "zsh" in shell:
        hook_cmd = 'eval "$(mise activate zsh)"'
        zshenv = Path.home() / ".zshenv"
        if zshenv.exists():
            shell_config_file = zshenv
        else:
            shell_config_file = Path.home() / ".zshrc"
    elif "fish" in shell:
        hook_cmd = "mise activate fish | source"
        fish_config = Path.home() / ".config" / "fish" / "config.fish"
        shell_config_file = fish_config
    elif "bash" in shell:
        hook_cmd = 'eval "$(mise activate bash)"'
        bashrc = Path.home() / ".bashrc"
        if bashrc.exists():
            shell_config_file = bashrc
        else:
            shell_config_file = Path.home() / ".bash_profile"

    if shell_config_file and hook_cmd:
        _add_hook_to_config(shell_config_file, hook_cmd)


def _add_hook_to_config(config_file: Path, hook_cmd: str) -> None:
    """Add a hook command to a shell config file if not already present."""
    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(f"# mise activation\n{hook_cmd}\n")
        return
    
    content = config_file.read_text()
    if "mise activate" not in content:
        with open(config_file, "a") as f:
            f.write(f"\n# mise activation\n{hook_cmd}\n")


def verify_mise_installation(console: Console | None = None) -> bool:
    """Verify mise is properly installed and configured.
    
    Args:
        console: Rich console for output
        
    Returns:
        True if mise is properly configured
    """
    if not _command_exists("mise"):
        if console:
            console.print("[red]mise not found in PATH[/red]")
        return False
    
    # Check mise version
    rc, stdout, stderr = _run_command(
        ["mise", "version"],
        check=False,
    )
    
    if rc != 0:
        if console:
            console.print(f"[red]mise version check failed: {stderr}[/red]")
        return False
    
    if console:
        console.print(f"[green]mise version: {stdout.strip()}[/green]")
    
    return True


def uninstall_mise_hooks(console: Console | None = None) -> bool:
    """Remove mise hooks from shell config files.
    
    Args:
        console: Rich console for output
        
    Returns:
        True if hooks were removed successfully
    """
    config_files = [
        Path.home() / ".zshrc",
        Path.home() / ".zshenv",
        Path.home() / ".bashrc",
        Path.home() / ".bash_profile",
        Path.home() / ".config" / "fish" / "config.fish",
    ]
    
    removed = False
    for config_file in config_files:
        if config_file.exists():
            content = config_file.read_text()
            if "mise activate" in content:
                lines = content.split("\n")
                new_lines = [
                    line for line in lines
                    if "mise activate" not in line
                    and "# mise activation" not in line
                ]
                config_file.write_text("\n".join(new_lines))
                if console:
                    console.print(f"[yellow]Removed mise hooks from {config_file}[/yellow]")
                removed = True
    
    return removed


def uninstall_system_dependencies(
    console: Console | None = None,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """Uninstall system dependencies installed by thegent.
    
    Args:
        console: Rich console for output
        dry_run: If True, don't make changes
        
    Returns:
        Tuple of (success, message)
    """
    if dry_run:
        return True, "Would uninstall system dependencies"
    
    # Remove mise hooks
    uninstall_mise_hooks(console)
    
    # Note: We don't uninstall Homebrew or mise itself as they may be used by other tools
    if console:
        console.print("[green]System dependencies uninstalled[/green]")
    
    return True, "System dependencies uninstalled"


def clone_git_repo(
    url: str,
    target: Path,
    *,
    depth: int = 1,
    branch: str | None = None,
    console: Console | None = None,
) -> tuple[bool, str]:
    """Clone a git repository.
    
    Args:
        url: Repository URL
        target: Target directory
        depth: Clone depth (default: 1 for shallow clone)
        branch: Specific branch to clone
        console: Rich console for output
        
    Returns:
        Tuple of (success, message)
    """
    if target.exists():
        return True, f"Directory already exists: {target}"
    
    cmd = ["git", "clone", "--depth", str(depth)]
    
    if branch:
        cmd.extend(["--branch", branch])
    
    cmd.extend([url, str(target)])
    
    if console:
        console.print(f"[cyan]Cloning {url}...[/cyan]")
    
    rc, stdout, stderr = _run_command(cmd, check=False)
    
    if rc != 0:
        return False, f"Clone failed: {stderr or stdout}"
    
    return True, f"Cloned to {target}"


def install_system_dependencies(
    console: Console | None = None,
    dry_run: bool = False,
    settings: "ThegentSettings | None" = None,
) -> tuple[bool, str]:
    """Install all system dependencies.
    
    Args:
        console: Rich console for output
        dry_run: If True, don't make changes
        settings: Thegent settings
        
    Returns:
        Tuple of (success, message)
    """
    messages = []
    
    # Install Homebrew
    if not _command_exists("brew"):
        success, msg = install_homebrew(console, dry_run)
        messages.append(msg)
        if not success:
            return False, "\n".join(messages)
    
    # Install mise
    success, msg = install_mise(console, dry_run, settings=settings)
    messages.append(msg)
    if not success:
        return False, "\n".join(messages)
    
    return True, "\n".join(messages)


__all__ = [
    "install_homebrew",
    "install_mise",
    "verify_mise_installation",
    "uninstall_mise_hooks",
    "uninstall_system_dependencies",
    "clone_git_repo",
    "install_system_dependencies",
    "_command_exists",
    "_run_command",
]
