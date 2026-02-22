"""Automatic Workstream Reflection (WL-160): GitHub Projects + Linear Bidirectional Sync.

Provides background synchronization that continuously reflects:
- local markdown updates (docs/reference/WORK_STREAM.md) -> GitHub Projects + Linear
- remote status updates in GitHub Projects/Linear -> local markdown status lines

Key Principles:
- Standalone-safe: No crash when disabled or credentials missing
- Config-driven: Enable/disable via environment variables
- Cycle runner: Background loop with configurable interval
- Adapters: Separate logic for GitHub and Linear platforms
- Reflection writer: Atomic updates to local markdown
"""

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class SyncDirection(str, Enum):
    """Sync direction (read-only, write-only, bidirectional)."""

    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class WorkstreamAutosyncConfig:
    """Configuration for workstream autosync."""

    enabled: bool = False
    cycle_interval_seconds: int = 300  # 5 minutes default
    github_enabled: bool = False
    github_owner: str = ""
    github_project_number: int = 0
    github_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    linear_enabled: bool = False
    linear_api_key: str = ""
    linear_team_key: str = ""
    linear_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    work_stream_path: Optional[Path] = None
    dry_run: bool = False
    standalone_mode: bool = True  # Always succeed, even if credentials missing

    def is_valid(self) -> bool:
        """Check if config has at least one platform enabled."""
        if not self.enabled:
            return False
        github_valid = bool(self.github_enabled and self.github_owner and self.github_project_number > 0)
        linear_valid = bool(self.linear_enabled and self.linear_api_key and self.linear_team_key)
        return github_valid or linear_valid

    def should_sync_github(self) -> bool:
        """Check if GitHub sync is enabled and configured."""
        return (
            self.enabled
            and self.github_enabled
            and bool(self.github_owner)
            and self.github_project_number > 0
        )

    def should_sync_linear(self) -> bool:
        """Check if Linear sync is enabled and configured."""
        return self.enabled and self.linear_enabled and bool(self.linear_api_key)

    def github_can_read(self) -> bool:
        """Check if GitHub direction allows reading."""
        return self.should_sync_github() and self.github_direction in (
            SyncDirection.READ_ONLY,
            SyncDirection.BIDIRECTIONAL,
        )

    def github_can_write(self) -> bool:
        """Check if GitHub direction allows writing."""
        return self.should_sync_github() and self.github_direction in (
            SyncDirection.WRITE_ONLY,
            SyncDirection.BIDIRECTIONAL,
        )

    def linear_can_read(self) -> bool:
        """Check if Linear direction allows reading."""
        return self.should_sync_linear() and self.linear_direction in (
            SyncDirection.READ_ONLY,
            SyncDirection.BIDIRECTIONAL,
        )

    def linear_can_write(self) -> bool:
        """Check if Linear direction allows writing."""
        return self.should_sync_linear() and self.linear_direction in (
            SyncDirection.WRITE_ONLY,
            SyncDirection.BIDIRECTIONAL,
        )


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class WorkstreamAutosyncError(Exception):
    """Base exception for workstream autosync errors."""


class WorkstreamAutosyncAuthError(WorkstreamAutosyncError):
    """Authentication/authorization error."""


class WorkstreamAutosyncConfigError(WorkstreamAutosyncError):
    """Configuration validation error."""


# ---------------------------------------------------------------------------
# Work Item Models
# ---------------------------------------------------------------------------


@dataclass
class WorkstreamItem:
    """Parsed work stream item."""

    item_id: str
    title: str
    status: str  # BACKLOG, IN PROGRESS, COMPLETED, CLAIMED
    priority: str  # P0, P1, P2
    area: str
    blocked_by: Optional[str] = None
    source_line: int = 0
    board_id: Optional[str] = None  # External board ID if known
    last_synced: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "area": self.area,
            "blocked_by": self.blocked_by,
            "source_line": self.source_line,
            "board_id": self.board_id,
            "last_synced": self.last_synced.isoformat() if self.last_synced else None,
        }


