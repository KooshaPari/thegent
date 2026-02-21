"""PowerShell-specific install helpers for mise shell activation."""

import os
import sys
from pathlib import Path

from rich.console import Console

from thegent.install_backups import backup_shell_config

POWERSHELL_MISE_HOOK = (
    "if (Get-Command mise -ErrorAction SilentlyContinue) { mise activate pwsh | Out-String | Invoke-Expression }"
)

# Sentinel comment written alongside the hook so idempotency checks work correctly.
POWERSHELL_HOOK_SENTINEL = "# mise hook - auto-installed by thegent"


def is_powershell_environment() -> bool:
    """Return True when the active shell is PowerShell or the platform is Windows."""
    if sys.platform == "win32":
        return True
    shell_env = os.environ.get("SHELL", "").lower()
    return "pwsh" in shell_env or "powershell" in shell_env


def detect_powershell_profile() -> Path:
    """Return the PowerShell profile path for the current user."""
    profile_env = os.environ.get("PROFILE", "").strip()
    if profile_env:
        return Path(profile_env)

    home = Path.home()
    win_ps5 = home / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
    ps7 = home / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"

    if ps7.exists():
        return ps7
    return win_ps5


def write_powershell_mise_hook(
    profile_path: Path,
    console: Console | None = None,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """Append the mise activation hook to a PowerShell profile file (idempotent)."""
    hook_block = f"\n{POWERSHELL_HOOK_SENTINEL}\n{POWERSHELL_MISE_HOOK}\n"

    if dry_run:
        return True, f"Would append mise hook to {profile_path}"

    if profile_path.exists():
        existing = profile_path.read_text(encoding="utf-8")
        if "mise activate pwsh" in existing:
            if console:
                console.print(f"[dim]mise hook already in {profile_path.name}[/dim]")
            return True, f"mise hook already present in {profile_path}"
        backup_shell_config(profile_path, console)
        profile_path.write_text(existing + hook_block, encoding="utf-8")
    else:
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_path.write_text(hook_block.lstrip("\n"), encoding="utf-8")

    if console:
        console.print(f"[green]✓[/green] Added mise hook to {profile_path}")
    return True, f"mise hook written to {profile_path}"
