"""Proactive doctor --fix command for thegent environment self-healing.

Provides DoctorCheck dataclass and DoctorRunner class that perform 7 lightweight
environment checks and apply automatic fixes where possible.

# @trace FR-CLI-002
"""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class DoctorCheck:
    """Result of a single environment check."""

    name: str
    status: Literal["ok", "warn", "error"]
    message: str
    fixable: bool = False
    _fix_fn: Callable[[], str] | None = field(default=None, repr=False, compare=False)

    def apply_fix(self) -> str | None:
        """Execute the fix action. Returns a description string on success, None if not fixable."""
        if not self.fixable or self._fix_fn is None:
            return None
        return self._fix_fn()


class DoctorRunner:
    """Runs environment checks and applies automatic fixes.

    Checks performed:
      1. Python version >= 3.11
      2. ANTHROPIC_API_KEY env var set
      3. ~/.thegent/ directory exists
      4. ~/.thegent/sessions/ directory exists
      5. pyproject.toml present in cwd
      6. ruff available on PATH
      7. cargo available on PATH
      8. ~/.config/thegent/ MCP config dir exists
    """

    def run_checks(self) -> list[DoctorCheck]:
        """Run all environment checks and return results."""
        checks: list[DoctorCheck] = []
        checks.append(self._check_python_version())
        checks.append(self._check_anthropic_api_key())
        checks.append(self._check_thegent_dir())
        checks.append(self._check_thegent_sessions_dir())
        checks.append(self._check_pyproject_toml())
        checks.append(self._check_ruff())
        checks.append(self._check_cargo())
        checks.append(self._check_mcp_config_dir())
        return checks

    def apply_fixes(self, checks: list[DoctorCheck]) -> list[str]:
        """Apply fixes for all fixable failing checks.

        Args:
            checks: List of DoctorCheck results from run_checks().

        Returns:
            List of human-readable strings describing each fix that was applied.
        """
        applied: list[str] = []
        for check in checks:
            if check.status in ("warn", "error") and check.fixable:
                result = check.apply_fix()
                if result is not None:
                    applied.append(result)
        return applied

    # ------------------------------------------------------------------
    # Individual check implementations
    # ------------------------------------------------------------------

    def _check_python_version(self) -> DoctorCheck:
        major, minor, micro = sys.version_info[:3]
        version_str = f"{major}.{minor}.{micro}"

        if major > 3 or (major == 3 and minor >= 11):
            return DoctorCheck(
                name="python_version",
                status="ok",
                message=f"Python {version_str} >= 3.11",
            )
        return DoctorCheck(
            name="python_version",
            status="warn",
            message=f"Python {version_str} < 3.11; upgrade recommended for full compatibility",
            fixable=False,
        )

    def _check_anthropic_api_key(self) -> DoctorCheck:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if key:
            masked = key[:8] + "..." if len(key) > 8 else "***"
            return DoctorCheck(
                name="ANTHROPIC_API_KEY",
                status="ok",
                message=f"ANTHROPIC_API_KEY is set ({masked})",
            )
        return DoctorCheck(
            name="ANTHROPIC_API_KEY",
            status="warn",
            message="ANTHROPIC_API_KEY is not set; direct Anthropic API calls will fail",
            fixable=False,
        )

    def _check_thegent_dir(self) -> DoctorCheck:
        thegent_dir = Path.home() / ".thegent"

        if thegent_dir.is_dir():
            return DoctorCheck(
                name="thegent_home_dir",
                status="ok",
                message=f"{thegent_dir} exists",
            )

        def _fix() -> str:
            thegent_dir.mkdir(parents=True, exist_ok=True)
            return f"Created {thegent_dir}"

        return DoctorCheck(
            name="thegent_home_dir",
            status="error",
            message=f"{thegent_dir} does not exist",
            fixable=True,
            _fix_fn=_fix,
        )

    def _check_thegent_sessions_dir(self) -> DoctorCheck:
        sessions_dir = Path.home() / ".thegent" / "sessions"

        if sessions_dir.is_dir():
            return DoctorCheck(
                name="thegent_sessions_dir",
                status="ok",
                message=f"{sessions_dir} exists",
            )

        def _fix() -> str:
            sessions_dir.mkdir(parents=True, exist_ok=True)
            return f"Created {sessions_dir}"

        return DoctorCheck(
            name="thegent_sessions_dir",
            status="error",
            message=f"{sessions_dir} does not exist",
            fixable=True,
            _fix_fn=_fix,
        )

    def _check_pyproject_toml(self) -> DoctorCheck:
        pyproject = Path.cwd() / "pyproject.toml"

        if pyproject.is_file():
            return DoctorCheck(
                name="pyproject_toml",
                status="ok",
                message=f"pyproject.toml found at {pyproject}",
            )
        return DoctorCheck(
            name="pyproject_toml",
            status="warn",
            message=f"pyproject.toml not found in {Path.cwd()}; run from project root",
            fixable=False,
        )

    def _check_ruff(self) -> DoctorCheck:
        ruff_path = shutil.which("ruff")
        if ruff_path:
            return DoctorCheck(
                name="ruff",
                status="ok",
                message=f"ruff found at {ruff_path}",
            )
        return DoctorCheck(
            name="ruff",
            status="warn",
            message="ruff not found on PATH; install with: pip install ruff",
            fixable=False,
        )

    def _check_cargo(self) -> DoctorCheck:
        cargo_path = shutil.which("cargo")
        if cargo_path:
            return DoctorCheck(
                name="cargo",
                status="ok",
                message=f"cargo found at {cargo_path}",
            )
        return DoctorCheck(
            name="cargo",
            status="warn",
            message="cargo not found on PATH; native Rust binaries may not build (install rustup from https://rustup.rs)",
            fixable=False,
        )

    def _check_mcp_config_dir(self) -> DoctorCheck:
        mcp_config_dir = Path.home() / ".config" / "thegent"

        if mcp_config_dir.is_dir():
            return DoctorCheck(
                name="mcp_config_dir",
                status="ok",
                message=f"{mcp_config_dir} exists",
            )

        def _fix() -> str:
            mcp_config_dir.mkdir(parents=True, exist_ok=True)
            return f"Created {mcp_config_dir}"

        return DoctorCheck(
            name="mcp_config_dir",
            status="error",
            message=f"MCP config dir {mcp_config_dir} does not exist",
            fixable=True,
            _fix_fn=_fix,
        )
