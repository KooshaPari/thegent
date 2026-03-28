"""Cycle execution module.

Handles sync cycle execution - extracted to reduce runner size.
"""

import logging
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from phenotype_thegent_sync.integrations.workstream_autosync_shared import (
    SyncDirection,
    WorkstreamParser,
)

logger = logging.getLogger(__name__)


async def run_sync_cycle(runner) -> dict[str, Any]:
    """Execute one complete sync cycle.

    This is the main cycle logic - extracted to reduce runner size.
    """
    result = {
        "started_at": datetime.now(UTC).isoformat(),
        "items_count": 0,
        "error": None,
    }

    try:
        # Load local items
        items = await _load_local_items(runner)
        result["items_count"] = len(items)

        if not items:
            result["skipped"] = "no_items"
            return result

        # Determine direction
        direction = _determine_direction(runner)

        # Execute sync based on direction
        if direction == SyncDirection.LOCAL_TO_REMOTE:
            await _sync_to_remote(runner, items)
        elif direction == SyncDirection.REMOTE_TO_LOCAL:
            await _sync_from_remote(runner, items)
        elif direction == SyncDirection.BIDIRECTIONAL:
            await _sync_bidirectional(runner, items)

        result["status"] = "success"

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Cycle error: {e}")

    result["completed_at"] = datetime.now(UTC).isoformat()
    return result


async def _load_local_items(runner) -> list:
    """Load items from local workstream file."""
    workstream_path = runner.config.work_stream_path
    if not workstream_path or not workstream_path.exists():
        return []

    try:
        parser = WorkstreamParser()
        return parser.parse_file(workstream_path)
    except Exception as e:
        logger.error(f"Failed to load items: {e}")
        return []


def _determine_direction(runner) -> SyncDirection:
    """Determine sync direction from config."""
    gh = runner.config.github_enabled
    lin = runner.config.linear_enabled

    if gh and lin:
        return SyncDirection.BIDIRECTIONAL
    if gh:
        return SyncDirection.LOCAL_TO_REMOTE
    if lin:
        return SyncDirection.REMOTE_TO_LOCAL
    return SyncDirection.NONE


async def _sync_to_remote(runner, items: list) -> None:
    """Sync items to remote platforms."""
    if runner.config.github_enabled:
        await _sync_to_github(runner, items)
    if runner.config.linear_enabled:
        await _sync_to_linear(runner, items)


async def _sync_from_remote(runner, items: list) -> None:
    """Sync items from remote platforms."""
    workstream_path = runner.config.work_stream_path
    if runner.config.github_enabled:
        await _sync_from_github(runner, items, workstream_path)
    if runner.config.linear_enabled:
        await _sync_from_linear(runner, items, workstream_path)


async def _sync_bidirectional(runner, items: list) -> None:
    """Sync in both directions."""
    await _sync_to_remote(runner, items)
    await _sync_from_remote(runner, items)


async def _sync_to_github(runner, items: list) -> dict[str, Any]:
    """Sync to GitHub - delegates to sync module."""
    from phenotype_thegent_sync.autosync.github_sync import sync_to_github

    return await sync_to_github(runner, items)


async def _sync_from_github(runner, items: list, path: Path) -> list:
    """Sync from GitHub - delegates to sync module."""
    from phenotype_thegent_sync.autosync.github_sync import sync_from_github

    return await sync_from_github(runner, items, path)


async def _sync_to_linear(runner, items: list) -> dict[str, Any]:
    """Sync to Linear - delegates to sync module."""
    from phenotype_thegent_sync.autosync.linear_sync import sync_to_linear

    return await sync_to_linear(runner, items)


async def _sync_from_linear(runner, items: list, path: Path) -> list:
    """Sync from Linear - delegates to sync module."""
    from phenotype_thegent_sync.autosync.linear_sync import sync_from_linear

    return await sync_from_linear(runner, items, path)


__all__ = ["run_sync_cycle"]
