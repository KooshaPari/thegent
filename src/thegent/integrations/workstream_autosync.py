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
import base64
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar
from uuid import uuid4

from thegent.config_defaults import autosync_phase1_enabled
from thegent.infra.identity_proxy import SSHIdentityProxy
from thegent.integrations.capability_alerts import CapabilityMismatchDetector, ConnectorCapabilityDiscovery
from thegent.integrations.connector_mapping_cache import ConnectorMappingCache
from thegent.integrations.error_budget import ErrorBudgetConfig, ErrorBudgetTracker
from thegent.integrations.gh_project_sync import (
    GHProjectConfig,
    GHProjectSyncError,
    close_or_comment_github_issue_refs,
    extract_github_issue_refs,
    sync_from_github as gh_sync_from_github,
    sync_to_github as gh_sync_to_github,
)
from thegent.integrations.idempotency_cache import IdempotencyCache
from thegent.integrations.linear_graphql import (
    LinearGraphQLAuthError,
    LinearGraphQLConfig,
    LinearGraphQLError,
    sync_from_linear as linear_sync_from,
    sync_to_linear as linear_sync_to,
)
from thegent.integrations.rate_limit_backoff import RateLimitBackoffManager, RateLimitConfig
from thegent.integrations.policy_checksum import verify_payload_checksum
from thegent.integrations.sync_provenance import enrich_sync_metadata
from thegent.integrations.writer_lock import SingleWriterLock
from thegent.observability.prometheus import get_metrics_collector
from thegent.execution import EscalationQueue
from thegent.routing.circuit_breaker import (
    CircuitOpenError,
    ProviderCircuitBreakerConfig,
    ProviderCircuitBreakerRegistry,
)

