"""GitHub sync operations for workstream autosync.

Extracts GitHub sync logic from workstream_autosync.py.
"""

import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Any

from thegent.integrations.gh_project_sync import (
    GHProjectConfig,
    GHProjectSyncError,
    close_or_comment_github_issue_refs,
    extract_github_issue_refs,
    sync_from_github as gh_sync_from_github,
    sync_to_github as gh_sync_to_github,
)
from thegent.integrations.workstream_autosync_shared import (
    SyncDirection,
    WorkstreamItem,
)

logger = logging.getLogger(__name__)


class GitHubSync:
    """Handles GitHub sync operations."""

    def __init__(self, config: Any, connector_timeout: float):
        self.config = config
        self.connector_timeout = connector_timeout

    async def sync_to_github(
        self,
        items: list[WorkstreamItem],
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Sync items to GitHub."""
        if not self.config.github_enabled:
            return {"skipped": True, "reason": "github disabled"}

        try:
            result = await asyncio.wait_for(
                gh_sync_to_github(
                    items=items,
                    config=self._gh_config(),
                    dry_run=dry_run,
                ),
                timeout=self.connector_timeout,
            )
            return {"success": True, "result": result}
        except GHProjectSyncError as e:
            logger.error(f"GitHub sync error: {e}")
            return {"error": str(e)}
        except asyncio.TimeoutError:
            return {"error": "timeout"}

    async def sync_from_github(
        self,
        work_stream_path: Path,
    ) -> list[WorkstreamItem]:
        """Sync items from GitHub."""
        if not self.config.github_enabled:
            return []

        try:
            result = await asyncio.wait_for(
                gh_sync_from_github(config=self._gh_config()),
                timeout=self.connector_timeout,
            )
            return result
        except Exception as e:
            logger.error(f"GitHub sync error: {e}")
            return []

    def _gh_config(self) -> GHProjectConfig:
        return GHProjectConfig(
            owner=self.config.github_owner,
            project=self.config.github_project,
            token=self.config.github_token,
        )

    @staticmethod
    def extract_issue_refs(text: str) -> list[str]:
        """Extract GitHub issue references from text."""
        return extract_github_issue_refs(text)

    @staticmethod
    def close_or_comment_issues(refs: list[str], comment: str) -> None:
        """Close or comment on GitHub issues."""
        close_or_comment_github_issue_refs(refs, comment)


__all__ = ["GitHubSync"]
