"""Linear sync operations.

Extracts Linear API logic from main runner.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from phenotype_thegent_sync.integrations.linear_graphql import (
    LinearGraphQLConfig,
    sync_from_linear as linear_sync_from,
    sync_to_linear as linear_sync_to,
)

logger = logging.getLogger(__name__)


async def sync_to_linear(runner, items: list) -> dict[str, Any]:
    """Sync items to Linear."""
    if not runner.config.linear_enabled:
        return {"skipped": True, "reason": "linear disabled"}

    try:
        config = LinearGraphQLConfig(
            api_key=runner.config.linear_api_key,
            team_id=runner.config.linear_team_id,
        )

        if runner.config.shadow_mode:
            logger.info(f"Shadow mode: blocking {len(items)} Linear mutations")
            return {"success": True, "shadow": True}

        if runner.config.dry_run:
            logger.info(f"Dry-run: skip Linear write ({len(items)} items)")
            return {"success": True, "dry_run": True}

        result = await asyncio.to_thread(linear_sync_to, items, config)
        return {"success": True, "result": result}

    except Exception as e:
        logger.error(f"Linear sync error: {e}")
        return {"error": str(e)}


async def sync_from_linear(runner, items: list, path: Path) -> list:
    """Sync items from Linear."""
    if not runner.config.linear_enabled:
        return []

    try:
        config = LinearGraphQLConfig(
            api_key=runner.config.linear_api_key,
            team_id=runner.config.linear_team_id,
        )
        return await asyncio.to_thread(linear_sync_from, config)
    except Exception as e:
        logger.error(f"Linear sync error: {e}")
        return []


__all__ = ["sync_from_linear", "sync_to_linear"]
