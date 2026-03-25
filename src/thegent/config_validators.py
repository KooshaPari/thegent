"""Validators for thegent configuration.

Extracted from config.py for maintainability.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol


class _SettingsLike(Protocol):
    """Subset of settings fields validated by this module."""

    session_dir: Path | str | None
    factory_skills_dir: Path | str | None
    default_timeout_claude: int
    default_timeout: int


def parse_retention_by_domain(v: object) -> dict[str, int]:
    """Parse retention_by_domain from various formats.

    Args:
        v: Input value (string, dict, or None)

    Returns:
        Dict mapping domains to retention days
    """
    if v is None:
        return {}

    if isinstance(v, dict):
        # Ensure all values are ints
        return {k: int(v) for k, v in v.items()}

    if isinstance(v, str):
        # Parse "domain:days,domain:days" format
        result = {}
        for part in v.split(","):
            if ":" in part:
                domain, days = part.split(":", 1)
                result[domain.strip()] = int(days.strip())
        return result

    return {}


def parse_env_allowlist(v: object) -> list[str]:
    """Parse sandbox_env_allowlist from various formats.

    Args:
        v: Input value (string, list, or None)

    Returns:
        List of allowed environment variable names
    """
    if v is None:
        return []

    if isinstance(v, list):
        return [str(x) for x in v]

    if isinstance(v, str):
        # Parse comma or newline separated
        if "," in v:
            return [x.strip() for x in v.split(",") if x.strip()]
        return [x.strip() for x in v.split("\n") if x.strip()]

    return []


def parse_zen_api_key(v: object) -> str:
    """Parse zen_api_key, stripping whitespace.

    Args:
        v: Input value

    Returns:
        Cleaned API key string
    """
    if v is None:
        return ""

    return str(v).strip()


def parse_virtual_env(v: object) -> Path | None:
    """Parse virtual_env path.

    Args:
        v: Input value (path string or None)

    Returns:
        Path object or None
    """
    if v is None or v == "":
        return None

    path = Path(str(v)).expanduser()

    if not path.is_absolute():
        # Relative to home
        path = Path.home() / path

    return path


def parse_shell_path(v: object) -> str:
    """Parse shell_path, defaulting to /bin/zsh.

    Args:
        v: Input value

    Returns:
        Shell path string
    """
    if v is None or v == "":
        return "/bin/zsh"

    return str(v)


def parse_appdata_path(v: object) -> Path | None:
    """Parse appdata_path for Windows.

    Args:
        v: Input value

    Returns:
        Path object or None
    """
    if v is None or v == "":
        return None

    return Path(str(v)).expanduser()


def parse_check_leaks(v: object) -> bool:
    """Parse check_leaks boolean.

    Args:
        v: Input value (bool, string, int)

    Returns:
        Boolean value
    """
    if isinstance(v, bool):
        return v

    if isinstance(v, str):
        return v.lower() in ("true", "1", "yes", "on")

    if isinstance(v, int):
        return bool(v)

    return False


def parse_testing_mode(v: object) -> bool:
    """Parse testing_mode boolean.

    Args:
        v: Input value

    Returns:
        Boolean value
    """
    return parse_check_leaks(v)  # Same logic


def parse_mac_keep_awake_agents(v: object) -> list[str]:
    """Parse mac_keep_awake_agents list.

    Args:
        v: Input value (string, list, or None)

    Returns:
        List of agent names
    """
    if v is None:
        return ["claude", "codex", "gemini"]

    if isinstance(v, list):
        return [str(x) for x in v]

    if isinstance(v, str):
        return [x.strip() for x in v.split(",") if x.strip()]

    return ["claude", "codex", "gemini"]


def validate_settings_setup(settings: _SettingsLike) -> list[str]:
    """Validate settings for common issues.

    Args:
        settings: Settings object to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check session directory is writable
    session_dir = settings.session_dir
    if session_dir:
        session_dir_path = Path(session_dir).expanduser()
        session_dir_path.mkdir(parents=True, exist_ok=True)
        if not os.access(session_dir_path, os.W_OK):
            errors.append(f"Session directory not writable: {session_dir_path}")

    # Check factory directories exist
    skills_dir = settings.factory_skills_dir
    if skills_dir and not Path(skills_dir).expanduser().exists():
        errors.append(f"Factory skills directory does not exist: {skills_dir}")

    # Validate timeouts
    if settings.default_timeout_claude < settings.default_timeout:
        errors.append("default_timeout_claude must be >= default_timeout")

    return errors


__all__ = [
    "parse_retention_by_domain",
    "parse_env_allowlist",
    "parse_zen_api_key",
    "parse_virtual_env",
    "parse_shell_path",
    "parse_appdata_path",
    "parse_check_leaks",
    "parse_testing_mode",
    "parse_mac_keep_awake_agents",
    "validate_settings_setup",
]
