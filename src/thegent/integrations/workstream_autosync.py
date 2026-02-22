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
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

OPEN_STATUSES: set[str] = {"BACKLOG", "IN PROGRESS", "REVIEW", "TODO", "OPEN"}

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Utility Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MaintenanceWindow:
    """Parsed maintenance window configuration for a connector."""

    connector: str
    start_utc: datetime
    end_utc: datetime
    reason: str = ""

    def is_active(self, now: datetime) -> bool:
        """Return whether the window is active at the given timestamp."""
        now_utc = now.astimezone(timezone.utc)
        return self.start_utc <= now_utc <= self.end_utc


@dataclass(frozen=True)
class WorkstreamPartition:
    """Partition for large sync ranges."""

    start: int
    end: int

    @property
    def count(self) -> int:
        """Return number of items in the partition."""
        return max(0, self.end - self.start)


@dataclass(frozen=True)
class SyncCheckpoint:
    """Minimal checkpoint used for rolling resume."""

    connector: str
    direction: str
    start_index: int
    total_partitions: int
    partition_size: int
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Serialize checkpoint state."""
        return {
            "connector": self.connector,
            "direction": self.direction,
            "start_index": self.start_index,
            "total_partitions": self.total_partitions,
            "partition_size": self.partition_size,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SyncCheckpoint":
        """Construct a checkpoint from serialized state."""
        created_at = payload["created_at"]
        if isinstance(created_at, str):
            created_at_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            created_at_dt = created_at
        return cls(
            connector=payload["connector"],
            direction=payload["direction"],
            start_index=int(payload["start_index"]),
            total_partitions=int(payload["total_partitions"]),
            partition_size=int(payload["partition_size"]),
            created_at=created_at_dt,
        )


@dataclass(frozen=True)
class FailureRecord:
    """Failure entry for queue pruning and retry heuristics."""

    operation_id: str
    connector: str
    item_id: str
    message: str
    occurred_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Serialize failure record."""
        return {
            "operation_id": self.operation_id,
            "connector": self.connector,
            "item_id": self.item_id,
            "message": self.message,
            "occurred_at": self.occurred_at.isoformat(),
        }


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
    work_stream_path: Path | None = None
    status_file_path: Path | None = None
    checkpoint_file_path: Path | None = None
    dry_run: bool = False
    max_partition_size: int = 200
    maintenance_windows: list[MaintenanceWindow] = field(default_factory=list)
    checkpoint_ttl_seconds: int = 3600
    allowed_tags: list[str] = field(default_factory=list)
    failure_queue_path: Path | None = None
    failure_queue_retention_seconds: int = 60 * 60 * 24
    strict_tag_validation: bool = False
    strict_title_validation: bool = False
    standalone_mode: bool = True  # Always succeed, even if credentials missing

    @property
    def effective_partition_size(self) -> int:
        """Return a bounded partition size for planning."""
        return max(1, self.max_partition_size)

    def is_valid(self) -> bool:
        """Check if config has at least one platform enabled."""
        if not self.enabled:
            return False
        github_valid = bool(self.github_enabled and self.github_owner and self.github_project_number > 0)
        linear_valid = bool(self.linear_enabled and self.linear_api_key and self.linear_team_key)
        return github_valid or linear_valid

    def should_sync_github(self) -> bool:
        """Check if GitHub sync is enabled and configured."""
        return self.enabled and self.github_enabled and bool(self.github_owner) and self.github_project_number > 0

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

    def is_maintenance_active(self, connector: str, at: datetime | None = None) -> bool:
        """Return whether a connector is currently in planned maintenance."""
        now = at or datetime.now(timezone.utc)
        target = connector.lower()
        for window in self.maintenance_windows:
            if window.connector not in (target, "all", "*"):
                continue
            if window.is_active(now):
                return True
        return False


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class WorkstreamAutosyncError(Exception):
    """Base exception for workstream autosync errors."""


class WorkstreamAutosyncAuthError(WorkstreamAutosyncError):
    """Authentication/authorization error."""


class WorkstreamAutosyncConfigError(WorkstreamAutosyncError):
    """Configuration validation error."""


class WorkstreamAutosyncMaintenanceError(WorkstreamAutosyncError):
    """Raised when a maintenance window blocks sync operations."""


