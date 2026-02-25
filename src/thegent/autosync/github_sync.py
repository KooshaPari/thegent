"""GitHub sync operations.

Extracts GitHub API logic from main runner.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from thegent.integrations.gh_project_sync import (
    GHProjectConfig,
    sync_from_github as gh_sync_from,
    sync_to_github as gh_sync_to,
)
from thegent.integrations.sync_provenance import (
    enrich_sync_metadata,
    propagate_owner_metadata,
)

logger = logging.getLogger(__name__)


async def sync_to_github(runner, items: list) -> dict[str, Any]:
    """Sync items to GitHub."""
    if not runner.config.github_can_write():
        return {"skipped": True, "reason": "github not writable"}

    try:
        # Enrich items with metadata
        enriched = _enrich_items(runner, items)

        # Check shadow mode
        if runner.config.shadow_mode:
            logger.info(f"Shadow mode: blocking {len(items)} GitHub mutations")
            return {"success": True, "shadow": True}

        # Check dry run
        if runner.config.dry_run:
            logger.info(f"Dry-run: skip GitHub write ({len(items)} items)")
            return {"success": True, "dry_run": True}

        # Execute sync
        config = GHProjectConfig(
            enabled=True,
            owner=runner.config.github_owner,
            number=runner.config.effective_github_project_number(),
            direction=runner.config.github_direction.value,
        )

        result = await asyncio.to_thread(gh_sync_to, config, enriched)
        return {"success": True, "result": result}

    except Exception as e:
        logger.error(f"GitHub sync error: {e}")
        return {"error": str(e)}


async def sync_from_github(runner, items: list, path: Path) -> list:
    """Sync items from GitHub."""
    if not runner.config.github_enabled:
        return []

    try:
        config = GHProjectConfig(
            enabled=True,
            owner=runner.config.github_owner,
            number=runner.config.effective_github_project_number(),
        )
        return await asyncio.to_thread(gh_sync_from, config)
    except Exception as e:
        logger.error(f"GitHub sync error: {e}")
        return []


def _enrich_items(runner, items: list) -> list:
    """Enrich items with metadata."""
    fallback_owner = runner.config.actor_id.strip()
    enriched = []

    for item in items:
        metadata = enrich_sync_metadata(
            item.to_dict(),
            source_url=f"github://workstream/{item.item_id}",
            source_tag="github",
        )
        owner = item.owner.strip() if item.owner else ""
        if not owner:
            owner = fallback_owner
        if owner:
            metadata = propagate_owner_metadata(metadata, owner=owner)
        enriched.append(metadata)

    return enriched


__all__ = ["sync_from_github", "sync_to_github"]