OPEN_STATUSES: set[str] = {"BACKLOG", "IN PROGRESS", "REVIEW", "TODO", "OPEN"}
WL_ID_PATTERN = re.compile(r"^WL-\d+$")

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
    project: str = "default"

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
    retry_class: str = "permanent"
    correlation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize failure record."""
        return {
            "operation_id": self.operation_id,
            "connector": self.connector,
            "item_id": self.item_id,
            "message": self.message,
            "occurred_at": self.occurred_at.isoformat(),
            "retry_class": self.retry_class,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True)
class ConnectorHealthProbeResult:
    """Connector health probe state for a cycle."""

    connector: str
    status: str
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "connector": self.connector,
            "status": self.status,
            "reason": self.reason,
        }


def compute_adaptive_sync_interval(
    *,
    base_interval_seconds: int,
    min_interval_seconds: int,
    max_interval_seconds: int,
    drift_rate: float,
    error_rate: float,
    load_factor: float,
) -> int:
    """Compute next-cycle interval from drift/error/load metrics.

    Higher drift or error rates shrink the interval.
    Higher load factor expands the interval to reduce pressure.
    """
    floor = max(1, min_interval_seconds)
    ceiling = max(floor, max_interval_seconds)
    base = max(floor, min(base_interval_seconds, ceiling))
    pressure = (0.6 * drift_rate) + (0.4 * error_rate) - (0.35 * load_factor)
    multiplier = 1.0 - pressure
    candidate = round(base * multiplier)
    return max(floor, min(ceiling, candidate))


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class SyncDirection(str, Enum):
    """Sync direction (read-only, write-only, bidirectional)."""

    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    BIDIRECTIONAL = "bidirectional"


class RemoteMissingItemPolicy(str, Enum):
    """Policy for local WL items missing from remote connector snapshots."""

    IGNORE = "ignore"
    ARCHIVE = "archive"
    DELETE = "delete"


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
    github_sandbox_mode: bool = False
    github_sandbox_project_number: int = 0
    work_stream_path: Path | None = None
    status_file_path: Path | None = None
    checkpoint_file_path: Path | None = None
    cycle_manifest_path: Path | None = None
    dry_run: bool = False
    shadow_mode: bool = False
    max_partition_size: int = 200
    maintenance_windows: list[MaintenanceWindow] = field(default_factory=list)
    checkpoint_ttl_seconds: int = 3600
    migration_phase: str = "phase1-detect"
    repo_previously_opted_in: bool = False
    conflict_ttl_seconds: int = 1800
    allowed_tags: list[str] = field(default_factory=list)
    failure_queue_path: Path | None = None
    failure_queue_retention_seconds: int = 60 * 60 * 24
    connector_mapping_cache_path: Path | None = None
    simulation_mode: bool = False
    snapshot_retention_count: int = 20
    trend_file_path: Path | None = None
    artifact_encryption_enabled: bool = False
    artifact_encryption_key: str = ""
    strict_tag_validation: bool = False
    strict_title_validation: bool = False
    adaptive_interval_enabled: bool = False
    adaptive_interval_min_seconds: int = 30
    adaptive_interval_max_seconds: int = 900
    connector_health_states: dict[str, str] = field(default_factory=dict)
    incident_bundle_path: Path | None = None
    metadata_ttl_seconds: int = 3600
    metadata_last_refreshed_at: datetime | None = None
    bootstrap_connector: str = "github"
    bootstrap_required_fields: list[str] = field(default_factory=list)
    bootstrap_mapping_cache_path: Path | None = None
    project_id: str = "default"
    require_actor_identity: bool = False
    actor_id: str = ""
    actor_signature: str = ""
    actor_signing_key: str = ""
    connector_capabilities: dict[str, list[str]] = field(default_factory=dict)
    required_connector_capabilities: dict[str, list[str]] = field(default_factory=dict)
    payload_checksum_enforced: bool = False
    expected_payload_checksum: str = ""
    emergency_stop_enabled: bool = True
    emergency_stop_file_path: Path | None = None
    emergency_stop_env_var: str = "THGENT_AUTOSYNC_EMERGENCY_STOP"
    wl_ignore_list: list[str] = field(default_factory=list)
    scope_areas: list[str] = field(default_factory=list)
    scope_statuses: list[str] = field(default_factory=list)
    scope_priorities: list[str] = field(default_factory=list)
    scope_wl_ranges: list[str] = field(default_factory=list)
    remote_missing_item_policy: RemoteMissingItemPolicy = RemoteMissingItemPolicy.IGNORE
    github_write_timeout_seconds: float = 30.0
    github_read_timeout_seconds: float = 30.0
    linear_write_timeout_seconds: float = 30.0
    linear_read_timeout_seconds: float = 30.0
    github_auto_close_issues: bool = False
    github_auto_close_comment: str | None = "Closed automatically from autosync."
    error_budget_max_consecutive_failures: int = 3
    error_budget_max_failure_rate: float = 0.5
    error_budget_escalation_after: int = 5
    autosync_stale_snapshot_seconds: int = 3600
    connector_circuit_breaker_failure_threshold: int = 3
    connector_circuit_breaker_success_threshold: int = 1
    connector_circuit_breaker_timeout_seconds: float = 60.0
    autosync_prometheus_export_path: Path | None = None
    cycle_metrics_path: Path | None = None
    writer_lock_enabled: bool = True
    writer_lock_path: Path | None = None
    rate_limit_max_retries: int = 2
    rate_limit_initial_wait: float = 1.0
    rate_limit_max_wait: float = 16.0
    rate_limit_multiplier: float = 2.0
    standalone_mode: bool = True  # Always succeed, even if credentials missing

    @property
    def effective_partition_size(self) -> int:
        """Return a bounded partition size for planning."""
        return max(1, self.max_partition_size)

    @property
    def normalized_wl_ignore_list(self) -> list[str]:
        """Return canonical WL IDs to skip during sync cycles."""
        normalized: set[str] = set()
        for raw in self.wl_ignore_list:
            candidate = raw.strip().upper()
            if not candidate:
                continue
            if not WL_ID_PATTERN.fullmatch(candidate):
                raise ValueError(f"Invalid WL ignore ID: {raw}")
            normalized.add(candidate)
        return sorted(normalized)

    @property
    def normalized_scope_areas(self) -> set[str]:
        return {area.strip().lower() for area in self.scope_areas if area.strip()}

    @property
    def normalized_scope_statuses(self) -> set[str]:
        return {status.strip().upper() for status in self.scope_statuses if status.strip()}

    @property
    def normalized_scope_priorities(self) -> set[str]:
        return {priority.strip().upper() for priority in self.scope_priorities if priority.strip()}

    @property
    def normalized_scope_wl_ranges(self) -> list[tuple[int, int]]:
        ranges: list[tuple[int, int]] = []
        for raw in self.scope_wl_ranges:
            token = raw.strip().upper()
            if not token:
                continue
            if ".." not in token:
                raise ValueError(f"Invalid WL range filter: {raw}")
            start_raw, end_raw = token.split("..", 1)
            if not start_raw.startswith("WL-") or not end_raw.startswith("WL-"):
                raise ValueError(f"Invalid WL range filter: {raw}")
            try:
                start_num = int(start_raw[3:])
                end_num = int(end_raw[3:])
            except ValueError as exc:
                raise ValueError(f"Invalid WL range filter: {raw}") from exc
            if end_num < start_num:
                raise ValueError(f"WL range end must be >= start: {raw}")
            ranges.append((start_num, end_num))
        return ranges

    def matches_scope_filters(self, item: "WorkstreamItem") -> bool:
        """Return whether a work item is included by configured sync scope filters."""
        if self.normalized_scope_areas and item.area.strip().lower() not in self.normalized_scope_areas:
            return False
        if self.normalized_scope_statuses and item.status.strip().upper() not in self.normalized_scope_statuses:
            return False
        if self.normalized_scope_priorities and item.priority.strip().upper() not in self.normalized_scope_priorities:
            return False
        wl_ranges = self.normalized_scope_wl_ranges
        if wl_ranges:
            if not item.item_id.upper().startswith("WL-"):
                return False
            try:
                wl_number = int(item.item_id[3:])
            except ValueError:
                return False
            return any(start <= wl_number <= end for start, end in wl_ranges)
        return True

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

    def is_maintenance_active(self, connector: str, at: datetime | None = None, project: str | None = None) -> bool:
        """Return whether a connector is currently in planned maintenance."""
        now = at or datetime.now(timezone.utc)
        target = connector.lower()
        project_target = (project or self.project_id).strip().lower()
        for window in self.maintenance_windows:
            if window.connector not in (target, "all", "*"):
                continue
            if window.project.strip().lower() not in {project_target, "all", "*"}:
                continue
            if window.is_active(now):
                return True
        return False

    def is_emergency_stop_active(self) -> bool:
        """Return whether emergency-stop controls are active."""
        if not self.emergency_stop_enabled:
            return False

        env_value = os.getenv(self.emergency_stop_env_var, "").strip().lower()
        if env_value in {"1", "true", "yes", "on"}:
            return True

        stop_path = self.emergency_stop_file_path
        if stop_path and stop_path.exists():
            return True

        return False

    def effective_github_project_number(self) -> int:
        """Return effective GitHub project target (sandbox-aware)."""
        if self.github_sandbox_mode and self.github_sandbox_project_number > 0:
            return self.github_sandbox_project_number
        return self.github_project_number


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


class RetryClass(str, Enum):
    """Error classes driving retry/backoff policy."""

    TRANSIENT = "transient"
    RATE_LIMIT = "rate_limit"
    PERMANENT = "permanent"


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
    correlation_id: str | None = None
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
            "correlation_id": self.correlation_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class SyncCycleManifest:
    """Append-only cycle manifest for reproducible autosync audit."""

    cycle_number: int
    started_at: str
    status: str
    inputs: dict[str, Any]
    decisions: dict[str, Any]
    outputs: dict[str, Any]
    previous_manifest_hash: str = ""
    manifest_hash: str = ""

    def with_hash(self) -> "SyncCycleManifest":
        """Return a copy with deterministic manifest hash."""
        payload = {
            "cycle_number": self.cycle_number,
            "started_at": self.started_at,
            "status": self.status,
            "inputs": self.inputs,
            "decisions": self.decisions,
            "outputs": self.outputs,
            "previous_manifest_hash": self.previous_manifest_hash,
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        return SyncCycleManifest(
            cycle_number=self.cycle_number,
            started_at=self.started_at,
            status=self.status,
            inputs=self.inputs,
            decisions=self.decisions,
            outputs=self.outputs,
            previous_manifest_hash=self.previous_manifest_hash,
            manifest_hash=digest,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_number": self.cycle_number,
            "started_at": self.started_at,
            "status": self.status,
            "inputs": self.inputs,
            "decisions": self.decisions,
            "outputs": self.outputs,
            "previous_manifest_hash": self.previous_manifest_hash,
            "manifest_hash": self.manifest_hash,
        }


class SyncFailureQueue:
    """Store and prune recent sync failures."""

    def __init__(self, retention_seconds: int) -> None:
        self.retention_seconds = max(1, retention_seconds)
        self._entries: list[FailureRecord] = []

    def push(
        self,
        operation_id: str,
        connector: str,
        item_id: str,
        message: str,
        *,
        retry_class: RetryClass = RetryClass.PERMANENT,
        correlation_id: str | None = None,
    ) -> None:
        """Record a failed item operation."""
        self._entries.append(
            FailureRecord(
                operation_id=operation_id,
                connector=connector,
                item_id=item_id,
                message=message,
                occurred_at=datetime.now(timezone.utc),
                retry_class=retry_class.value,
                correlation_id=correlation_id,
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
            title = match.group(2)
            body = match.group(3)
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
            return f"### [{item_id}] {title}\n{replacement}"

        pattern = re.compile(
            r"###\s+\[(WL-\d+)\]\s+(.+?)\n((?:.|\n)*?)(?=\n###\s+\[WL-|\Z)",
            re.MULTILINE,
        )
        return pattern.sub(_rewrite_section, text)

    @classmethod
    def sync_status_annotations(cls, text: str, *, statuses: dict[str, str]) -> str:
        """Ensure status lines are synchronized from remote updates."""
        if not statuses:
            return text

        def _rewrite_section(match: re.Match[str]) -> str:
            item_id = match.group(1)
            title = match.group(2)
            body = match.group(3)
            remote_status = statuses.get(item_id)
            if not remote_status:
                return match.group(0)

            status_line = f"**Status:** {remote_status}"
            if cls.STATUS_PATTERN.search(body):
                updated_body = cls.STATUS_PATTERN.sub(status_line, body)
            elif body.strip():
                updated_body = f"{status_line}\n{body}"
            else:
                updated_body = f"{status_line}\n"

            return f"### [{item_id}] {title}\n{updated_body}"

        pattern = re.compile(
            r"###\s+\[(WL-\d+)\]\s+(.+?)\n((?:.|\n)*?)(?=\n###\s+\[WL-|\Z)",
            re.MULTILINE,
        )
        return pattern.sub(_rewrite_section, text)


def build_owner_metadata(owner: str) -> dict[str, str]:
    """Build canonical owner fields for local/GitHub/Linear propagation."""
    normalized = owner.strip()
    if not normalized:
        raise ValueError("owner must not be empty")
    return {
        "owner": normalized,
        "github_owner": normalized,
        "linear_assignee": normalized,
    }


def validate_env_profile_drift(
    profiles: dict[str, dict[str, str]],
    required_keys: set[str],
    allowed_drift_keys: set[str] | None = None,
) -> tuple[bool, dict[str, list[str]]]:
    """Validate required autosync keys are consistent across env profiles."""
    allowed = allowed_drift_keys or set()
    drift: dict[str, list[str]] = {}
    env_names = sorted(profiles.keys())
    for env_name in env_names:
        profile = profiles[env_name]
        missing = sorted(key for key in required_keys if key not in profile)
        if missing:
            drift[f"{env_name}:missing"] = missing

    for key in sorted(required_keys):
        if key in allowed:
            continue
        values = {profiles[name].get(key, "") for name in env_names}
        if len(values) > 1:
            drift[f"drift:{key}"] = sorted(values)

    return len(drift) == 0, drift


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
        self._last_ignored_item_ids: list[str] = []
        self._last_scope_filtered_item_ids: list[str] = []
        self._last_connector_probe: list[ConnectorHealthProbeResult] = []
        self._next_cycle_interval_seconds = self.config.cycle_interval_seconds
        self._latest_incident_snapshot: dict[str, Any] | None = None
        self._idempotency_cache = IdempotencyCache()
        self._error_budget = ErrorBudgetTracker(
            ErrorBudgetConfig(
                max_consecutive_failures=self.config.error_budget_max_consecutive_failures,
                max_failure_rate=self.config.error_budget_max_failure_rate,
                escalation_after=self.config.error_budget_escalation_after,
            ),
        )
        self._metrics = get_metrics_collector()
        self._breaker_registry = ProviderCircuitBreakerRegistry.get_instance()
        self._current_run_correlation_id: str | None = None
        self._last_cycle_fingerprint: str | None = None
        self._slo_alerts: list[str] = []
        self._last_slo_escalation_signature: str | None = None
        self._local_orphan_report: dict[str, Any] = {
            "local_ids": [],
            "mapped_remote_ids": [],
            "local_orphan_ids": [],
            "orphan_count": 0,
        }
        self._no_op_summary: dict[str, Any] | None = None
        self._last_trend_sample: dict[str, Any] | None = None
        self._rate_limit_backoff = RateLimitBackoffManager(
            RateLimitConfig(
                max_retries=max(0, int(self.config.rate_limit_max_retries)),
                initial_wait=max(0.01, float(self.config.rate_limit_initial_wait)),
                max_wait=max(0.01, float(self.config.rate_limit_max_wait)),
                multiplier=max(1.0, float(self.config.rate_limit_multiplier)),
            )
        )
        self._writer_lock = SingleWriterLock(lock_path=self._writer_lock_path())

    def _connector_breaker(self, connector: str) -> Any:
        config = ProviderCircuitBreakerConfig(
            failure_threshold=max(1, self.config.connector_circuit_breaker_failure_threshold),
            success_threshold=max(1, self.config.connector_circuit_breaker_success_threshold),
            timeout_sec=max(0.1, self.config.connector_circuit_breaker_timeout_seconds),
        )
        return self._breaker_registry.get(connector, config=config)

    def _connector_timeout_seconds(self, connector: str, direction: str) -> float:
        if connector == "github" and direction == "write":
            return max(0.001, self.config.github_write_timeout_seconds)
        if connector == "github" and direction == "read":
            return max(0.001, self.config.github_read_timeout_seconds)
        if connector == "linear" and direction == "write":
            return max(0.001, self.config.linear_write_timeout_seconds)
        if connector == "linear" and direction == "read":
            return max(0.001, self.config.linear_read_timeout_seconds)
        raise ValueError(f"Unsupported connector timeout target: {connector}/{direction}")

    def _autosync_metrics_export_path(self) -> Path:
        default_path = Path("docs/reference/workstream_autosync_metrics.prom")
        return self.config.autosync_prometheus_export_path or default_path

    def _cycle_metrics_path(self) -> Path:
        default_cycle_metrics_path = Path("docs/reference/workstream_autosync_cycle_metrics.jsonl")
        return self.config.cycle_metrics_path or default_cycle_metrics_path

    def _writer_lock_path(self) -> Path:
        if self.config.writer_lock_path is not None:
            return self.config.writer_lock_path
        if self.config.work_stream_path is not None:
            return self.config.work_stream_path.parent / "autosync.lock"
        return SingleWriterLock.DEFAULT_LOCK_PATH

    def _writer_lock_owner(self) -> str:
        actor_id = self.config.actor_id.strip()
        if actor_id:
            return actor_id
        return f"pid-{os.getpid()}"

    def _requires_writer_lock(self) -> bool:
        return (
            self.config.writer_lock_enabled
            and not self.config.dry_run
            and not self.config.simulation_mode
            and (self.config.github_can_write() or self.config.linear_can_write())
        )

    def _escalation_session_dir(self) -> Path:
        status_path = self.config.status_file_path or Path("docs/reference/autosync_status.json")
        return status_path.parent

    def _latest_snapshot_age_seconds(self) -> int | None:
        status_path = self.config.status_file_path or Path("docs/reference/autosync_status.json")
        snapshot_candidates = sorted(status_path.parent.glob("autosync_snapshot_*.json"))
        if not snapshot_candidates:
            return None
        try:
            latest = max(snapshot_candidates, key=lambda path: path.stat().st_mtime)
            age_delta = datetime.now(timezone.utc) - datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
            return max(0, int(age_delta.total_seconds()))
        except OSError:
            return None

    def _evaluate_slo_state(self) -> list[str]:
        alerts: list[str] = []
        snapshot_age = self._latest_snapshot_age_seconds()
        if snapshot_age is not None and snapshot_age > self.config.autosync_stale_snapshot_seconds:
            alerts.append(f"autosync snapshot stale for {snapshot_age}s")

        if self._error_budget.should_escalate():
            alerts.append("autosync error budget escalation threshold reached")

        if self._error_budget.should_hard_fail():
            alerts.append("autosync error budget hard-fail threshold reached")

        return alerts

    def _maybe_enqueue_escalation(self, reason: str) -> None:
        if not reason or self.config.dry_run:
            return
        if not self._current_run_correlation_id:
            return
        signature = hashlib.sha1(f"{self._current_run_correlation_id}:{reason}".encode()).hexdigest()
        if signature == self._last_slo_escalation_signature:
            return

        escalation_queue = EscalationQueue(self._escalation_session_dir())
        escalation_queue.add(
            run_id=self._current_run_correlation_id,
            reason=reason,
            sla_minutes=max(1, int(self.config.autosync_stale_snapshot_seconds / 60)),
            owner=self.config.actor_id.strip() or None,
            agent="autosync",
            lane="autosync",
            priority=1,
        )
        self._last_slo_escalation_signature = signature
        logger.warning("Autosync SLO escalation queued: %s", reason)

    def _flush_prometheus_metrics(self) -> None:
        self._metrics.export_text_file(self._autosync_metrics_export_path())

    def _cycle_manifest_path(self) -> Path:
        default_cycle_manifest_path = Path("artifacts/workstream_autosync_cycle_manifest.jsonl")
        return self.config.cycle_manifest_path or default_cycle_manifest_path

    def _read_last_manifest_hash(self) -> str:
        path = self._cycle_manifest_path()
        if not path.exists():
            return ""
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return ""
        last_payload = json.loads(lines[-1])
        manifest_hash = last_payload.get("manifest_hash")
        if isinstance(manifest_hash, str):
            return manifest_hash
        return ""

    def _append_cycle_manifest(
        self,
        *,
        status: str,
        started_at: datetime,
        items: list[WorkstreamItem],
        decisions: dict[str, Any],
        outputs: dict[str, Any],
    ) -> None:
        manifest = SyncCycleManifest(
            cycle_number=self.total_cycles + 1,
            started_at=started_at.isoformat(),
            status=status,
            inputs={
                "item_count": len(items),
                "item_ids": sorted(item.item_id for item in items),
                "shadow_mode": self.config.shadow_mode,
            },
            decisions=decisions,
            outputs=outputs,
            previous_manifest_hash=self._read_last_manifest_hash(),
        ).with_hash()
        path = self._cycle_manifest_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(manifest.to_dict(), sort_keys=True) + "\n")

    @staticmethod
    def _build_operation_id(platform: str, direction: str, items: list[WorkstreamItem]) -> str:
        """Build replay-safe deterministic operation IDs for sync batches."""
        item_key = ",".join(sorted(item.item_id for item in items))
        digest = hashlib.sha1(f"{platform}:{direction}:{item_key}".encode()).hexdigest()[:12]
        return f"{platform}-{direction}-{digest}"

    @staticmethod
    def _build_mutation_id(platform: str, item: WorkstreamItem) -> str:
        """Build a deterministic mutation identifier for one item write."""
        payload = f"{platform}:{item.item_id}:{item.status}:{item.priority}:{item.area}"
        digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]
        return f"{platform}-mutation-{item.item_id}-{digest}"

    def _enforce_write_guards(self, *, connector: str, items: list[WorkstreamItem]) -> None:
        """Fail-fast guard for write-capable sync entrypoints."""
        if self.config.is_emergency_stop_active():
            raise WorkstreamAutosyncConfigError(
                "Emergency stop active; write-capable autosync entrypoint is disabled",
            )
        if self.config.require_actor_identity:
            payload = ",".join(sorted(item.item_id for item in items))
            SSHIdentityProxy.require_actor_identity(
                actor_id=self.config.actor_id,
                signature=self.config.actor_signature,
                payload=payload,
                signing_key=self.config.actor_signing_key,
            )
        required = self.config.required_connector_capabilities.get(connector, [])
        if required:
            discovery = ConnectorCapabilityDiscovery(
                lambda key: self.config.connector_capabilities.get(key, []),
            )
            available = discovery.discover(connector, refresh=True)
            missing = CapabilityMismatchDetector(required).check_connector(connector, available)
            if missing:
                raise WorkstreamAutosyncConfigError(
                    f"Connector capability mismatch for {connector}: missing {', '.join(missing)}",
                )
        if self.config.payload_checksum_enforced:
            payload = [item.to_dict() for item in items]
            verify_payload_checksum(payload, self.config.expected_payload_checksum)

    @staticmethod
    def _xor_encrypt(data: bytes, key: str) -> str:
        key_bytes = key.encode("utf-8")
        encrypted = bytes(data[index] ^ key_bytes[index % len(key_bytes)] for index in range(len(data)))
        return base64.b64encode(encrypted).decode("utf-8")

    @staticmethod
    def _xor_decrypt(payload: str, key: str) -> str:
        key_bytes = key.encode("utf-8")
        raw = base64.b64decode(payload.encode("utf-8"))
        decrypted = bytes(raw[index] ^ key_bytes[index % len(key_bytes)] for index in range(len(raw)))
        return decrypted.decode("utf-8")

    def _artifact_encryption_key(self) -> str:
        key = self.config.artifact_encryption_key or os.getenv("THGENT_AUTOSYNC_ARTIFACT_KEY", "")
        if self.config.artifact_encryption_enabled and not key:
            raise WorkstreamAutosyncConfigError(
                "Artifact encryption is enabled but no key is configured (THGENT_AUTOSYNC_ARTIFACT_KEY)."
            )
        return key

    def _serialize_artifact_payload(self, payload: Any) -> str:
        text = json.dumps(payload, indent=2)
        if not self.config.artifact_encryption_enabled:
            return text
        key = self._artifact_encryption_key()
        encrypted = {
            "encrypted": True,
            "algorithm": "xor-v1",
            "ciphertext_b64": self._xor_encrypt(text.encode("utf-8"), key),
        }
        return json.dumps(encrypted, indent=2)

    def _deserialize_artifact_payload(self, raw_text: str) -> Any:
        payload = json.loads(raw_text)
        if not isinstance(payload, dict) or payload.get("encrypted") is not True:
            return payload
        if payload.get("algorithm") != "xor-v1":
            raise WorkstreamAutosyncConfigError("Unsupported encrypted artifact algorithm.")
        ciphertext = payload.get("ciphertext_b64")
        if not isinstance(ciphertext, str):
            raise WorkstreamAutosyncConfigError("Encrypted artifact is missing ciphertext_b64.")
        key = self._artifact_encryption_key()
        decrypted_text = self._xor_decrypt(ciphertext, key)
        return json.loads(decrypted_text)

    def _compute_local_orphan_report(self, items: list[WorkstreamItem]) -> dict[str, Any]:
        local_ids = sorted(item.item_id for item in items)
        mapped_remote_ids: set[str] = set()
        for item in items:
            if item.board_id:
                mapped_remote_ids.add(item.item_id)

        mapping_path = self.config.connector_mapping_cache_path
        if mapping_path is None:
            mapping_path = Path("docs/reference/connector_mapping_cache.json")
        if mapping_path.exists():
            mapping_cache = ConnectorMappingCache(cache_file=mapping_path)
            mapped_remote_ids.update(mapping_cache.list_cached_wl_ids("github"))
            mapped_remote_ids.update(mapping_cache.list_cached_wl_ids("linear"))

        orphan_ids = sorted(set(local_ids) - mapped_remote_ids)
        return {
            "local_ids": local_ids,
            "mapped_remote_ids": sorted(mapped_remote_ids),
            "local_orphan_ids": orphan_ids,
            "orphan_count": len(orphan_ids),
        }

    def _build_remote_reflection_status_updates(
        self,
        *,
        local_items: list[WorkstreamItem],
        remote_status_updates: dict[str, str],
    ) -> dict[str, str]:
        """Apply remote archive/delete policy for local items absent in remote snapshots."""
        merged_updates = dict(remote_status_updates)
        if self.config.remote_missing_item_policy == RemoteMissingItemPolicy.IGNORE:
            return merged_updates

        local_ids = {item.item_id for item in local_items}
        remote_ids = set(remote_status_updates.keys())
        missing_ids = sorted(local_ids - remote_ids)
        if not missing_ids:
            return merged_updates

        policy_status = (
            "ARCHIVED" if self.config.remote_missing_item_policy == RemoteMissingItemPolicy.ARCHIVE else "DELETED"
        )
        for item_id in missing_ids:
            merged_updates[item_id] = policy_status
        return merged_updates

    @staticmethod
    def _classify_retry(message: str) -> RetryClass:
        lowered = message.lower()
        if "429" in lowered or "rate limit" in lowered or "quota" in lowered:
            return RetryClass.RATE_LIMIT
        if "timeout" in lowered or "temporar" in lowered or "network" in lowered or "connection reset" in lowered:
            return RetryClass.TRANSIENT
        return RetryClass.PERMANENT

    def _compute_cycle_fingerprint(self, items: list[WorkstreamItem]) -> str:
        canonical = "|".join(
            sorted(
                f"{item.item_id}:{item.status}:{item.priority}:{item.area}:{item.blocked_by or ''}" for item in items
            )
        )
        return hashlib.sha1(canonical.encode("utf-8")).hexdigest()

    def _trend_path(self) -> Path:
        return self.config.trend_file_path or Path("docs/reference/autosync_trend.jsonl")

    def _append_trend_sample(
        self,
        *,
        started_at: datetime,
        completed_at: datetime,
        item_count: int,
        no_op: bool,
        no_op_reason: str | None,
    ) -> None:
        sample = {
            "captured_at": completed_at.isoformat(),
            "duration_seconds": max(0.0, (completed_at - started_at).total_seconds()),
            "item_count": item_count,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "orphan_count": int(self._local_orphan_report.get("orphan_count", 0)),
            "no_op": no_op,
            "no_op_reason": no_op_reason,
            "correlation_id": self._current_run_correlation_id,
        }
        path = self._trend_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(sample, sort_keys=True) + "\n")
        self._last_trend_sample = sample

    def _emit_cycle_metrics(
        self,
        *,
        started_at: datetime,
        completed_at: datetime,
        item_count: int,
        status: str,
        no_op: bool,
        no_op_reason: str | None,
    ) -> None:
        payload = {
            "captured_at": completed_at.isoformat(),
            "cycle_number": self.total_cycles,
            "status": status,
            "duration_seconds": max(0.0, (completed_at - started_at).total_seconds()),
            "item_count": item_count,
            "no_op": no_op,
            "no_op_reason": no_op_reason,
            "last_error": self.last_error,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "next_cycle_interval_seconds": self._next_cycle_interval_seconds,
            "connector_health": [probe.to_dict() for probe in self._last_connector_probe],
            "correlation_id": self._current_run_correlation_id,
        }
        path = self._cycle_metrics_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def _compact_snapshots(self, status_path: Path) -> None:
        retention = max(1, int(self.config.snapshot_retention_count))
        snapshots = sorted(status_path.parent.glob("autosync_snapshot_*.json"))
        if len(snapshots) <= retention:
            return
        for snapshot in snapshots[: len(snapshots) - retention]:
            snapshot.unlink(missing_ok=True)

    @staticmethod
    def simulate_connector_chaos(
        connector: str,
        scenario: str,
        *,
        items_count: int,
    ) -> dict[str, Any]:
        """Deterministic chaos fixture for outage and partial-ack scenarios."""
        normalized = scenario.strip().lower()
        if normalized == "timeout":
            return {
                "connector": connector,
                "scenario": normalized,
                "items_attempted": items_count,
                "items_acked": 0,
                "retry_count": 3,
                "backoff_seconds": [1, 2, 4],
                "escalate": True,
                "outcome": "outage",
            }
        if normalized == "http_5xx":
            return {
                "connector": connector,
                "scenario": normalized,
                "items_attempted": items_count,
                "items_acked": 0,
                "retry_count": 2,
                "backoff_seconds": [1, 2],
                "escalate": True,
                "outcome": "server_error",
            }
        if normalized == "partial_ack":
            acked = 0 if items_count <= 1 else items_count - 1
            return {
                "connector": connector,
                "scenario": normalized,
                "items_attempted": items_count,
                "items_acked": acked,
                "retry_count": 1,
                "backoff_seconds": [1],
                "escalate": acked != items_count,
                "outcome": "partial",
            }
        raise ValueError(f"Unsupported chaos scenario: {scenario}")

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
                await asyncio.sleep(self._next_cycle_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in autosync cycle: %s", e, exc_info=True)
                await asyncio.sleep(min(self._next_cycle_interval_seconds, 60))

    def _probe_connectors(self) -> list[ConnectorHealthProbeResult]:
        """Probe connector health and return deterministic statuses."""
        probes: list[ConnectorHealthProbeResult] = []
        if self.config.should_sync_github():
            status = self.config.connector_health_states.get("github", "healthy").strip().lower()
            if status not in {"healthy", "degraded", "down"}:
                status = "healthy"
            probes.append(ConnectorHealthProbeResult(connector="github", status=status))
        if self.config.should_sync_linear():
            status = self.config.connector_health_states.get("linear", "healthy").strip().lower()
            if status not in {"healthy", "degraded", "down"}:
                status = "healthy"
            probes.append(ConnectorHealthProbeResult(connector="linear", status=status))
        return probes

    def _metadata_state(self) -> dict[str, Any]:
        """Compute metadata freshness state."""
        refreshed_at = self.config.metadata_last_refreshed_at
        if refreshed_at is None:
            return {"status": "fresh", "age_seconds": 0}
        now = datetime.now(timezone.utc)
        age_seconds = int((now - refreshed_at).total_seconds())
        stale = age_seconds > self.config.metadata_ttl_seconds
        return {
            "status": "stale" if stale else "fresh",
            "age_seconds": max(0, age_seconds),
        }

    def _build_incident_snapshot_bundle(
        self,
        *,
        items_count: int,
        metadata_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Build immutable incident snapshot payload for the current cycle."""
        policy_hash = hashlib.sha1(
            json.dumps(
                {
                    "strict_tag_validation": self.config.strict_tag_validation,
                    "strict_title_validation": self.config.strict_title_validation,
                    "adaptive_interval_enabled": self.config.adaptive_interval_enabled,
                    "metadata_ttl_seconds": self.config.metadata_ttl_seconds,
                },
                sort_keys=True,
            ).encode("utf-8"),
        ).hexdigest()
        return {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "items_count": items_count,
            "policy_hash": policy_hash,
            "connector_health": [probe.to_dict() for probe in self._last_connector_probe],
            "metadata": metadata_state,
            "last_error": self.last_error,
            "failure_queue_size": len(self._failure_queue.snapshot()),
            "mutation_summary": self.last_operation.to_dict() if self.last_operation else None,
        }

    def _append_incident_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Append snapshot bundle to incident artifact stream."""
        path = self.config.incident_bundle_path or Path("docs/reference/workstream_incident_snapshots.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(snapshot, sort_keys=True) + "\n")

    def _update_next_cycle_interval(self, *, items_count: int) -> None:
        """Compute and set next-cycle interval."""
        if not self.config.adaptive_interval_enabled:
            self._next_cycle_interval_seconds = self.config.cycle_interval_seconds
            return
        queue_size = len(self._failure_queue.snapshot())
        drift_rate = 1.0 if self._latest_blocker_digest else 0.0
        error_rate = 1.0 if self.last_error else 0.0
        load_factor = min(1.0, float(items_count + queue_size) / 200.0)
        self._next_cycle_interval_seconds = compute_adaptive_sync_interval(
            base_interval_seconds=self.config.cycle_interval_seconds,
            min_interval_seconds=self.config.adaptive_interval_min_seconds,
            max_interval_seconds=self.config.adaptive_interval_max_seconds,
            drift_rate=drift_rate,
            error_rate=error_rate,
            load_factor=load_factor,
        )

    async def _perform_sync_cycle(self) -> None:
        """Perform a single sync cycle."""
        cycle_started_at = datetime.now(timezone.utc)
        cycle_monotonic_started = time.perf_counter()
        no_op = False
        no_op_reason: str | None = None
        cycle_items: list[WorkstreamItem] = []
        writer_lock_owner: str | None = None
        writer_lock_acquired = False
        cycle_decisions: dict[str, Any] = {
            "github_enabled": self.config.should_sync_github(),
            "linear_enabled": self.config.should_sync_linear(),
            "shadow_mode": self.config.shadow_mode,
        }

        def _record_cycle_status(status: str) -> None:
            duration = time.perf_counter() - cycle_monotonic_started
            self._metrics.record_autosync_cycle_result(status=status, duration_seconds=duration)

        try:
            if self._requires_writer_lock():
                writer_lock_owner = self._writer_lock_owner()
                if not self._writer_lock.acquire(writer_lock_owner):
                    current_owner = self._writer_lock.get_owner() or "unknown"
                    raise WorkstreamAutosyncError(
                        f"single-writer lock unavailable: held by {current_owner}",
                    )
                writer_lock_acquired = True
                cycle_decisions["writer_lock_owner"] = writer_lock_owner

            if self.config.is_emergency_stop_active():
                raise WorkstreamAutosyncConfigError(
                    "Emergency stop active; autosync external mutation is paused",
                )
            self._current_run_correlation_id = str(uuid4())
            self._no_op_summary = None

            work_stream_path = self.config.work_stream_path or Path("docs/reference/WORK_STREAM.md")
            raw_content = ""
            if work_stream_path.exists():
                raw_content = work_stream_path.read_text(encoding="utf-8")

            # Parse local items
            items = WorkstreamParser.parse_items(work_stream_path)
            ignore_set = set(self.config.normalized_wl_ignore_list)
            self._last_ignored_item_ids = sorted(item.item_id for item in items if item.item_id in ignore_set)
            if self._last_ignored_item_ids:
                items = [item for item in items if item.item_id not in ignore_set]
            self._last_scope_filtered_item_ids = sorted(
                item.item_id for item in items if not self.config.matches_scope_filters(item)
            )
            if self._last_scope_filtered_item_ids:
                items = [item for item in items if self.config.matches_scope_filters(item)]
            cycle_items = items
            self._local_orphan_report = self._compute_local_orphan_report(items)
            if not items:
                logger.debug("No work stream items to sync")
                self._clear_checkpoint()
                no_op = True
                no_op_reason = "no_workstream_items"
                self._no_op_summary = {
                    "no_op": True,
                    "reason": no_op_reason,
                    "skipped_connectors": int(self.config.should_sync_github()) + int(self.config.should_sync_linear()),
                }
                self.total_cycles += 1
                self.last_error = None
                self._update_next_cycle_interval(items_count=0)
                self._latest_incident_snapshot = self._build_incident_snapshot_bundle(
                    items_count=0,
                    metadata_state=self._metadata_state(),
                )
                self._append_incident_snapshot(self._latest_incident_snapshot)
                self._metrics.record_autosync_cycle(
                    items_count=0,
                    ignored_count=len(self._last_ignored_item_ids),
                    had_error=False,
                )
                self._flush_prometheus_metrics()
                self._write_status_snapshot()
                self._append_trend_sample(
                    started_at=cycle_started_at,
                    completed_at=datetime.now(timezone.utc),
                    item_count=0,
                    no_op=no_op,
                    no_op_reason=no_op_reason,
                )
                self._emit_cycle_metrics(
                    started_at=cycle_started_at,
                    completed_at=datetime.now(timezone.utc),
                    item_count=0,
                    status="success",
                    no_op=no_op,
                    no_op_reason=no_op_reason,
                )
                self._append_cycle_manifest(
                    status="success",
                    started_at=cycle_started_at,
                    items=[],
                    decisions={**cycle_decisions, "reason": "no_items"},
                    outputs={"total_cycles": self.total_cycles},
                )
                _record_cycle_status("success")
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

            self._last_connector_probe = self._probe_connectors()
            unhealthy = [probe for probe in self._last_connector_probe if probe.status != "healthy"]
            if unhealthy:
                failed = ", ".join(f"{probe.connector}:{probe.status}" for probe in unhealthy)
                raise WorkstreamAutosyncError(f"Pre-apply connector health probe failed: {failed}")

            self.last_sync_time = datetime.now(timezone.utc)
            logger.debug("Performing sync cycle for %d items", len(items))
            self._failure_queue.prune_expired(self.last_sync_time)
            self._write_failure_queue()
            self._latest_blocker_digest = WorkstreamParser.open_blocker_digest(items)
            cycle_fingerprint = self._compute_cycle_fingerprint(items)
            if cycle_fingerprint == self._last_cycle_fingerprint:
                no_op = True
                no_op_reason = "unchanged_workstream_state"
                self._no_op_summary = {
                    "no_op": True,
                    "reason": no_op_reason,
                    "skipped_connectors": int(self.config.should_sync_github()) + int(self.config.should_sync_linear()),
                }
                self.total_cycles += 1
                self.last_error = None
                self._update_next_cycle_interval(items_count=len(items))
                self._latest_incident_snapshot = self._build_incident_snapshot_bundle(
                    items_count=len(items),
                    metadata_state=self._metadata_state(),
                )
                self._append_incident_snapshot(self._latest_incident_snapshot)
                self._metrics.record_autosync_cycle(
                    items_count=len(items),
                    ignored_count=len(self._last_ignored_item_ids),
                    had_error=False,
                )
                self._flush_prometheus_metrics()
                self._write_status_snapshot()
                self._append_trend_sample(
                    started_at=cycle_started_at,
                    completed_at=datetime.now(timezone.utc),
                    item_count=len(items),
                    no_op=no_op,
                    no_op_reason=no_op_reason,
                )
                self._emit_cycle_metrics(
                    started_at=cycle_started_at,
                    completed_at=datetime.now(timezone.utc),
                    item_count=len(items),
                    status="success",
                    no_op=no_op,
                    no_op_reason=no_op_reason,
                )
                self._append_cycle_manifest(
                    status="success",
                    started_at=cycle_started_at,
                    items=items,
                    decisions={**cycle_decisions, "reason": no_op_reason},
                    outputs={"total_cycles": self.total_cycles, "no_op": True},
                )
                _record_cycle_status("success")
                return
            cycle_decisions["open_blockers"] = list(self._latest_blocker_digest)
            metadata_state = self._metadata_state()

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

            if self.config.simulation_mode:
                no_op_reason = "simulation_mode"
                self._no_op_summary = {
                    "no_op": False,
                    "reason": "simulation_mode",
                    "skipped_connectors": int(self.config.should_sync_github()) + int(self.config.should_sync_linear()),
                }
            else:
                # Sync to GitHub if enabled
                if self.config.should_sync_github():
                    if self.config.is_maintenance_active("github", project=self.config.project_id):
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
                    if self.config.is_maintenance_active("linear", project=self.config.project_id):
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
            self._last_cycle_fingerprint = cycle_fingerprint
            self._update_next_cycle_interval(items_count=len(items))
            self._latest_incident_snapshot = self._build_incident_snapshot_bundle(
                items_count=len(items),
                metadata_state=metadata_state,
            )
            self._append_incident_snapshot(self._latest_incident_snapshot)
            self._metrics.record_autosync_cycle(
                items_count=len(items),
                ignored_count=len(self._last_ignored_item_ids),
                had_error=False,
            )
            self._flush_prometheus_metrics()
            self._write_status_snapshot()
            self._append_trend_sample(
                started_at=cycle_started_at,
                completed_at=datetime.now(timezone.utc),
                item_count=len(items),
                no_op=no_op,
                no_op_reason=no_op_reason,
            )
            self._emit_cycle_metrics(
                started_at=cycle_started_at,
                completed_at=datetime.now(timezone.utc),
                item_count=len(items),
                status="success",
                no_op=no_op,
                no_op_reason=no_op_reason,
            )
            self._append_cycle_manifest(
                status="success",
                started_at=cycle_started_at,
                items=items,
                decisions=cycle_decisions,
                outputs={
                    "total_cycles": self.total_cycles,
                    "last_operation": self.last_operation.to_dict() if self.last_operation else None,
                    "failure_queue_size": len(self._failure_queue.snapshot()),
                },
            )
            _record_cycle_status("success")

        except Exception as e:
            logger.error("Failed to perform sync cycle: %s", e, exc_info=True)
            self.total_cycles += 1
            self.last_error = str(e)
            self._update_next_cycle_interval(items_count=0)
            self._latest_incident_snapshot = self._build_incident_snapshot_bundle(
                items_count=0,
                metadata_state=self._metadata_state(),
            )
            self._append_incident_snapshot(self._latest_incident_snapshot)
            self._metrics.record_autosync_cycle(
                items_count=0,
                ignored_count=len(self._last_ignored_item_ids),
                had_error=True,
            )
            self._flush_prometheus_metrics()
            self._write_status_snapshot()
            self._append_trend_sample(
                started_at=cycle_started_at,
                completed_at=datetime.now(timezone.utc),
                item_count=0,
                no_op=no_op,
                no_op_reason=no_op_reason,
            )
            self._emit_cycle_metrics(
                started_at=cycle_started_at,
                completed_at=datetime.now(timezone.utc),
                item_count=0,
                status="failed",
                no_op=no_op,
                no_op_reason=no_op_reason,
            )
            self._append_cycle_manifest(
                status="failed",
                started_at=cycle_started_at,
                items=cycle_items,
                decisions=cycle_decisions,
                outputs={"total_cycles": self.total_cycles, "last_error": self.last_error},
            )
            _record_cycle_status("failed")
        finally:
            if writer_lock_acquired and writer_lock_owner:
                self._writer_lock.release(writer_lock_owner)

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
            "connector_health": [probe.to_dict() for probe in self._last_connector_probe],
            "next_cycle_interval_seconds": self._next_cycle_interval_seconds,
            "incident_snapshot": self._latest_incident_snapshot,
            "correlation_id": self._current_run_correlation_id,
            "local_orphan_report": self._local_orphan_report,
            "ignored_wl_ids": self._last_ignored_item_ids,
            "scope_filtered_wl_ids": self._last_scope_filtered_item_ids,
            "no_op_summary": self._no_op_summary,
            "trend_sample": self._last_trend_sample,
        }
        try:
            status_path.parent.mkdir(parents=True, exist_ok=True)
            serialized = self._serialize_artifact_payload(payload)
            status_path.write_text(serialized, encoding="utf-8")
            snapshot_name = datetime.now(timezone.utc).strftime("autosync_snapshot_%Y%m%dT%H%M%S%fZ.json")
            snapshot_path = status_path.parent / snapshot_name
            snapshot_path.write_text(serialized, encoding="utf-8")
            self._compact_snapshots(status_path)
        except OSError as exc:
            logger.warning("Failed to write autosync status to %s: %s", status_path, exc)

    async def _sync_to_github(self, items: list[WorkstreamItem]) -> None:
        """Sync items to GitHub Projects.

        Args:
            items: Work stream items to sync
        """
        if not self.config.github_can_write():
            return
        self._enforce_write_guards(connector="github", items=items)

        op = SyncOperation(
            operation_id=self._build_operation_id("gh", "write", items),
            platform="github",
            direction="write",
            correlation_id=self._current_run_correlation_id,
        )

        try:
            op.items_processed = len(items)
            _ = [
                enrich_sync_metadata(
                    item.to_dict(),
                    source_url=f"linear://workstream/{item.item_id}",
                    source_tag="linear",
                )
                for item in items
            ]
            if self.config.shadow_mode:
                logger.info("Shadow mode active: blocking %d GitHub mutations", len(items))
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self.last_operation = op
                return
            if self._idempotency_cache.check(op.operation_id):
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self.last_operation = op
                logger.info("Skipping replayed GitHub write operation: %s", op.operation_id)
                return

            if self.config.dry_run:
                logger.info(
                    "Dry-run: skip GitHub write sync (%d items to %s/%d)",
                    len(items),
                    self.config.github_owner,
                    self.config.effective_github_project_number(),
                )
                op.items_successful = len(items)
            else:
                gh_config = GHProjectConfig(
                    enabled=True,
                    owner=self.config.github_owner,
                    number=self.config.effective_github_project_number(),
                    direction=self.config.github_direction.value,
                    standalone_mode=self.config.standalone_mode,
                )
                enriched_items = [
                    enrich_sync_metadata(
                        item.to_dict(),
                        source_url=f"github://workstream/{item.item_id}",
                        source_tag="github",
                    )
                    for item in items
                ]
                result = await asyncio.to_thread(gh_sync_to_github, gh_config, enriched_items)
                created = int(result.get("items_created", 0))
                updated = int(result.get("items_updated", 0))
                op.items_successful = created + updated
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    op.errors.extend(str(error) for error in errors)

                error_ids = {
                    str(error).split(":", 1)[0].strip()
                    for error in op.errors
                    if isinstance(error, str) and ":" in error
                }
                successful_items = [item for item in items if item.item_id not in error_ids]
                for item in successful_items:
                    mutation_id = self._build_mutation_id("gh", item)
                    mutation_hash = hashlib.sha1(
                        f"{item.item_id}:{item.status}:{item.priority}:{item.area}".encode()
                    ).hexdigest()
                    if self._idempotency_cache.check_content("github", item.item_id, mutation_hash):
                        continue
                    self._idempotency_cache.record(
                        operation_id=mutation_id,
                        wl_id=item.item_id,
                        connector="github",
                        content_hash=mutation_hash,
                    )
                if successful_items:
                    self._idempotency_cache.record(
                        operation_id=op.operation_id,
                        wl_id=successful_items[0].item_id,
                        connector="github",
                        content_hash=hashlib.sha1(
                            ",".join(sorted(item.item_id for item in successful_items)).encode("utf-8")
                        ).hexdigest(),
                    )

            op.items_failed = max(0, op.items_processed - op.items_successful)

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except (GHProjectSyncError, ValueError, TypeError) as e:
            logger.error("Failed to sync to GitHub: %s", e, exc_info=True)
            op.items_failed = max(0, op.items_processed - op.items_successful)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise
        except Exception as e:
            logger.error("Unexpected GitHub write sync failure: %s", e, exc_info=True)
            op.items_failed = max(0, op.items_processed - op.items_successful)
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
            operation_id=self._build_operation_id("gh", "read", items),
            platform="github",
            direction="read",
            correlation_id=self._current_run_correlation_id,
        )

        try:
            op.items_processed = len(items)
            if self.config.dry_run:
                logger.info("Dry-run: skip GitHub read reflection (%d items)", len(items))
            else:
                gh_config = GHProjectConfig(
                    enabled=True,
                    owner=self.config.github_owner,
                    number=self.config.effective_github_project_number(),
                    direction=self.config.github_direction.value,
                    standalone_mode=self.config.standalone_mode,
                )
                result = await asyncio.to_thread(gh_sync_from_github, gh_config)
                remote_items = result.get("items", [])
                target_ids = {item.item_id for item in items}
                status_updates: dict[str, str] = {}
                if isinstance(remote_items, list):
                    for remote_item in remote_items:
                        if not isinstance(remote_item, dict):
                            continue
                        remote_item_id = str(remote_item.get("item_id") or "").strip()
                        remote_status = str(remote_item.get("status") or "").strip().upper()
                        if remote_item_id in target_ids and remote_status:
                            status_updates[remote_item_id] = remote_status

                status_updates = self._build_remote_reflection_status_updates(
                    local_items=items,
                    remote_status_updates=status_updates,
                )
                if status_updates:
                    content = work_stream_path.read_text(encoding="utf-8")
                    updated_content = WorkstreamParser.sync_status_annotations(content, statuses=status_updates)
                    if updated_content != content:
                        work_stream_path.write_text(updated_content, encoding="utf-8")
                op.items_successful = len(status_updates)
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    op.errors.extend(str(error) for error in errors)
            op.items_failed = max(0, op.items_processed - op.items_successful)

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except (GHProjectSyncError, OSError, ValueError, TypeError) as e:
            logger.error("Failed to sync from GitHub: %s", e, exc_info=True)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise
        except Exception as e:
            logger.error("Unexpected GitHub read sync failure: %s", e, exc_info=True)
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
        self._enforce_write_guards(connector="linear", items=items)

        op = SyncOperation(
            operation_id=self._build_operation_id("linear", "write", items),
            platform="linear",
            direction="write",
            correlation_id=self._current_run_correlation_id,
        )

        try:
            op.items_processed = len(items)
            if self.config.shadow_mode:
                logger.info("Shadow mode active: blocking %d Linear mutations", len(items))
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self.last_operation = op
                return
            if self._idempotency_cache.check(op.operation_id):
                op.completed_at = datetime.now(timezone.utc)
                op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
                self.last_operation = op
                logger.info("Skipping replayed Linear write operation: %s", op.operation_id)
                return

            if self.config.dry_run:
                logger.info(
                    "Dry-run: skip Linear write sync (%d items to team %s)", len(items), self.config.linear_team_key
                )
                op.items_successful = len(items)
            else:
                linear_config = LinearGraphQLConfig(
                    api_key=self.config.linear_api_key,
                    team_key=self.config.linear_team_key,
                    timeout_seconds=self.config.linear_write_timeout_seconds,
                )
                result = await asyncio.to_thread(linear_sync_to, linear_config, [item.to_dict() for item in items])
                created = int(result.get("items_created", 0))
                updated = int(result.get("items_updated", 0))
                op.items_successful = created + updated
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    op.errors.extend(str(error) for error in errors)

                error_ids = {
                    str(error).split(":", 1)[0].strip()
                    for error in op.errors
                    if isinstance(error, str) and ":" in error
                }
                successful_items = [item for item in items if item.item_id not in error_ids]
                for item in successful_items:
                    mutation_id = self._build_mutation_id("linear", item)
                    mutation_hash = hashlib.sha1(
                        f"{item.item_id}:{item.status}:{item.priority}:{item.area}".encode()
                    ).hexdigest()
                    if self._idempotency_cache.check_content("linear", item.item_id, mutation_hash):
                        continue
                    self._idempotency_cache.record(
                        operation_id=mutation_id,
                        wl_id=item.item_id,
                        connector="linear",
                        content_hash=mutation_hash,
                    )
                if successful_items:
                    self._idempotency_cache.record(
                        operation_id=op.operation_id,
                        wl_id=successful_items[0].item_id,
                        connector="linear",
                        content_hash=hashlib.sha1(
                            ",".join(sorted(item.item_id for item in successful_items)).encode("utf-8")
                        ).hexdigest(),
                    )

            op.items_failed = max(0, op.items_processed - op.items_successful)

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except (LinearGraphQLAuthError, LinearGraphQLError, ValueError, TypeError) as e:
            logger.error("Failed to sync to Linear: %s", e, exc_info=True)
            op.items_failed = max(0, op.items_processed - op.items_successful)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise
        except Exception as e:
            logger.error("Unexpected Linear write sync failure: %s", e, exc_info=True)
            op.items_failed = max(0, op.items_processed - op.items_successful)
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
            operation_id=self._build_operation_id("linear", "read", items),
            platform="linear",
            direction="read",
            correlation_id=self._current_run_correlation_id,
        )

        try:
            op.items_processed = len(items)
            if self.config.dry_run:
                logger.info("Dry-run: skip Linear read reflection (%d items)", len(items))
            else:
                linear_config = LinearGraphQLConfig(
                    api_key=self.config.linear_api_key,
                    team_key=self.config.linear_team_key,
                    timeout_seconds=self.config.linear_read_timeout_seconds,
                )
                result = await asyncio.to_thread(linear_sync_from, linear_config)
                remote_items = result.get("items", [])
                target_ids = {item.item_id for item in items}
                status_updates: dict[str, str] = {}
                if isinstance(remote_items, list):
                    for remote_item in remote_items:
                        if not isinstance(remote_item, dict):
                            continue
                        remote_item_id = str(remote_item.get("item_id") or "").strip()
                        remote_status = str(remote_item.get("status") or "").strip().upper()
                        if remote_item_id in target_ids and remote_status:
                            status_updates[remote_item_id] = remote_status

                status_updates = self._build_remote_reflection_status_updates(
                    local_items=items,
                    remote_status_updates=status_updates,
                )
                if status_updates:
                    content = work_stream_path.read_text(encoding="utf-8")
                    updated_content = WorkstreamParser.sync_status_annotations(content, statuses=status_updates)
                    if updated_content != content:
                        work_stream_path.write_text(updated_content, encoding="utf-8")
                op.items_successful = len(status_updates)
                errors = result.get("errors", [])
                if isinstance(errors, list):
                    op.errors.extend(str(error) for error in errors)
            op.items_failed = max(0, op.items_processed - op.items_successful)

            op.completed_at = datetime.now(timezone.utc)
            op.duration_seconds = (op.completed_at - op.started_at).total_seconds()
            self.last_operation = op

        except (LinearGraphQLAuthError, LinearGraphQLError, OSError, ValueError, TypeError) as e:
            logger.error("Failed to sync from Linear: %s", e, exc_info=True)
            op.errors.append(str(e))
            if self.config.standalone_mode:
                return
            raise
        except Exception as e:
            logger.error("Unexpected Linear read sync failure: %s", e, exc_info=True)
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
        breaker = self._connector_breaker(connector)
        timeout_seconds = self._connector_timeout_seconds(connector, direction)
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
            partition_attempt = 0
            while True:
                try:
                    partition = partitions[partition_index]
                    started_at = time.monotonic()

                    async def _run_partition_sync(partition_items: list[WorkstreamItem] = partition) -> None:
                        await asyncio.wait_for(sync_fn(partition_items), timeout=timeout_seconds)

                    try:
                        await breaker.call_async(_run_partition_sync)
                    except asyncio.TimeoutError as exc:
                        self._metrics.record_autosync_connector_operation(
                            connector=connector,
                            direction=direction,
                            result="timeout",
                            duration_seconds=max(0.0, time.monotonic() - started_at),
                        )
                        self._metrics.set_circuit_breaker(connector, breaker.state == "open")
                        raise WorkstreamAutosyncError(
                            f"{connector}/{direction} timed out after {timeout_seconds:.3f}s",
                        ) from exc
                    except CircuitOpenError as exc:
                        self._metrics.record_autosync_circuit_open(connector=connector, direction=direction)
                        self._metrics.record_autosync_connector_operation(
                            connector=connector,
                            direction=direction,
                            result="circuit_open",
                            duration_seconds=max(0.0, time.monotonic() - started_at),
                        )
                        self._metrics.set_circuit_breaker(connector, True)
                        raise WorkstreamAutosyncError(
                            f"{connector}/{direction} blocked by open connector circuit breaker",
                        ) from exc
                    except Exception:
                        self._metrics.record_autosync_connector_operation(
                            connector=connector,
                            direction=direction,
                            result="error",
                            duration_seconds=max(0.0, time.monotonic() - started_at),
                        )
                        self._metrics.set_circuit_breaker(connector, breaker.state == "open")
                        raise
                    else:
                        self._metrics.record_autosync_connector_operation(
                            connector=connector,
                            direction=direction,
                            result="success",
                            duration_seconds=max(0.0, time.monotonic() - started_at),
                        )
                        self._metrics.set_circuit_breaker(connector, breaker.state == "open")
                        break
                except Exception as exc:
                    retry_class = await self._record_failure(
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
                    if retry_class == RetryClass.PERMANENT:
                        self._clear_checkpoint(connector, direction)
                        return

                    partition_attempt += 1
                    if partition_attempt > self._rate_limit_backoff.config.max_retries:
                        logger.error(
                            "Partition sync exhausted retries for connector=%s direction=%s partition=%d: %s",
                            connector,
                            direction,
                            partition_index,
                            exc,
                        )
                        return

                    backoff_seconds = self._rate_limit_backoff.compute_wait(partition_attempt)
                    logger.warning(
                        "Retrying %s/%s partition=%d attempt=%d/%d in %.3fs after %s",
                        connector,
                        direction,
                        partition_index,
                        partition_attempt,
                        self._rate_limit_backoff.config.max_retries,
                        backoff_seconds,
                        retry_class.value,
                    )
                    await asyncio.sleep(backoff_seconds)

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
            payload = self._deserialize_artifact_payload(path.read_text(encoding="utf-8"))
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
                        retry_class=str(item.get("retry_class", RetryClass.PERMANENT.value)),
                        correlation_id=(
                            str(item["correlation_id"]) if item.get("correlation_id") is not None else None
                        ),
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
        path.write_text(self._serialize_artifact_payload(self._failure_queue.to_dict_list()), encoding="utf-8")

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

        payload = self._deserialize_artifact_payload(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Checkpoint payload must be an object.")
        return SyncCheckpoint.from_dict(payload)

    def _write_checkpoint(self) -> None:
        """Persist current checkpoint state."""
        if not self._checkpoint:
            return
        path = self._checkpoint_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._serialize_artifact_payload(self._checkpoint.to_dict()), encoding="utf-8")

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
    ) -> RetryClass:
        """Record a failure and prune stale entries."""
        digest = hashlib.sha1(f"{connector}:{direction}:{item_id}:{message}".encode()).hexdigest()[:12]
        operation_id = f"{connector}-{direction}-{item_id}-{digest}"
        retry_class = self._classify_retry(message)
        self._failure_queue.push(
            operation_id=operation_id,
            connector=connector,
            item_id=item_id,
            message=message,
            retry_class=retry_class,
            correlation_id=self._current_run_correlation_id,
        )
        self._write_failure_queue()
        self.last_error = message
        return retry_class

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
            "next_cycle_interval_seconds": self._next_cycle_interval_seconds,
            "connector_health": [probe.to_dict() for probe in self._last_connector_probe],
            "metadata": self._metadata_state(),
            "correlation_id": self._current_run_correlation_id,
            "local_orphan_report": self._local_orphan_report,
            "ignored_wl_ids": self._last_ignored_item_ids,
            "scope_filtered_wl_ids": self._last_scope_filtered_item_ids,
            "no_op_summary": self._no_op_summary,
            "trend_sample": self._last_trend_sample,
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
    THGENT_AUTOSYNC_EMERGENCY_STOP_ENABLED: Enable emergency stop checks
    THGENT_AUTOSYNC_EMERGENCY_STOP_FILE_PATH: Sentinel file path for emergency stop
    THGENT_AUTOSYNC_EMERGENCY_STOP_ENV_VAR: Env var name checked for emergency stop activation

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

    def parse_float(value: str | None, default: float) -> float:
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def parse_wl_ignore_list(raw: str | None) -> list[str]:
        if raw is None:
            return []
        value = raw.strip()
        if not value:
            return []
        if value.startswith("["):
            payload = json.loads(value)
            if not isinstance(payload, list):
                raise ValueError("THGENT_WORKSTREAM_WL_IGNORE_LIST JSON must be a list")
            candidates = [str(item).strip().upper() for item in payload if str(item).strip()]
        else:
            candidates = [token.strip().upper() for token in value.split(",") if token.strip()]
        for candidate in candidates:
            if not WL_ID_PATTERN.fullmatch(candidate):
                raise ValueError(f"Invalid WL ignore ID: {candidate}")
        return sorted(set(candidates))

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
                project = str(item.get("project", "default")).strip().lower() or "default"
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
                            project=project,
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
                        project="default",
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

    def parse_connector_health_states(raw: str | None) -> dict[str, str]:
        if not raw:
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if not isinstance(payload, dict):
            return {}
        states: dict[str, str] = {}
        for key, value in payload.items():
            states[str(key).strip().lower()] = str(value).strip().lower()
        return states

    def parse_bootstrap_mappings(raw: str | None) -> list[str]:
        if not raw:
            return []
        return [field.strip() for field in raw.split(",") if field.strip()]

    def parse_scope_tokens(raw: str | None, *, upper: bool = False) -> list[str]:
        if not raw:
            return []
        values = [token.strip() for token in raw.split(",") if token.strip()]
        if upper:
            return [value.upper() for value in values]
        return values

    def parse_capability_map(raw: str | None) -> dict[str, list[str]]:
        if not raw:
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if not isinstance(payload, dict):
            return {}
        normalized: dict[str, list[str]] = {}
        for connector, values in payload.items():
            if isinstance(values, list):
                normalized[str(connector).strip().lower()] = [str(value).strip().lower() for value in values]
        return normalized

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
    cycle_manifest_path = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_CYCLE_MANIFEST_PATH")
    cycle_metrics_path = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_CYCLE_METRICS_PATH")
    failure_queue_path = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_FAILURE_QUEUE_PATH")
    autosync_prometheus_export_path = os.getenv("THGENT_AUTOSYNC_PROMETHEUS_EXPORT_PATH")
    connector_mapping_cache_path = os.getenv("THGENT_CONNECTOR_MAPPING_CACHE_PATH")
    trend_file_path = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_TREND_PATH")
    writer_lock_path = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_LOCK_PATH")
    emergency_stop_file_path = os.getenv("THGENT_AUTOSYNC_EMERGENCY_STOP_FILE_PATH")
    incident_bundle_path = os.getenv("THGENT_WORKSTREAM_INCIDENT_BUNDLE_PATH")
    bootstrap_mapping_cache_path = os.getenv("THGENT_CONNECTOR_MAPPING_CACHE_PATH")
    emergency_stop_env_var = os.getenv("THGENT_AUTOSYNC_EMERGENCY_STOP_ENV_VAR", "THGENT_AUTOSYNC_EMERGENCY_STOP")
    maintenance_windows = parse_json_windows(os.getenv("THGENT_AUTOSYNC_MAINTENANCE_WINDOWS"))
    allowed_tags = parse_tag_taxonomy(os.getenv("THGENT_WORKSTREAM_TAG_TAXONOMY"))
    wl_ignore_list = parse_wl_ignore_list(os.getenv("THGENT_WORKSTREAM_WL_IGNORE_LIST"))
    connector_health_states = parse_connector_health_states(os.getenv("THGENT_CONNECTOR_HEALTH_STATES"))
    connector_capabilities = parse_capability_map(os.getenv("THGENT_CONNECTOR_CAPABILITIES"))
    required_connector_capabilities = parse_capability_map(os.getenv("THGENT_REQUIRED_CONNECTOR_CAPABILITIES"))
    bootstrap_required_fields = parse_bootstrap_mappings(os.getenv("THGENT_BOOTSTRAP_REQUIRED_FIELDS"))
    scope_areas = parse_scope_tokens(os.getenv("THGENT_WORKSTREAM_SYNC_SCOPE_AREAS"))
    scope_statuses = parse_scope_tokens(os.getenv("THGENT_WORKSTREAM_SYNC_SCOPE_STATUSES"), upper=True)
    scope_priorities = parse_scope_tokens(os.getenv("THGENT_WORKSTREAM_SYNC_SCOPE_PRIORITIES"), upper=True)
    scope_wl_ranges = parse_scope_tokens(os.getenv("THGENT_WORKSTREAM_SYNC_SCOPE_WL_RANGES"), upper=True)
    remote_missing_policy_raw = os.getenv("THGENT_WORKSTREAM_REMOTE_MISSING_ITEM_POLICY", "ignore").strip().lower()
    try:
        remote_missing_policy = RemoteMissingItemPolicy(remote_missing_policy_raw)
    except ValueError as exc:
        raise ValueError(f"Invalid THGENT_WORKSTREAM_REMOTE_MISSING_ITEM_POLICY: {remote_missing_policy_raw}") from exc
    metadata_last_refreshed_at_raw = os.getenv("THGENT_METADATA_LAST_REFRESHED_AT")
    metadata_last_refreshed_at = None
    if metadata_last_refreshed_at_raw:
        metadata_last_refreshed_at = datetime.fromisoformat(metadata_last_refreshed_at_raw.replace("Z", "+00:00"))
    explicit_enabled = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_ENABLED")
    repo_previously_opted_in = parse_bool(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_PREVIOUS_OPT_IN"), default=False)
    migration_phase = os.getenv("THGENT_WORKSTREAM_AUTOSYNC_MIGRATION_PHASE", "phase1-detect").strip().lower()
    enabled = (
        parse_bool(explicit_enabled)
        if explicit_enabled is not None
        else autosync_phase1_enabled(
            explicit_env=explicit_enabled,
            repo_previously_opted_in=repo_previously_opted_in,
        )
    )

    return WorkstreamAutosyncConfig(
        enabled=enabled,
        migration_phase=migration_phase,
        repo_previously_opted_in=repo_previously_opted_in,
        cycle_interval_seconds=parse_int(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_INTERVAL", "300"), default=300),
        checkpoint_ttl_seconds=parse_int(
            os.getenv("THGENT_WORKSTREAM_AUTOSYNC_TTL_SECONDS", str(3600)),
            default=3600,
        ),
        conflict_ttl_seconds=parse_int(
            os.getenv("THGENT_WORKSTREAM_AUTOSYNC_CONFLICT_TTL_SECONDS", "1800"),
            default=1800,
        ),
        github_enabled=parse_bool(os.getenv("THGENT_GITHUB_ENABLED")),
        github_owner=os.getenv("THGENT_GITHUB_OWNER", ""),
        github_project_number=parse_int(os.getenv("THGENT_GITHUB_PROJECT_NUMBER", "0"), default=0),
        github_direction=github_dir,
        github_sandbox_mode=parse_bool(os.getenv("THGENT_GITHUB_SANDBOX_MODE")),
        github_sandbox_project_number=parse_int(os.getenv("THGENT_GITHUB_SANDBOX_PROJECT_NUMBER", "0"), default=0),
        linear_enabled=parse_bool(os.getenv("THGENT_LINEAR_ENABLED")),
        linear_api_key=os.getenv("THGENT_LINEAR_API_KEY", ""),
        linear_team_key=os.getenv("THGENT_LINEAR_TEAM_KEY", ""),
        linear_direction=linear_dir,
        work_stream_path=Path(work_stream_path) if work_stream_path else None,
        status_file_path=Path(status_file_path) if status_file_path else None,
        checkpoint_file_path=Path(checkpoint_file_path) if checkpoint_file_path else None,
        cycle_manifest_path=Path(cycle_manifest_path) if cycle_manifest_path else None,
        cycle_metrics_path=Path(cycle_metrics_path) if cycle_metrics_path else None,
        maintenance_windows=maintenance_windows,
        max_partition_size=parse_int(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_MAX_PARTITION_SIZE", "200"), default=200),
        allowed_tags=allowed_tags,
        adaptive_interval_enabled=parse_bool(os.getenv("THGENT_WORKSTREAM_ADAPTIVE_INTERVAL_ENABLED")),
        adaptive_interval_min_seconds=parse_int(
            os.getenv("THGENT_WORKSTREAM_ADAPTIVE_INTERVAL_MIN_SECONDS", "30"),
            default=30,
        ),
        adaptive_interval_max_seconds=parse_int(
            os.getenv("THGENT_WORKSTREAM_ADAPTIVE_INTERVAL_MAX_SECONDS", "900"),
            default=900,
        ),
        connector_health_states=connector_health_states,
        incident_bundle_path=Path(incident_bundle_path) if incident_bundle_path else None,
        metadata_ttl_seconds=parse_int(os.getenv("THGENT_METADATA_TTL_SECONDS", "3600"), default=3600),
        metadata_last_refreshed_at=metadata_last_refreshed_at,
        bootstrap_connector=os.getenv("THGENT_BOOTSTRAP_CONNECTOR", "github"),
        bootstrap_required_fields=bootstrap_required_fields,
        bootstrap_mapping_cache_path=Path(bootstrap_mapping_cache_path) if bootstrap_mapping_cache_path else None,
        project_id=os.getenv("THGENT_WORKSTREAM_PROJECT_ID", "default"),
        require_actor_identity=parse_bool(os.getenv("THGENT_AUTOSYNC_REQUIRE_ACTOR_IDENTITY")),
        actor_id=os.getenv("THGENT_AUTOSYNC_ACTOR_ID", ""),
        actor_signature=os.getenv("THGENT_AUTOSYNC_ACTOR_SIGNATURE", ""),
        actor_signing_key=os.getenv("THGENT_AUTOSYNC_ACTOR_SIGNING_KEY", ""),
        connector_capabilities=connector_capabilities,
        required_connector_capabilities=required_connector_capabilities,
        payload_checksum_enforced=parse_bool(os.getenv("THGENT_AUTOSYNC_PAYLOAD_CHECKSUM_ENFORCED")),
        expected_payload_checksum=os.getenv("THGENT_AUTOSYNC_EXPECTED_PAYLOAD_CHECKSUM", ""),
        failure_queue_path=Path(failure_queue_path) if failure_queue_path else None,
        connector_mapping_cache_path=Path(connector_mapping_cache_path) if connector_mapping_cache_path else None,
        scope_areas=scope_areas,
        scope_statuses=scope_statuses,
        scope_priorities=scope_priorities,
        scope_wl_ranges=scope_wl_ranges,
        remote_missing_item_policy=remote_missing_policy,
        autosync_prometheus_export_path=(
            Path(autosync_prometheus_export_path) if autosync_prometheus_export_path else None
        ),
        wl_ignore_list=wl_ignore_list,
        github_write_timeout_seconds=parse_float(os.getenv("THGENT_GITHUB_WRITE_TIMEOUT_SECONDS"), default=30.0),
        github_read_timeout_seconds=parse_float(os.getenv("THGENT_GITHUB_READ_TIMEOUT_SECONDS"), default=30.0),
        linear_write_timeout_seconds=parse_float(os.getenv("THGENT_LINEAR_WRITE_TIMEOUT_SECONDS"), default=30.0),
        linear_read_timeout_seconds=parse_float(os.getenv("THGENT_LINEAR_READ_TIMEOUT_SECONDS"), default=30.0),
        connector_circuit_breaker_failure_threshold=parse_int(
            os.getenv("THGENT_AUTOSYNC_CONNECTOR_BREAKER_FAILURE_THRESHOLD"),
            default=3,
        ),
        connector_circuit_breaker_success_threshold=parse_int(
            os.getenv("THGENT_AUTOSYNC_CONNECTOR_BREAKER_SUCCESS_THRESHOLD"),
            default=1,
        ),
        connector_circuit_breaker_timeout_seconds=parse_float(
            os.getenv("THGENT_AUTOSYNC_CONNECTOR_BREAKER_TIMEOUT_SECONDS"),
            default=60.0,
        ),
        failure_queue_retention_seconds=parse_int(
            os.getenv("THGENT_WORKSTREAM_AUTOSYNC_FAILURE_QUEUE_TTL_SECONDS", str(60 * 60 * 24)),
            default=60 * 60 * 24,
        ),
        simulation_mode=parse_bool(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_SIMULATION_MODE")),
        snapshot_retention_count=parse_int(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_SNAPSHOT_RETENTION", "20"), 20),
        trend_file_path=Path(trend_file_path) if trend_file_path else None,
        artifact_encryption_enabled=parse_bool(os.getenv("THGENT_AUTOSYNC_ARTIFACT_ENCRYPTION")),
        artifact_encryption_key=os.getenv("THGENT_AUTOSYNC_ARTIFACT_KEY", ""),
        strict_tag_validation=parse_bool(os.getenv("THGENT_WORKSTREAM_STRICT_TAG_VALIDATION")),
        strict_title_validation=parse_bool(os.getenv("THGENT_WORKSTREAM_STRICT_TITLE_VALIDATION")),
        emergency_stop_enabled=parse_bool(os.getenv("THGENT_AUTOSYNC_EMERGENCY_STOP_ENABLED"), default=True),
        emergency_stop_file_path=Path(emergency_stop_file_path) if emergency_stop_file_path else None,
        emergency_stop_env_var=emergency_stop_env_var,
        writer_lock_enabled=parse_bool(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_LOCK_ENABLED"), default=True),
        writer_lock_path=Path(writer_lock_path) if writer_lock_path else None,
        rate_limit_max_retries=parse_int(os.getenv("THGENT_AUTOSYNC_RATE_LIMIT_MAX_RETRIES"), default=2),
        rate_limit_initial_wait=parse_float(os.getenv("THGENT_AUTOSYNC_RATE_LIMIT_INITIAL_WAIT"), default=1.0),
        rate_limit_max_wait=parse_float(os.getenv("THGENT_AUTOSYNC_RATE_LIMIT_MAX_WAIT"), default=16.0),
        rate_limit_multiplier=parse_float(os.getenv("THGENT_AUTOSYNC_RATE_LIMIT_MULTIPLIER"), default=2.0),
        standalone_mode=parse_bool(os.getenv("THGENT_AUTOSYNC_STANDALONE_MODE"), default=True),
        shadow_mode=parse_bool(os.getenv("THGENT_WORKSTREAM_AUTOSYNC_SHADOW_MODE")),
    )