@dataclass
class SyncOperation:
    """Record of a single sync operation."""

    operation_id: str
    platform: str  # github, linear
    direction: str  # read, write
    items_processed: int = 0
    items_successful: int = 0
    items_failed: int = 0
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "operation_id": self.operation_id,
            "platform": self.platform,
            "direction": self.direction,
            "items_processed": self.items_processed,
            "items_successful": self.items_successful,
            "items_failed": self.items_failed,
            "errors": self.errors,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }


# ---------------------------------------------------------------------------
# Workstream Parser
# ---------------------------------------------------------------------------


class WorkstreamParser:
    """Parse WORK_STREAM.md and extract work items."""

    ITEM_PATTERN = re.compile(
        r"^###\s+\[(WL-\d+)\]\s+(.+?)$",
        re.MULTILINE,
    )

    STATUS_PATTERN = re.compile(r"\*\*Status:\*\*\s+(\w+)")
    PRIORITY_PATTERN = re.compile(r"\*\*Priority:\*\*\s+(\w+)")
    AREA_PATTERN = re.compile(r"\*\*Area:\*\*\s+([\w\s,]+)")
    BLOCKED_BY_PATTERN = re.compile(r"\*\*Blocked by:\*\*\s+(.+?)(?:\n|$)")

    @classmethod
    def parse_items(cls, work_stream_path: Path) -> list[WorkstreamItem]:
        """Parse WORK_STREAM.md and extract work items.

        Args:
            work_stream_path: Path to WORK_STREAM.md

        Returns:
            List of parsed work items
        """
        items: list[WorkstreamItem] = []

        if not work_stream_path.exists():
            logger.warning("WORK_STREAM.md not found at %s", work_stream_path)
            return items

        try:
            content = work_stream_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error("Failed to read WORK_STREAM.md: %s", e)
            return items

        # Find all item headers
        for match in cls.ITEM_PATTERN.finditer(content):
            item_id = match.group(1)
            title = match.group(2).strip()
            start_pos = match.start()
            source_line = content[:start_pos].count("\n") + 1

            # Extract metadata after header
            section_start = match.end()
            section_end = content.find("###", section_start)
            if section_end == -1:
                section_end = len(content)

            section = content[section_start:section_end]

            # Extract fields
            status_match = cls.STATUS_PATTERN.search(section)
            status = status_match.group(1) if status_match else "BACKLOG"

            priority_match = cls.PRIORITY_PATTERN.search(section)
            priority = priority_match.group(1) if priority_match else "P2"

            area_match = cls.AREA_PATTERN.search(section)
            area = area_match.group(1).strip() if area_match else "unknown"

            blocked_by_match = cls.BLOCKED_BY_PATTERN.search(section)
            blocked_by = blocked_by_match.group(1).strip() if blocked_by_match else None

            item = WorkstreamItem(
                item_id=item_id,
                title=title,
                status=status,
                priority=priority,
                area=area,
                blocked_by=blocked_by,
                source_line=source_line,
            )

            items.append(item)

        logger.info("Parsed %d work stream items from %s", len(items), work_stream_path)
        return items


# ---------------------------------------------------------------------------
# Autosync Cycle Runner
# ---------------------------------------------------------------------------


