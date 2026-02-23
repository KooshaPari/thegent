"""Linear sync operations for workstream autosync.

Extracts Linear sync logic from workstream_autosync.py.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from thegent.integrations.linear_graphql import (
    LinearGraphQLAuthError,
    LinearGraphQLConfig,
    LinearGraphQLError,
    sync_from_linear as linear_sync_from,
    sync_to_linear as linear_sync_to,
)
from thegent.integrations.workstream_autosync_shared import WorkstreamItem

logger = logging.getLogger(__name__)


class LinearSync:
    """Handles Linear sync operations."""

    def __init__(self, config: Any, connector_timeout: float):
        self.config = config
        self.connector_timeout = connector_timeout

    async def sync_to_linear(
        self,
        items: list[WorkstreamItem],
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Sync items to Linear."""
        if not self.config.linear_enabled:
            return {"skipped": True, "reason": "linear disabled"}

        try:
            result = await asyncio.wait_for(
                linear_sync_to(
                    items=items,
                    config=self._linear_config(),
                    dry_run=dry_run,
                ),
                timeout=self.connector_timeout,
            )
            return {"success": True, "result": result}
        except (LinearGraphQLError, LinearGraphQLAuthError) as e:
            logger.error(f"Linear sync error: {e}")
            return {"error": str(e)}
        except TimeoutError:
            return {"error": "timeout"}

    async def sync_from_linear(self) -> list[WorkstreamItem]:
        """Sync items from Linear."""
        if not self.config.linear_enabled:
            return []

        try:
            result = await asyncio.wait_for(
                linear_sync_from(config=self._linear_config()),
                timeout=self.connector_timeout,
            )
            return result
        except Exception as e:
            logger.error(f"Linear sync error: {e}")
            return []

    def _linear_config(self) -> LinearGraphQLConfig:
        return LinearGraphQLConfig(
            api_key=self.config.linear_api_key,
            team_id=self.config.linear_team_id,
        )


__all__ = ["LinearSync"]
