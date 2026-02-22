"""GitHub Projects v2 Bidirectional Sync Integration (WL-157).

Provides optional, standalone-safe bidirectional syncing with GitHub Projects v2.
Skips gracefully when disabled or when gh auth lacks project scope.

Key Principles:
- Standalone-safe: No crash or side effects when disabled or gh auth missing
- Optional: Fully backward compatible; can be disabled entirely
- Bidirectional: Read/write thegent workstream to/from GitHub Projects
- Composable: Works with existing WORK_STREAM.md format
"""

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)


@dataclass
class GHProjectConfig:
    """Configuration for GitHub Projects sync."""

    enabled: bool
    owner: str
    number: int
    direction: Literal["read_only", "write_only", "bidirectional"]
    standalone_mode: bool

    def is_valid(self) -> bool:
        """Check if config is valid for sync operations."""
        return self.enabled and bool(self.owner) and self.number > 0

    def can_read(self) -> bool:
        """Check if sync direction allows reading."""
        return self.direction in ("read_only", "bidirectional")

    def can_write(self) -> bool:
        """Check if sync direction allows writing."""
        return self.direction in ("write_only", "bidirectional")


class GHProjectSyncError(Exception):
    """Base exception for GitHub Projects sync errors."""



class GHProjectAuthError(GHProjectSyncError):
    """Authentication/authorization error (e.g., missing project scope)."""



class GHProjectNotFoundError(GHProjectSyncError):
    """Project not found error."""



def _check_gh_command() -> bool:
    """Check if gh CLI is available.

    Returns:
        True if gh is available and callable, False otherwise.
    """
    return shutil.which("gh") is not None


def _run_gh_command(args: list[str], capture: bool = True) -> tuple[int, str, str]:
    """Run gh CLI command safely.

    Args:
        args: Command arguments (without 'gh' prefix)
        capture: If True, capture stdout/stderr; if False, stream to console

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        GHProjectAuthError: If command fails due to auth issues
        GHProjectSyncError: For other gh CLI errors
    """
    if not _check_gh_command():
        raise GHProjectSyncError("gh CLI not found on PATH")

    try:
        cmd = ["gh"] + args
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=30,
            check=False,
        )

        # Check for auth-related errors
        if result.returncode == 1:
            stderr_lower = result.stderr.lower()
            if "auth" in stderr_lower or "permission" in stderr_lower or "project" in stderr_lower:
                raise GHProjectAuthError(
                    f"GitHub authentication issue: {result.stderr[:200]}"
                )

        if result.returncode != 0:
            raise GHProjectSyncError(f"gh command failed: {result.stderr[:200]}")

        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired as e:
        raise GHProjectSyncError(f"gh command timeout: {e}")
    except Exception as e:
        raise GHProjectSyncError(f"gh command error: {e}")


def get_project_status(config: GHProjectConfig) -> dict[str, Any]:
    """Get GitHub Project sync status.

    Args:
        config: GitHub Projects configuration

    Returns:
        Dict with project metadata, item count, and sync status.
        Returns empty dict if sync disabled or auth unavailable.

    Raises:
        GHProjectSyncError: For unexpected errors (not auth issues)
    """
    if not config.is_valid():
        if config.standalone_mode:
            logger.debug("GH Project sync not configured or disabled; skipping status")
            return {"enabled": False, "reason": "not_configured"}
        raise GHProjectSyncError("GitHub project config invalid")

    try:
        # Query project info via gh API
        query = f"owner:{config.owner} number:{config.number}"
        code, stdout, _ = _run_gh_command(
            [
                "project",
                "view",
                query,
                "--format",
                "json",
            ]
        )

        if code == 0:
            data = json.loads(stdout)
            return {
                "enabled": True,
                "owner": config.owner,
                "number": config.number,
                "title": data.get("title", ""),
                "url": data.get("url", ""),
                "items": data.get("items", []),
                "synced_at": None,
                "direction": config.direction,
            }
        return {"enabled": True, "status": "unavailable", "reason": "query_failed"}

    except GHProjectAuthError as e:
        if config.standalone_mode:
            logger.warning(f"GH Project auth issue (standalone mode, skipping): {e}")
            return {"enabled": True, "status": "auth_required", "reason": str(e)}
        raise
    except GHProjectSyncError:
        raise