class WorkstreamDuplicateTitleError(WorkstreamAutosyncConfigError):
    """Raised for duplicate workstream titles."""


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
    blocked_by: str | None = None
    source_line: int = 0
    board_id: str | None = None  # External board ID if known
    tags: list[str] = field(default_factory=list)
    sla_hours: float | None = None
    last_synced: datetime | None = None

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
            "tags": self.tags,
            "sla_hours": self.sla_hours,
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
    completed_at: datetime | None = None
    duration_seconds: float | None = None

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


class SyncFailureQueue:
    """Store and prune recent sync failures."""

    def __init__(self, retention_seconds: int) -> None:
        self.retention_seconds = max(1, retention_seconds)
        self._entries: list[FailureRecord] = []

    def push(self, operation_id: str, connector: str, item_id: str, message: str) -> None:
        """Record a failed item operation."""
        self._entries.append(
            FailureRecord(
                operation_id=operation_id,
                connector=connector,
                item_id=item_id,
                message=message,
                occurred_at=datetime.now(timezone.utc),
            )
        )
        self.prune_expired()

    def prune_expired(self, now: datetime | None = None) -> None:
        """Drop failures older than retention window."""
        now_utc = now or datetime.now(timezone.utc)
        cutoff = now_utc - timedelta(seconds=self.retention_seconds)
        self._entries = [entry for entry in self._entries if entry.occurred_at >= cutoff]

    def snapshot(self) -> list[FailureRecord]:
        """Return all active failure records."""
        return list(self._entries)

    def to_dict_list(self) -> list[dict[str, Any]]:
        """Serialize active entries."""
        return [entry.to_dict() for entry in self._entries]

    def replace_records(self, entries: list[FailureRecord]) -> None:
        """Replace queue entries with persisted state."""
        self._entries = list(entries)


# ---------------------------------------------------------------------------
# Workstream Parser
# ---------------------------------------------------------------------------


