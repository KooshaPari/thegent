"""Dotfiles manager: deploy tool configs from thegent templates to ~/."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import rtoml

TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "templates" / "shared"
HOME = Path.home()
PROFILES_TOML = TEMPLATES_DIR / "dotfiles-profiles.toml"

# Fallback profiles if TOML file is not present
_FALLBACK_PROFILES: dict[str, dict[str, Any]] = {
    "work-macos": {
        "tools": ["git", "gh", "neovim", "ripgrep", "fzf", "bat", "eza", "zoxide", "starship.toml"],
        "description": "Full macOS development environment",
    },
    "home-linux": {
        "tools": ["git", "gh", "ripgrep", "fzf", "bat", "eza", "zoxide"],
        "description": "Linux home setup",
    },
    "wsl": {
        "tools": ["git", "gh", "ripgrep", "fzf"],
        "description": "Minimal WSL setup",
    },
    "minimal": {
        "tools": ["git"],
        "description": "Bare minimum: just git",
    },
}


def _load_profiles() -> dict[str, dict[str, Any]]:
    """Load profiles from TOML config or fall back to built-ins."""
    if PROFILES_TOML.is_file():
        data = rtoml.load(PROFILES_TOML)
        return data.get("profiles", _FALLBACK_PROFILES)
    return _FALLBACK_PROFILES


def get_profiles() -> dict[str, dict[str, Any]]:
    """Return all available deployment profiles."""
    return _load_profiles()


def list_tools() -> list[str]:
    """Return all available tool configs in templates/shared/.

    Includes both directory-based tool configs and standalone config files.
    """
    if not TEMPLATES_DIR.exists():
        msg = f"Templates directory not found: {TEMPLATES_DIR}"
        raise FileNotFoundError(msg)
    return sorted(p.name for p in TEMPLATES_DIR.iterdir())


def _resolve_dest(src: Path, tool_root: Path) -> Path:
    """Map a template file to its destination path under HOME.

    Files inside a tool directory are placed relative to HOME preserving
    their relative path under the tool directory.  Standalone config files
    (e.g. starship.toml) are placed directly under HOME.
    """
    rel = src.relative_to(tool_root)
    return HOME / rel


def install_tool(tool: str, *, dry_run: bool = False, backup: bool = True) -> dict[str, Any]:
    """Deploy a single tool's config to ~/.

    Args:
        tool: Name of the tool (matches a path under templates/shared/).
        dry_run: If True, compute what would happen without writing.
        backup: If True, rename existing files to *.bak before overwriting.

    Returns:
        Result dict with keys: tool, status, files (list of deployed paths).
    """
    tool_path = TEMPLATES_DIR / tool
    if not tool_path.exists():
        return {"tool": tool, "status": "not_found", "files": []}

    deployed: list[str] = []

    if tool_path.is_file():
        # Standalone config file (e.g. starship.toml)
        dst = HOME / tool
        if not dry_run:
            if backup and dst.exists():
                dst.rename(dst.with_suffix(dst.suffix + ".bak"))
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tool_path, dst)
        deployed.append(str(dst))
    else:
        # Directory of config files
        for src in tool_path.rglob("*"):
            if src.is_file():
                dst = _resolve_dest(src, tool_path)
                if not dry_run:
                    if backup and dst.exists():
                        dst.rename(dst.with_suffix(dst.suffix + ".bak"))
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                deployed.append(str(dst))

    if not deployed:
        return {"tool": tool, "status": "empty", "files": []}

    return {"tool": tool, "status": "dry_run" if dry_run else "installed", "files": deployed}


def install_profile(profile: str, *, dry_run: bool = False, backup: bool = True) -> list[dict[str, Any]]:
    """Deploy all tools in a named profile.

    Args:
        profile: Profile name (must exist in profiles config).
        dry_run: If True, compute what would happen without writing.
        backup: If True, back up existing files before overwriting.

    Returns:
        List of result dicts, one per tool.
    """
    profiles = get_profiles()
    if profile not in profiles:
        msg = f"Unknown profile '{profile}'. Available: {', '.join(profiles)}"
        raise ValueError(msg)

    tools: list[str] = profiles[profile].get("tools", [])
    return [install_tool(t, dry_run=dry_run, backup=backup) for t in tools]