def sync_to_github(
    config: GHProjectConfig,
    workstream_data: list[dict[str, Any]],
) -> dict[str, Any]:
    """Sync thegent workstream to GitHub Projects.

    Args:
        config: GitHub Projects configuration
        workstream_data: Workstream items (from WORK_STREAM.md or similar)

    Returns:
        Dict with sync results: items_created, items_updated, errors

    Raises:
        GHProjectSyncError: For unexpected errors (not auth issues)
    """
    if not config.is_valid() or not config.can_write():
        if config.standalone_mode:
            logger.debug(
                "GH Project sync not configured or read-only; skipping write sync"
            )
            return {"items_synced": 0, "reason": "not_writable"}
        raise GHProjectSyncError("GitHub project not writable")

    try:
        # Verify project exists and sync direction is correct
        query = f"owner:{config.owner} number:{config.number}"
        _run_gh_command(
            [
                "project",
                "view",
                query,
                "--format",
                "json",
            ]
        )

        # TODO: Implement actual item creation/update logic
        # For now, return mock response (actual implementation requires gh API for item creation)
        return {
            "items_created": 0,
            "items_updated": 0,
            "errors": [],
            "synced_at": None,
        }

    except GHProjectAuthError as e:
        if config.standalone_mode:
            logger.warning(f"GH Project auth issue (standalone mode, skipping): {e}")
            return {
                "items_created": 0,
                "items_updated": 0,
                "errors": [str(e)],
                "status": "auth_required",
            }
        raise
    except GHProjectSyncError:
        raise


def sync_from_github(config: GHProjectConfig) -> dict[str, Any]:
    """Sync GitHub Projects to thegent workstream.

    Args:
        config: GitHub Projects configuration

    Returns:
        Dict with sync results: items_imported, errors

    Raises:
        GHProjectSyncError: For unexpected errors (not auth issues)
    """
    if not config.is_valid() or not config.can_read():
        if config.standalone_mode:
            logger.debug(
                "GH Project sync not configured or write-only; skipping read sync"
            )
            return {"items_imported": 0, "reason": "not_readable"}
        raise GHProjectSyncError("GitHub project not readable")

    try:
        # Query project items via gh API
        query = f"owner:{config.owner} number:{config.number}"
        code, stdout, _ = _run_gh_command(
            [
                "project",
                "item-list",
                query,
                "--format",
                "json",
            ]
        )

        if code == 0:
            items = json.loads(stdout)
            return {
                "items_imported": len(items),
                "items": items,
                "errors": [],
                "synced_at": None,
            }
        return {"items_imported": 0, "status": "failed"}

    except GHProjectAuthError as e:
        if config.standalone_mode:
            logger.warning(f"GH Project auth issue (standalone mode, skipping): {e}")
            return {"items_imported": 0, "status": "auth_required", "reason": str(e)}
        raise
    except GHProjectSyncError:
        raise


def export_to_csv(
    config: GHProjectConfig,
    output_path: Path,
) -> dict[str, Any]:
    """Export GitHub Project to CSV.

    Args:
        config: GitHub Projects configuration
        output_path: Path to write CSV export

    Returns:
        Dict with export results: items_exported, file_path
    """
    if not config.is_valid() or not config.can_read():
        if config.standalone_mode:
            logger.debug("GH Project sync not configured or write-only; skipping export")
            return {"items_exported": 0, "reason": "not_readable"}
        raise GHProjectSyncError("GitHub project not readable")

    try:
        query = f"owner:{config.owner} number:{config.number}"
        code, stdout, _ = _run_gh_command(
            [
                "project",
                "item-list",
                query,
                "--format",
                "csv",
            ]
        )

        if code == 0:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(stdout)
            return {
                "items_exported": len(stdout.splitlines()),
                "file_path": str(output_path),
            }
        return {"items_exported": 0, "status": "failed"}

    except GHProjectAuthError as e:
        if config.standalone_mode:
            logger.warning(f"GH Project auth issue (standalone mode, skipping): {e}")
            return {"items_exported": 0, "status": "auth_required", "reason": str(e)}
        raise
    except GHProjectSyncError:
        raise


def import_from_csv(
    config: GHProjectConfig,
    csv_path: Path,
) -> dict[str, Any]:
    """Import items to GitHub Project from CSV.

    Args:
        config: GitHub Projects configuration
        csv_path: Path to CSV file to import

    Returns:
        Dict with import results: items_imported, errors
    """
    if not config.is_valid() or not config.can_write():
        if config.standalone_mode:
            logger.debug("GH Project sync not configured or read-only; skipping import")
            return {"items_imported": 0, "reason": "not_writable"}
        raise GHProjectSyncError("GitHub project not writable")

    if not csv_path.exists():
        raise GHProjectSyncError(f"CSV file not found: {csv_path}")

    try:
        # Verify project exists
        query = f"owner:{config.owner} number:{config.number}"
        _run_gh_command(
            [
                "project",
                "view",
                query,
                "--format",
                "json",
            ]
        )

        # TODO: Implement actual CSV import via gh API
        # For now, return mock response
        return {
            "items_imported": 0,
            "errors": [],
        }

    except GHProjectAuthError as e:
        if config.standalone_mode:
            logger.warning(f"GH Project auth issue (standalone mode, skipping): {e}")
            return {
                "items_imported": 0,
                "errors": [str(e)],
                "status": "auth_required",
            }
        raise
    except GHProjectSyncError:
        raise


# End of file