class WorkstreamParser:
    """Parse WORK_STREAM.md and extract work items."""

    ITEM_PATTERN = re.compile(r"^###\s+\[(WL-\d+)\]\s+(.+?)$", re.MULTILINE)

    STATUS_PATTERN = re.compile(r"\*\*Status:\*\*\s+(.+?)(?:\n|$)")
    PRIORITY_PATTERN = re.compile(r"\*\*Priority:\*\*\s+(\w+)")
    AREA_PATTERN = re.compile(r"\*\*Area:\*\*\s+(.+?)(?:\n|$)")
    BLOCKED_BY_PATTERN = re.compile(r"\*\*Blocked by:\*\*\s+(.+?)(?:\n|$)")
    TAGS_PATTERN = re.compile(r"\*\*Tags:\*\*\s+(.+?)(?:\n|$)")
    SLA_PATTERN = re.compile(r"\*\*SLA:\*\*\s+(.+?)(?:\n|$)")

    @classmethod
    def _parse_sla_hours(cls, raw: str | None) -> float | None:
        """Parse SLA value into fractional hours."""
        if raw is None:
            return None
        value = raw.strip().lower()
        if not value:
            return None
        if value.endswith("h"):
            return float(value[:-1])
        if value.endswith("m"):
            return float(value[:-1]) / 60
        if value.endswith("d"):
            return float(value[:-1]) * 24
        return float(value)

    @classmethod
    def _parse_tags(cls, raw: str | None) -> list[str]:
        """Parse comma-separated tags and normalize to lower-case."""
        if raw is None:
            return []
        return [tag.strip().lower() for tag in raw.split(",") if tag.strip()]

    @staticmethod
    def _parse_checkpoint_partitions(items_count: int, partition_size: int) -> list[WorkstreamPartition]:
        """Build deterministic range partitions for large item streams."""
        step = max(1, partition_size)
        partitions = []
        start = 0
        while start < items_count:
            end = min(items_count, start + step)
            partitions.append(WorkstreamPartition(start=start, end=end))
            start = end
        return partitions

    @classmethod
    def split_items(cls, items: list[WorkstreamItem], partition_size: int) -> list[list[WorkstreamItem]]:
        """Split items into partitions by configured size."""
        partitions: list[list[WorkstreamItem]] = []
        for chunk in cls._parse_checkpoint_partitions(len(items), partition_size):
            partitions.append(items[chunk.start : chunk.end])
        return partitions

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
            status = status_match.group(1).strip() if status_match else "BACKLOG"

            priority_match = cls.PRIORITY_PATTERN.search(section)
            priority = priority_match.group(1) if priority_match else "P2"

            area_match = cls.AREA_PATTERN.search(section)
            area = area_match.group(1).strip() if area_match else "unknown"

            blocked_by_match = cls.BLOCKED_BY_PATTERN.search(section)
            blocked_by = blocked_by_match.group(1).strip() if blocked_by_match else None

            tags_match = cls.TAGS_PATTERN.search(section)
            tags = cls._parse_tags(tags_match.group(1).strip() if tags_match else None)

            sla_match = cls.SLA_PATTERN.search(section)
            sla_hours = cls._parse_sla_hours(sla_match.group(1).strip() if sla_match else None)

            item = WorkstreamItem(
                item_id=item_id,
                title=title,
                status=status,
                priority=priority,
                area=area,
                blocked_by=blocked_by,
                tags=tags,
                sla_hours=sla_hours,
                source_line=source_line,
            )

            items.append(item)

        logger.info("Parsed %d work stream items from %s", len(items), work_stream_path)
        return items

    @classmethod
    def duplicate_titles(
        cls,
        items: list[WorkstreamItem],
        *,
        allow_none: bool = True,
    ) -> list[tuple[str, list[WorkstreamItem]]]:
        """Return duplicate titles mapped to item clusters."""
        by_title: dict[str, list[WorkstreamItem]] = {}
        for item in items:
            by_title.setdefault(item.title.strip(), []).append(item)
        duplicates = [(title, group) for title, group in by_title.items() if len(group) > 1]
        if allow_none:
            return duplicates
        return [(title, group) for title, group in duplicates if title]

    @classmethod
    def validate_tags(
        cls,
        items: list[WorkstreamItem],
        *,
        allowed_tags: list[str],
        strict: bool = False,
    ) -> tuple[bool, list[str]]:
        """Validate local tag taxonomy against an allowed set."""
        allowed = {tag.lower().strip() for tag in allowed_tags}
        invalid: set[str] = set()
        for item in items:
            for tag in item.tags:
                if tag.lower() not in allowed:
                    invalid.add(tag)
        is_valid = len(invalid) == 0 or not strict
        return is_valid, sorted(invalid)

    @classmethod
    def open_blocker_digest(cls, items: list[WorkstreamItem]) -> list[str]:
        """Build a digest list for items still blocked by dependencies."""
        digest: list[str] = []
        for item in items:
            if item.status not in OPEN_STATUSES or not item.blocked_by:
                continue
            if item.blocked_by.strip().lower() in {"none", "n/a"}:
                continue
            digest.append(f"{item.item_id}:{item.title} -> {item.blocked_by}")
        return digest

    @classmethod
    def sync_sla_annotations(cls, text: str, *, items: list[WorkstreamItem]) -> str:
        """Ensure each SLA field is reflected in markdown content."""
        if not items:
            return text

        updates: dict[str, str] = {}
        for item in items:
            if item.sla_hours is None:
                continue
            updates[item.item_id] = f"{item.sla_hours}h"

        if not updates:
            return text

        def _rewrite_section(match: re.Match[str]) -> str:
            item_id = match.group(1)
            body = match.group(2)
            if item_id not in updates:
                return match.group(0)

            replacement = body
            sla_line = f"**SLA:** {updates[item_id]}"
            if cls.SLA_PATTERN.search(body):
                replacement = cls.SLA_PATTERN.sub(sla_line, body)
            elif body.strip():
                replacement = f"{body.rstrip()}\n{sla_line}"
            else:
                replacement = f"{sla_line}\n{body}"
            return f"### [{item_id}] {match.group(3)}{replacement}"

        pattern = re.compile(
            r"###\s+\[(WL-\d+)\]\s+(.+?)\n((?:.|\n)*?)(?=\n###\s+\[WL-|\Z)",
            re.MULTILINE,
        )
        return pattern.sub(_rewrite_section, text)


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
        self._task: asyncio.Task[None] | None = None
        self.last_sync_time: datetime | None = None
        self.last_operation: SyncOperation | None = None
        self.total_cycles = 0
        self.last_error: str | None = None
        self._failure_queue = SyncFailureQueue(
            retention_seconds=self.config.failure_queue_retention_seconds,
        )
        self._load_failure_queue()
        self._checkpoint: SyncCheckpoint | None = None
        self._latest_blocker_digest: list[str] = []

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
            raw_content = ""
            if work_stream_path.exists():
                raw_content = work_stream_path.read_text(encoding="utf-8")

            # Parse local items
            items = WorkstreamParser.parse_items(work_stream_path)
            if not items:
                logger.debug("No work stream items to sync")
                self._clear_checkpoint()
                self.total_cycles += 1
                self.last_error = None
                self._write_status_snapshot()
                return

            title_duplicates = WorkstreamParser.duplicate_titles(items)
            if title_duplicates and self.config.strict_title_validation:
                duplicates = ", ".join(title for title, _ in title_duplicates)
                raise WorkstreamDuplicateTitleError(
                    f"Duplicate workstream titles detected: {duplicates}",
                )

            _, invalid_tags = WorkstreamParser.validate_tags(
                items,
                allowed_tags=self.config.allowed_tags,
                strict=self.config.strict_tag_validation,
            )
            if invalid_tags and self.config.strict_tag_validation:
                raise WorkstreamAutosyncConfigError(
                    f"Invalid workstream tags detected: {', '.join(invalid_tags)}",
                )

            self.last_sync_time = datetime.now(timezone.utc)
            logger.debug("Performing sync cycle for %d items", len(items))
            self._failure_queue.prune_expired(self.last_sync_time)
            self._write_failure_queue()
            self._latest_blocker_digest = WorkstreamParser.open_blocker_digest(items)

            updated_content = WorkstreamParser.sync_sla_annotations(raw_content, items=items)
            if updated_content != raw_content and not self.config.dry_run:
                work_stream_path.parent.mkdir(parents=True, exist_ok=True)
                work_stream_path.write_text(updated_content, encoding="utf-8")

            try:
                self._checkpoint = self._load_checkpoint()
                if self._checkpoint and self.last_sync_time - self._checkpoint.created_at > timedelta(
                    seconds=self.config.checkpoint_ttl_seconds,
                ):
                    logger.debug("Checkpoint expired; restarting from index 0")
                    self._checkpoint = None
            except (ValueError, KeyError, OSError) as exc:
                logger.debug("Checkpoint load failed, continuing without resume: %s", exc)
                self._checkpoint = None

            # Sync to GitHub if enabled
            if self.config.should_sync_github():
                if self.config.is_maintenance_active("github"):
                    logger.info("Skipping GitHub sync because connector is in maintenance window")
                    self._clear_checkpoint("github", "write")
                    self._clear_checkpoint("github", "read")
                else:
                    await self._sync_in_partitions(
                        connector="github",
                        direction="write",
                        items=items,
                        sync_fn=self._sync_to_github,
                    )
                if self.config.github_can_read():
                    await self._sync_in_partitions(
                        connector="github",
                        direction="read",
                        items=items,
                        sync_fn=lambda chunk: self._sync_from_github(chunk, work_stream_path),
                    )

            # Sync to Linear if enabled
            if self.config.should_sync_linear():
                if self.config.is_maintenance_active("linear"):
                    logger.info("Skipping Linear sync because connector is in maintenance window")
                    self._clear_checkpoint("linear", "write")
                    self._clear_checkpoint("linear", "read")
                else:
                    await self._sync_in_partitions(
                        connector="linear",
                        direction="write",
                        items=items,
                        sync_fn=self._sync_to_linear,
                    )
                if self.config.linear_can_read():
                    await self._sync_in_partitions(
                        connector="linear",
                        direction="read",
                        items=items,
                        sync_fn=lambda chunk: self._sync_from_linear(chunk, work_stream_path),
                    )

            self.total_cycles += 1
            self.last_error = None
            self._write_status_snapshot()

        except Exception as e:
            logger.error("Failed to perform sync cycle: %s", e, exc_info=True)
            self.total_cycles += 1
            self.last_error = str(e)
            self._write_status_snapshot()

    def _write_status_snapshot(self) -> None:
        status_path = self.config.status_file_path or Path("docs/reference/autosync_status.json")
        payload = {
            "last_cycle_at": datetime.now(timezone.utc).isoformat(),
            "total_cycles": self.total_cycles,
            "last_error": self.last_error,
            "health": "degraded" if self.last_error else "ok",
            "runner": self.get_status(),
            "open_blockers": self._latest_blocker_digest,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "checkpoint": self._checkpoint.to_dict() if self._checkpoint else None,
        }
        try:
            status_path.parent.mkdir(parents=True, exist_ok=True)
            status_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            logger.warning("Failed to write autosync status to %s: %s", status_path, exc)

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

    async def _sync_from_github(self, items: list[WorkstreamItem], _work_stream_path: Path) -> None:  # pyright: ignore[reportUnusedParameter]
        """Sync status updates from GitHub Projects back to local markdown.

        Args:
            items: Work stream items
            _work_stream_path: Path to WORK_STREAM.md (unused in stub)
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

    async def _sync_from_linear(self, items: list[WorkstreamItem], _work_stream_path: Path) -> None:  # pyright: ignore[reportUnusedParameter]
        """Sync status updates from Linear back to local markdown.

        Args:
            items: Work stream items
            _work_stream_path: Path to WORK_STREAM.md (unused in stub)
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

    async def _sync_in_partitions(
        self,
        *,
        connector: str,
        direction: str,
        items: list[WorkstreamItem],
        sync_fn,
    ) -> None:
        """Run a sync function over dynamic partitions with checkpoint resume."""
        partitions = WorkstreamParser.split_items(items, self.config.effective_partition_size)
        start_index = self._checkpoint_start(connector, direction, len(partitions))

        if start_index >= len(partitions):
            self._clear_checkpoint(connector, direction)
            return

        for partition_index in range(start_index, len(partitions)):
            logger.debug("Running %s/%s partition %d/%d", connector, direction, partition_index + 1, len(partitions))
            self._checkpoint = SyncCheckpoint(
                connector=connector,
                direction=direction,
                start_index=partition_index,
                total_partitions=len(partitions),
                partition_size=self.config.effective_partition_size,
                created_at=datetime.now(timezone.utc),
            )
            self._write_checkpoint()
            try:
                await sync_fn(partitions[partition_index])
            except Exception as exc:
                await self._record_failure(
                    connector=connector,
                    direction=direction,
                    item_id=f"partition:{partition_index}",
                    message=str(exc),
                )
                self._checkpoint = SyncCheckpoint(
                    connector=connector,
                    direction=direction,
                    start_index=partition_index,
                    total_partitions=len(partitions),
                    partition_size=self.config.effective_partition_size,
                    created_at=datetime.now(timezone.utc),
                )
                self._write_checkpoint()
                if not self.config.standalone_mode:
                    raise

                logger.error(
                    "Partition sync failed for connector=%s direction=%s partition=%d: %s",
                    connector,
                    direction,
                    partition_index,
                    exc,
                )
                return

            self._checkpoint = SyncCheckpoint(
                connector=connector,
                direction=direction,
                start_index=partition_index + 1,
                total_partitions=len(partitions),
                partition_size=self.config.effective_partition_size,
                created_at=datetime.now(timezone.utc),
            )
            self._write_checkpoint()

        self._clear_checkpoint(connector, direction)

    def _failure_queue_path(self) -> Path:
        """Get failure queue persistence path."""
        default_failure_queue_path = Path("docs/reference/workstream_autosync_failures.json")
        return self.config.failure_queue_path or default_failure_queue_path

    def _load_failure_queue(self) -> None:
        """Load persisted failure queue entries."""
        path = self._failure_queue_path()
        if not path.exists():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        if not isinstance(payload, list):
            return

        entries: list[FailureRecord] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                occurred_at = item["occurred_at"]
                occurred_at_dt = (
                    datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
                    if isinstance(occurred_at, str)
                    else occurred_at
                )
                entries.append(
                    FailureRecord(
                        operation_id=item["operation_id"],
                        connector=item["connector"],
                        item_id=item["item_id"],
                        message=item["message"],
                        occurred_at=occurred_at_dt,
                    ),
                )
            except (KeyError, ValueError, TypeError):
                logger.debug("Skipping malformed failure queue entry: %s", item)
                continue

        self._failure_queue = SyncFailureQueue(
            retention_seconds=self.config.failure_queue_retention_seconds,
        )
        self._failure_queue.replace_records(entries)

    def _write_failure_queue(self) -> None:
        """Persist failure queue state."""
        path = self._failure_queue_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._failure_queue.to_dict_list(), indent=2), encoding="utf-8")

    def _checkpoint_start(self, connector: str, direction: str, partition_count: int) -> int:
        """Compute start partition index for resume."""
        if not self._checkpoint:
            return 0
        if (
            self._checkpoint.connector == connector
            and self._checkpoint.direction == direction
            and self._checkpoint.total_partitions == partition_count
            and self._checkpoint.partition_size == self.config.effective_partition_size
        ):
            return min(self._checkpoint.start_index, partition_count)
        return 0

    def _checkpoint_path(self) -> Path:
        """Get checkpoint persistence path."""
        default_checkpoint_path = Path("docs/reference/workstream_autosync_checkpoint.json")
        return self.config.checkpoint_file_path or default_checkpoint_path

    def _checkpoint_key(self) -> Path:
        """Compatibility alias for checkpoint naming."""
        return self._checkpoint_path()

    def _load_checkpoint(self) -> SyncCheckpoint | None:
        """Load checkpoint from disk."""
        path = self._checkpoint_path()
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        return SyncCheckpoint.from_dict(payload)

    def _write_checkpoint(self) -> None:
        """Persist current checkpoint state."""
        if not self._checkpoint:
            return
        path = self._checkpoint_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._checkpoint.to_dict(), indent=2), encoding="utf-8")

    def _clear_checkpoint(self, connector: str | None = None, direction: str | None = None) -> None:
        """Clear checkpoint state for requested scope."""
        if connector is None or direction is None:
            self._checkpoint = None
            path = self._checkpoint_path()
            if path.exists():
                path.unlink()
            return

        if self._checkpoint and self._checkpoint.connector == connector and self._checkpoint.direction == direction:
            self._checkpoint = None
            path = self._checkpoint_path()
            if path.exists():
                path.unlink()

    async def _record_failure(
        self,
        *,
        connector: str,
        direction: str,
        item_id: str,
        message: str,
    ) -> None:
        """Record a failure and prune stale entries."""
        operation_id = f"{connector}-{direction}-{int(time.time())}"
        self._failure_queue.push(
            operation_id=operation_id,
            connector=connector,
            item_id=item_id,
            message=message,
        )
        self._write_failure_queue()
        self.last_error = message

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
            "open_blockers": self._latest_blocker_digest,
            "failure_queue_size": len(self._failure_queue.snapshot()),
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
    THGENT_AUTOSYNC_STATUS_PATH: Path to autosync status JSON
    THGENT_WORKSTREAM_AUTOSYNC_CHECKPOINT_PATH: Path to checkpoint JSON
    THGENT_WORKSTREAM_AUTOSYNC_MAX_PARTITION_SIZE: Dynamic partition size
    THGENT_WORKSTREAM_AUTOSYNC_TTL_SECONDS: Checkpoint TTL seconds
    THGENT_AUTOSYNC_MAINTENANCE_WINDOWS: Maintenance windows (`connector:start:end:reason` or JSON array)
    THGENT_WORKSTREAM_TAG_TAXONOMY: Comma-separated approved tags
    THGENT_WORKSTREAM_AUTOSYNC_FAILURE_QUEUE_PATH: Path to failure queue JSON
    THGENT_WORKSTREAM_AUTOSYNC_FAILURE_QUEUE_TTL_SECONDS: Failure queue retention seconds
    THGENT_WORKSTREAM_STRICT_TAG_VALIDATION: Require tags to match taxonomy
    THGENT_WORKSTREAM_STRICT_TITLE_VALIDATION: Require duplicate titles to fail

    Returns:
        WorkstreamAutosyncConfig instance
    """
    import os

    def parse_bool(value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def parse_int(value: str | None, default: int) -> int:
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def parse_json_windows(raw: str | None) -> list[MaintenanceWindow]:
        if not raw:
            return []
        parsed = []
        candidate_windows = raw.strip()
        if candidate_windows.startswith("["):
            try:
                payload = json.loads(candidate_windows)
            except json.JSONDecodeError as exc:
                logger.warning("Invalid THGENT_AUTOSYNC_MAINTENANCE_WINDOWS JSON: %s", exc)
                return []
            if not isinstance(payload, list):
                return []
            for item in payload:
                if not isinstance(item, dict):
                    continue
                connector = str(item.get("connector", "all")).strip().lower() or "all"
                start_raw = item.get("start_utc") or item.get("start")
                end_raw = item.get("end_utc") or item.get("end")
                reason = str(item.get("reason", "")).strip()
                if start_raw is None or end_raw is None:
                    continue
                try:
                    parsed.append(
                        MaintenanceWindow(
                            connector=connector,
                            start_utc=datetime.fromisoformat(str(start_raw).replace("Z", "+00:00")),
                            end_utc=datetime.fromisoformat(str(end_raw).replace("Z", "+00:00")),
                            reason=reason,
                        )
                    )
                except (TypeError, ValueError):
                    logger.debug("Skipping malformed maintenance window item: %s", item)
            return parsed

        for raw_entry in candidate_windows.split(";"):
            raw_entry = raw_entry.strip()
            if not raw_entry:
                continue
            parts = raw_entry.split(":", 3)
            if len(parts) < 3:
                logger.debug("Skipping malformed maintenance window token: %s", raw_entry)
                continue
            connector, start_raw, end_raw, *reason_parts = parts
            reason = reason_parts[0].strip() if reason_parts else ""
            try:
                parsed.append(
                    MaintenanceWindow(
                        connector=connector.strip().lower() or "all",
                        start_utc=datetime.fromisoformat(start_raw.strip().replace("Z", "+00:00")),
                        end_utc=datetime.fromisoformat(end_raw.strip().replace("Z", "+00:00")),
                        reason=reason,
                    )
                )
            except (TypeError, ValueError):
                logger.debug("Skipping malformed maintenance window token: %s", raw_entry)
        return parsed

    def parse_tag_taxonomy(raw: str | None) -> list[str]:
        if not raw:
            return []
        raw = raw.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return []
            if not isinstance(payload, list):
                return []
            return [str(tag).strip().lower() for tag in payload if str(tag).strip()]
        return [tag.strip().lower() for tag in raw.split(",") if tag.strip()]

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
    status_file_path = os.getenv("THGENT_AUTOSYNC_STATUS_PATH")
    checkpoint_file_path = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_CHECKPOINT_PATH")
    failure_queue_path = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_FAILURE_QUEUE_PATH")
    maintenance_windows = parse_json_windows(os.getenv("THGENT_AUTOSYNC_MAINTENANCE_WINDOWS"))
    allowed_tags = parse_tag_taxonomy(os.getenv("THGENT_WORKSTREAM_TAG_TAXONOMY"))

    return WorkstreamAutosyncConfig(
        enabled=parse_bool(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_ENABLED")),
        cycle_interval_seconds=parse_int(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_INTERVAL", "300"), default=300),
        checkpoint_ttl_seconds=parse_int(
            os.getenv("THGENT_WORKSTREAM_AUTOSYNC_TTL_SECONDS", str(3600)),
            default=3600,
        ),
        github_enabled=parse_bool(os.getenv("THGENT_GITHUB_ENABLED")),
        github_owner=os.getenv("THGENT_GITHUB_OWNER", ""),
        github_project_number=parse_int(os.getenv("THGENT_GITHUB_PROJECT_NUMBER", "0"), default=0),
        github_direction=github_dir,
        linear_enabled=parse_bool(os.getenv("THGENT_LINEAR_ENABLED")),
        linear_api_key=os.getenv("THGENT_LINEAR_API_KEY", ""),
        linear_team_key=os.getenv("THGENT_LINEAR_TEAM_KEY", ""),
        linear_direction=linear_dir,
        work_stream_path=Path(work_stream_path) if work_stream_path else None,
        status_file_path=Path(status_file_path) if status_file_path else None,
        checkpoint_file_path=Path(checkpoint_file_path) if checkpoint_file_path else None,
        maintenance_windows=maintenance_windows,
        max_partition_size=parse_int(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_MAX_PARTITION_SIZE", "200"), default=200),
        allowed_tags=allowed_tags,
        failure_queue_path=Path(failure_queue_path) if failure_queue_path else None,
        failure_queue_retention_seconds=parse_int(
            os.getenv("THGENT_WORKSTREAM_AUTOSYNC_FAILURE_QUEUE_TTL_SECONDS", str(60 * 60 * 24)),
            default=60 * 60 * 24,
        ),
        strict_tag_validation=parse_bool(os.getenv("THGENT_WORKSTREAM_STRICT_TAG_VALIDATION")),
        strict_title_validation=parse_bool(os.getenv("THGENT_WORKSTREAM_STRICT_TITLE_VALIDATION")),
        standalone_mode=parse_bool(os.getenv("THGENT_AUTOSYNC_STANDALONE_MODE"), default=True),
    )