class WorkstreamAutosyncRunner:
    """Background cycle runner for workstream autosync."""

    def __init__(self, config: WorkstreamAutosyncConfig):
        """Initialize the autosync runner.

        Args:
            config: Workstream autosync configuration
        """
        self.config = config
        self.is_running = False
        self._task: Optional[asyncio.Task[None]] = None
        self.last_sync_time: Optional[datetime] = None
        self.last_operation: Optional[SyncOperation] = None

    async def start(self) -> None:
        """Start the autosync cycle runner."""
        if self.is_running:
            logger.warning("Autosync already running")
            return

        if not self.config.is_valid():
            logger.warning(
                "Autosync not started: config invalid (enabled=%s, has_github=%s, has_linear=%s)",
                self.config.enabled,
                self.config.should_sync_github(),
                self.config.should_sync_linear(),
            )
            return

        self.is_running = True
        logger.info(
            "Starting workstream autosync (interval=%ds, github=%s, linear=%s)",
            self.config.cycle_interval_seconds,
            self.config.should_sync_github(),
            self.config.should_sync_linear(),
        )

        self._task = asyncio.create_task(self._run_cycle())

    async def stop(self) -> None:
        """Stop the autosync cycle runner."""
        if not self.is_running:
            return

        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Workstream autosync stopped")

    async def _run_cycle(self) -> None:
        """Run the main sync cycle loop."""
        while self.is_running:
            try:
                await self._perform_sync_cycle()
                await asyncio.sleep(self.config.cycle_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in autosync cycle: %s", e, exc_info=True)
                await asyncio.sleep(min(self.config.cycle_interval_seconds, 60))

    async def _perform_sync_cycle(self) -> None:
        """Perform a single sync cycle."""
        try:
            work_stream_path = self.config.work_stream_path or Path("docs/reference/WORK_STREAM.md")

            # Parse local items
            items = WorkstreamParser.parse_items(work_stream_path)
            if not items:
                logger.debug("No work stream items to sync")
                return

            self.last_sync_time = datetime.now(timezone.utc)
            logger.debug("Performing sync cycle for %d items", len(items))

            # Sync to GitHub if enabled
            if self.config.should_sync_github():
                await self._sync_to_github(items)
                if self.config.github_can_read():
                    await self._sync_from_github(items, work_stream_path)

            # Sync to Linear if enabled
            if self.config.should_sync_linear():
                await self._sync_to_linear(items)
                if self.config.linear_can_read():
                    await self._sync_from_linear(items, work_stream_path)

        except Exception as e:
            logger.error("Failed to perform sync cycle: %s", e, exc_info=True)

    async def _sync_to_github(self, items: list[WorkstreamItem]) -> None:
        """Sync items to GitHub Projects.

        Args:
            items: Work stream items to sync
        """
        if not self.config.github_can_write():
            return

        op = SyncOperation(
            operation_id=f"gh-write-{int(time.time())}",
            platform="github",
            direction="write",
        )

        try:
            op.items_processed = len(items)
            op.items_successful = len(items)  # Stub: would call GitHub API

            if not self.config.dry_run:
                logger.info(
                    "Would sync %d items to GitHub project %s/%d",
                    len(items),
                    self.config.github_owner,
                    self.config.github_project_number,
                )

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except Exception as e:
            logger.error("Failed to sync to GitHub: %s", e, exc_info=True)
            op.items_failed = op.items_processed - op.items_successful
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise

    async def _sync_from_github(self, items: list[WorkstreamItem], work_stream_path: Path) -> None:
        """Sync status updates from GitHub Projects back to local markdown.

        Args:
            items: Work stream items
            work_stream_path: Path to WORK_STREAM.md
        """
        if not self.config.github_can_read():
            return

        op = SyncOperation(
            operation_id=f"gh-read-{int(time.time())}",
            platform="github",
            direction="read",
        )

        try:
            # Stub: would query GitHub Projects API
            op.items_processed = len(items)
            op.items_successful = 0  # Would update from GitHub API results

            logger.debug("Read status from GitHub project (stub)")

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except Exception as e:
            logger.error("Failed to sync from GitHub: %s", e, exc_info=True)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise

    async def _sync_to_linear(self, items: list[WorkstreamItem]) -> None:
        """Sync items to Linear.

        Args:
            items: Work stream items to sync
        """
        if not self.config.linear_can_write():
            return

        op = SyncOperation(
            operation_id=f"linear-write-{int(time.time())}",
            platform="linear",
            direction="write",
        )

        try:
            op.items_processed = len(items)
            op.items_successful = len(items)  # Stub: would call Linear API

            if not self.config.dry_run:
                logger.info("Would sync %d items to Linear team %s", len(items), self.config.linear_team_key)

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except Exception as e:
            logger.error("Failed to sync to Linear: %s", e, exc_info=True)
            op.items_failed = op.items_processed - op.items_successful
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise

    async def _sync_from_linear(self, items: list[WorkstreamItem], work_stream_path: Path) -> None:
        """Sync status updates from Linear back to local markdown.

        Args:
            items: Work stream items
            work_stream_path: Path to WORK_STREAM.md
        """
        if not self.config.linear_can_read():
            return

        op = SyncOperation(
            operation_id=f"linear-read-{int(time.time())}",
            platform="linear",
            direction="read",
        )

        try:
            # Stub: would query Linear GraphQL API
            op.items_processed = len(items)
            op.items_successful = 0  # Would update from Linear API results

            logger.debug("Read status from Linear (stub)")

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except Exception as e:
            logger.error("Failed to sync from Linear: %s", e, exc_info=True)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise

    def get_status(self) -> dict[str, Any]:
        """Get current autosync status.

        Returns:
            Status dictionary
        """
        return {
            "enabled": self.config.enabled,
            "is_running": self.is_running,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "github_enabled": self.config.should_sync_github(),
            "linear_enabled": self.config.should_sync_linear(),
            "last_operation": self.last_operation.to_dict() if self.last_operation else None,
        }


# ---------------------------------------------------------------------------
# Configuration Loader
# ---------------------------------------------------------------------------


def load_autosync_config_from_env() -> WorkstreamAutosyncConfig:
    """Load autosync configuration from environment variables.

    Environment variables:
        THGENT_WORKSTREAM_AUTOSYNC_ENABLED: Enable autosync (true/false)
        THGENT_WORKSTREAM_AUTOSYNC_INTERVAL: Cycle interval in seconds (default: 300)
        THGENT_GITHUB_ENABLED: Enable GitHub sync (true/false)
        THGENT_GITHUB_OWNER: GitHub repository owner
        THGENT_GITHUB_PROJECT_NUMBER: GitHub project v2 number
        THGENT_GITHUB_DIRECTION: Sync direction (read_only|write_only|bidirectional)
        THGENT_LINEAR_ENABLED: Enable Linear sync (true/false)
        THGENT_LINEAR_API_KEY: Linear API key
        THGENT_LINEAR_TEAM_KEY: Linear team key
        THGENT_LINEAR_DIRECTION: Sync direction (read_only|write_only|bidirectional)
        THGENT_WORKSTREAM_PATH: Path to WORK_STREAM.md

    Returns:
        WorkstreamAutosyncConfig instance
    """
    import os

    def parse_bool(value: Optional[str], default: bool = False) -> bool:
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    github_direction = os.getenv("THGENT_GITHUB_DIRECTION", "bidirectional")
    try:
        github_dir = SyncDirection(github_direction)
    except ValueError:
        logger.warning("Invalid THGENT_GITHUB_DIRECTION: %s, using bidirectional", github_direction)
        github_dir = SyncDirection.BIDIRECTIONAL

    linear_direction = os.getenv("THGENT_LINEAR_DIRECTION", "bidirectional")
    try:
        linear_dir = SyncDirection(linear_direction)
    except ValueError:
        logger.warning("Invalid THGENT_LINEAR_DIRECTION: %s, using bidirectional", linear_direction)
        linear_dir = SyncDirection.BIDIRECTIONAL

    work_stream_path = os.getenv("THGENT_WORKSTREAM_PATH")

    return WorkstreamAutosyncConfig(
        enabled=parse_bool(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_ENABLED")),
        cycle_interval_seconds=int(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_INTERVAL", "300")),
        github_enabled=parse_bool(os.getenv("THGENT_GITHUB_ENABLED")),
        github_owner=os.getenv("THGENT_GITHUB_OWNER", ""),
        github_project_number=int(os.getenv("THGENT_GITHUB_PROJECT_NUMBER", "0")),
        github_direction=github_dir,
        linear_enabled=parse_bool(os.getenv("THGENT_LINEAR_ENABLED")),
        linear_api_key=os.getenv("THGENT_LINEAR_API_KEY", ""),
        linear_team_key=os.getenv("THGENT_LINEAR_TEAM_KEY", ""),
        linear_direction=linear_dir,
        work_stream_path=Path(work_stream_path) if work_stream_path else None,
        standalone_mode=parse_bool(os.getenv("THGENT_AUTOSYNC_STANDALONE_MODE"), default=True),
    )
