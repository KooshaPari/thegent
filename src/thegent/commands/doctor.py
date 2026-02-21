"""Proactive doctor --fix command for thegent environment self-healing.

Provides DoctorCheck dataclass and DoctorRunner class that perform 7 lightweight
environment checks and apply automatic fixes where possible.

# @trace FR-CLI-002
"""

from __future__ import annotations

import os
import shutil
import sys
import time
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
      1.  Python version >= 3.11
      2.  ANTHROPIC_API_KEY env var set
      3.  ~/.thegent/ directory exists
      4.  ~/.thegent/ directory is writable (fix: chmod 700)
      5.  ~/.thegent/sessions/ directory exists
      6.  pyproject.toml present in cwd
      7.  .thegent/config.yaml is valid YAML (fix: thegent config wizard)
      8.  ruff available on PATH
      9.  cargo available on PATH
      10. ~/.config/thegent/ MCP config dir exists
      11. .shadow-* stale directory cleanup
      12. .shadow-* directory count > 50 warning
    """

    def run_checks(self) -> list[DoctorCheck]:
        """Run all environment checks and return results.

        # @trace WL-040 WP-4006
        """
        checks: list[DoctorCheck] = []
        checks.append(self._check_python_version())
        checks.append(self._check_anthropic_api_key())
        checks.append(self._check_thegent_dir())
        checks.append(self._check_thegent_dir_writable())
        checks.append(self._check_thegent_sessions_dir())
        checks.append(self._check_pyproject_toml())
        checks.append(self._check_config_yaml())
        checks.append(self._check_ruff())
        checks.append(self._check_cargo())
        checks.append(self._check_mcp_config_dir())
        checks.append(self._check_stale_shadow_dirs())
        checks.append(self._check_shadow_dirs_count())
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

    def _check_stale_shadow_dirs(self) -> DoctorCheck:
        root = Path.cwd()
        parent = root.parent
        max_age_hours = int(os.environ.get("THGENT_SHADOW_STALE_HOURS", "24"))
        cutoff_ts = time.time() - (max_age_hours * 3600)
        stale: list[Path] = []
        for p in parent.iterdir():
            if not p.is_dir() or not p.name.startswith(".shadow-"):
                continue
            try:
                if p.stat().st_mtime < cutoff_ts:
                    stale.append(p)
            except OSError:
                continue

        if not stale:
            return DoctorCheck(
                name="stale_shadow_dirs",
                status="ok",
                message=f"No stale .shadow-* dirs older than {max_age_hours}h in {parent}",
            )

        def _fix() -> str:
            removed = 0
            for d in stale:
                shutil.rmtree(d, ignore_errors=False)
                removed += 1
            return f"Removed {removed} stale .shadow-* directories from {parent}"

        return DoctorCheck(
            name="stale_shadow_dirs",
            status="warn",
            message=f"Found {len(stale)} stale .shadow-* dirs older than {max_age_hours}h in {parent}",
            fixable=True,
            _fix_fn=_fix,
        )

    def _check_thegent_dir_writable(self) -> DoctorCheck:
        """Check that ~/.thegent/ is writable and has correct permissions.

        # @trace WL-040 WP-4006
        """
        thegent_dir = Path.home() / ".thegent"

        if not thegent_dir.exists():
            # The other check will catch the missing dir
            return DoctorCheck(
                name="thegent_dir_writable",
                status="ok",
                message="~/.thegent/ not yet created (will be fixed by thegent_home_dir check)",
            )

        if os.access(thegent_dir, os.W_OK):
            return DoctorCheck(
                name="thegent_dir_writable",
                status="ok",
                message=f"{thegent_dir} is writable",
            )

        def _fix() -> str:
            import subprocess

            subprocess.run(["chmod", "700", str(thegent_dir)], check=True, timeout=5)
            return f"chmod 700 {thegent_dir}"

        return DoctorCheck(
            name="thegent_dir_writable",
            status="error",
            message=f"{thegent_dir} is not writable; agent operations will fail",
            fixable=True,
            _fix_fn=_fix,
        )

    def _check_config_yaml(self) -> DoctorCheck:
        """Check that .thegent/config.yaml (if present) is valid YAML.

        # @trace WL-040 WP-4006
        """
        config_path = Path.home() / ".thegent" / "config.yaml"

        if not config_path.exists():
            # Config file is optional — absence is not an error
            return DoctorCheck(
                name="config_yaml",
                status="ok",
                message=f"{config_path} not present (will be created on first run)",
            )

        try:
            import yaml  # type: ignore[import-untyped]

            with config_path.open("r", encoding="utf-8") as fh:
                parsed = yaml.safe_load(fh)
            if parsed is None or isinstance(parsed, dict):
                return DoctorCheck(
                    name="config_yaml",
                    status="ok",
                    message=f"{config_path} is valid YAML",
                )
            return DoctorCheck(
                name="config_yaml",
                status="warn",
                message=f"{config_path} has unexpected type ({type(parsed).__name__}); expected mapping",
                fixable=False,
            )
        except Exception as exc:
            return DoctorCheck(
                name="config_yaml",
                status="error",
                message=f"{config_path} is invalid YAML: {exc}. Run `thegent config wizard` to set up.",
                fixable=False,
            )

    def _check_shadow_dirs_count(self) -> DoctorCheck:
        """Warn if there are > 50 .shadow-* directories (potential resource leak).

        # @trace WL-040 WP-4006
        """
        parent = Path.cwd().parent
        try:
            shadow_dirs = [p for p in parent.iterdir() if p.is_dir() and p.name.startswith(".shadow-")]
        except OSError:
            shadow_dirs = []

        count = len(shadow_dirs)
        threshold = int(os.environ.get("THGENT_SHADOW_COUNT_WARN", "50"))

        if count <= threshold:
            return DoctorCheck(
                name="shadow_dirs_count",
                status="ok",
                message=f"{count} .shadow-* dir(s) in {parent} (threshold: {threshold})",
            )

        return DoctorCheck(
            name="shadow_dirs_count",
            status="warn",
            message=(
                f"High number of .shadow-* dirs: {count} in {parent}. "
                "Consider running `thegent mcp prune --shadow-dirs` to clean up."
            ),
            fixable=False,
        )
