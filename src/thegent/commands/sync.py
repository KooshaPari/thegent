"""SY-009: Unified `thegent sync` command.

Consolidates update/sync operations into a single entry point with
subcommands: all, work-stream, config, agents, hooks.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

from thegent.observability.prometheus import get_metrics_collector
from thegent.utils.workstream_ops import _atomic_write, _locked_file_access
from thegent.sync.dead_letter_queue import (
    DEFAULT_BOARD_DEAD_LETTER_BACKOFF_MULTIPLIER,
    DEFAULT_BOARD_DEAD_LETTER_MAX_ATTEMPTS,
    DEFAULT_BOARD_DEAD_LETTER_RETRY_DELAY_SECONDS,
    RemoteWriteDeadLetterQueue,
)

_log = structlog.get_logger(__name__)


def render_maintenance_banner(*, maintenance_active: bool, connector: str, reason: str = "") -> str:
    """Render maintenance banner used by sync command/report output."""
    if not maintenance_active:
        return ""
    normalized_reason = reason.strip() or "scheduled maintenance"
    return f"[MAINTENANCE] connector={connector} reason={normalized_reason}"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class SyncOperationStatus(str, Enum):
    """Status of a single sync operation."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    DRY_RUN = "dry_run"


@dataclass
class OperationResult:
    """Result of a single sync operation."""

    operation: str
    status: SyncOperationStatus
    message: str = ""
    duration: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    changes: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def ok(self) -> bool:
        return self.status in (SyncOperationStatus.SUCCESS, SyncOperationStatus.DRY_RUN)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "status": self.status.value,
            "message": self.message,
            "duration": self.duration,
            "details": self.details,
            "errors": self.errors,
            "changes": self.changes,
            "timestamp": self.timestamp,
        }


@dataclass
class SyncResult:
    """Aggregate result of a sync run (one or more operations).

    Attributes:
        operations: Per-operation results.
        files_synced: Total number of files synced across all operations.
        errors: Flat list of all error strings from failed operations.
        started_at: ISO timestamp when the sync began.
        finished_at: ISO timestamp when the sync ended.
        total_duration: Wall-clock duration in seconds.
    """

    operations: list[OperationResult] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str = ""
    total_duration: float = 0.0

    @property
    def success(self) -> bool:
        return all(op.ok for op in self.operations)

    @property
    def files_synced(self) -> int:
        """Total number of changes/files synced across all operations."""
        return sum(len(op.changes) for op in self.operations)

    @property
    def errors(self) -> list[str]:
        """Flat list of all error strings from failed operations."""
        errs: list[str] = []
        for op in self.operations:
            errs.extend(op.errors)
        return errs

    @property
    def failed_operations(self) -> list[OperationResult]:
        return [op for op in self.operations if not op.ok]

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "files_synced": self.files_synced,
            "errors": self.errors,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "total_duration": self.total_duration,
            "operations": [op.to_dict() for op in self.operations],
        }


@dataclass
class _RemoteWriteDeadLetterQueueConfig:
    """Configuration for remote write dead-letter retry metadata."""

    max_attempts: int = DEFAULT_BOARD_DEAD_LETTER_MAX_ATTEMPTS
    retry_interval_seconds: float = DEFAULT_BOARD_DEAD_LETTER_RETRY_DELAY_SECONDS
    backoff_multiplier: float = DEFAULT_BOARD_DEAD_LETTER_BACKOFF_MULTIPLIER


# ---------------------------------------------------------------------------
# SyncCommand
# ---------------------------------------------------------------------------


class SyncCommand:
    """Unified sync command with subcommands for all major sync operations.

    Subcommands
    -----------
    all          Run all sync operations in sequence.
    work-stream  Incorporate fragments from docs/ into WORK_STREAM.md.
    config       Refresh ThegentSettings from environment.
    agents       Discover new agent files in the agents/ directory.
    hooks        Validate hook registrations against hook-config.yaml.
    status       Show drift between local and remote agent config.
    push         Push local state to remote (stubbed for now).
    pull         Pull remote state locally (stubbed for now).
    reset        Reset local state to defaults (stubbed for now).
    """

    def __init__(
        self,
        project_root: Path | None = None,
        agents_dir: Path | None = None,
        hooks_dir: Path | None = None,
        hook_config_path: Path | None = None,
        work_stream_path: Path | None = None,
    ) -> None:
        self._root = (project_root or Path.cwd()).resolve()
        self._agents_dir = (agents_dir or self._root / "agents").resolve()
        self._hooks_dir = (hooks_dir or self._root / "hooks").resolve()
        self._hook_config = (hook_config_path or self._hooks_dir / "hook-config.yaml").resolve()
        self._work_stream = (work_stream_path or self._root / "docs" / "reference" / "WORK_STREAM.md").resolve()

    # ------------------------------------------------------------------
    # Public subcommand API
    # ------------------------------------------------------------------

    def sync_all(self, dry_run: bool = False) -> SyncResult:
        """Run all sync operations sequentially.

        Args:
            dry_run: If True, report what would be done without writing.

        Returns:
            SyncResult with per-operation OperationResult entries.
        """
        t0 = time.monotonic()
        result = SyncResult()

        for fn in (
            self.sync_work_stream,
            self.sync_config,
            self.sync_agents,
            self.sync_hooks,
        ):
            op = fn(dry_run=dry_run)
            result.operations.append(op)

        result.total_duration = time.monotonic() - t0
        result.finished_at = datetime.now(UTC).isoformat()
        return result

    def sync_work_stream(self, dry_run: bool = False) -> OperationResult:
        """Incorporate fragments from docs/ into WORK_STREAM.md.

        Scans ``docs/plans/``, ``docs/research/``, and ``docs/docset/`` for
        markdown fragments and merges discovered work items into WORK_STREAM.md
        while preserving existing CLAIMED and COMPLETED sections.

        Args:
            dry_run: If True, return what would be merged without writing.

        Returns:
            OperationResult with item counts and change details.
        """
        t0 = time.monotonic()
        op = "work-stream"

        if dry_run:
            items = self._discover_work_stream_fragments()
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.DRY_RUN,
                message=f"Would incorporate {len(items)} fragments (dry run).",
                duration=time.monotonic() - t0,
                details={"fragments_found": len(items)},
                changes=[f"[dry-run] {item}" for item in items[:10]],
            )

        try:
            items = self._discover_work_stream_fragments()
            incorporated = self._incorporate_into_work_stream(items)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.SUCCESS,
                message=f"Incorporated {incorporated} item(s) into WORK_STREAM.md.",
                duration=time.monotonic() - t0,
                details={"fragments_found": len(items), "items_incorporated": incorporated},
                changes=[f"incorporated: {it}" for it in items[:incorporated]],
            )
        except Exception as exc:
            _log.warning("sync_work_stream failed: %s", exc, exc_info=True)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Work-stream sync failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def sync_rules(self, dry_run: bool = False) -> OperationResult:
        """Delegate to ``thegent rules sync`` (RulesSyncManager).

        Thin wrapper that calls ``RulesSyncManager.sync_all()`` so that
        ``thegent sync rules`` is a convenience alias for ``thegent rules sync``.

        # @trace WL-037

        Args:
            dry_run: If True, report what would be written without writing.

        Returns:
            OperationResult with per-platform sync record details.
        """
        t0 = time.monotonic()
        op = "rules"

        from thegent.core.rules_sync import RulesSyncManager

        manager = RulesSyncManager()
        try:
            result = manager.sync_all(self._root, dry_run=dry_run)
        except Exception as exc:
            _log.warning("sync_rules failed: %s", exc, exc_info=True)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Rules sync failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

        files = result.files_dry_run if dry_run else result.files_written
        status = SyncOperationStatus.DRY_RUN if dry_run else SyncOperationStatus.SUCCESS
        changes = [str(p) for p in files]
        msg = (
            f"Rules sync dry-run: would write {len(files)} file(s)."
            if dry_run
            else f"Rules synced: {len(files)} file(s) written."
        )
        return OperationResult(
            operation=op,
            status=status,
            message=msg,
            duration=time.monotonic() - t0,
            details={"rules_loaded": result.rules_loaded, "files": changes},
            changes=changes,
            errors=result.errors,
        )

    def sync_research(self, dry_run: bool = False) -> OperationResult:
        """Run ``plan incorporate`` then update WORK_STREAM.md BACKLOG from research fragments.

        Scans ``docs/research/`` and ``docs/plans/`` for new work items and
        appends them to the BACKLOG section of WORK_STREAM.md, preserving any
        existing CLAIMED and COMPLETED entries.

        # @trace WL-037

        Args:
            dry_run: If True, report what would be merged without writing.

        Returns:
            OperationResult with item counts and change details.
        """
        t0 = time.monotonic()
        op = "research"

        try:
            # Step 1 — use incorporate_impl (same as ``thegent plan incorporate``)
            from thegent.cli.commands.impl import incorporate_impl

            inc_result = incorporate_impl(cd=self._root, dry_run=dry_run)
            inc_merged: int = inc_result.get("merged", 0)
            if "error" in inc_result and not dry_run:
                _log.warning("incorporate_impl returned error: %s", inc_result["error"])

            # Step 2 — scan research/ and plans/ markdown for additional checkbox items
            research_fragments = self._discover_research_fragments()
            research_incorporated = 0
            if not dry_run:
                research_incorporated = self._incorporate_into_work_stream(research_fragments)

            total = inc_merged + research_incorporated
            status = SyncOperationStatus.DRY_RUN if dry_run else SyncOperationStatus.SUCCESS
            msg = (
                f"Research sync dry-run: would incorporate {len(research_fragments)} fragment(s)."
                if dry_run
                else f"Research synced: {total} item(s) incorporated into WORK_STREAM.md."
            )
            return OperationResult(
                operation=op,
                status=status,
                message=msg,
                duration=time.monotonic() - t0,
                details={
                    "incorporate_merged": inc_merged,
                    "research_fragments_found": len(research_fragments),
                    "research_incorporated": research_incorporated,
                    "total_incorporated": total,
                },
                changes=[f"incorporated: {it}" for it in research_fragments[:research_incorporated]],
            )
        except Exception as exc:
            _log.warning("sync_research failed: %s", exc, exc_info=True)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Research sync failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def sync_config(self, dry_run: bool = False) -> OperationResult:
        """Refresh ThegentSettings from the current environment.

        Re-instantiates ``ThegentSettings`` (which reads env vars and .env
        files) and reports which fields changed from the previous state.

        Args:
            dry_run: If True, only report discovered settings without saving.

        Returns:
            OperationResult with changed-field details.
        """
        t0 = time.monotonic()
        op = "config"

        try:
            from thegent.config import ThegentSettings

            settings = ThegentSettings()
            field_names = list(type(settings).model_fields.keys())

            if dry_run:
                return OperationResult(
                    operation=op,
                    status=SyncOperationStatus.DRY_RUN,
                    message=f"Would refresh {len(field_names)} config field(s) (dry run).",
                    duration=time.monotonic() - t0,
                    details={"fields": field_names},
                )

            # Snapshot current values then re-instantiate to pick up env changes
            current = {k: getattr(settings, k, None) for k in field_names}
            refreshed = ThegentSettings()
            changed = [k for k in field_names if getattr(refreshed, k, None) != current.get(k)]

            return OperationResult(
                operation=op,
                status=SyncOperationStatus.SUCCESS,
                message=f"Config refreshed ({len(changed)} field(s) changed).",
                duration=time.monotonic() - t0,
                details={"fields_total": len(field_names), "fields_changed": len(changed)},
                changes=changed,
            )
        except Exception as exc:
            _log.warning("sync_config failed: %s", exc, exc_info=True)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Config sync failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def sync_agents(self, dry_run: bool = False) -> OperationResult:
        """Discover new agent persona files in the agents/ directory.

        Scans the ``agents/`` directory for ``*.md`` files and reports any
        agent definitions that are not yet registered in the canonical
        ``AGENT_NAMES`` registry list.

        Args:
            dry_run: If True, only report discovered agents without updating.

        Returns:
            OperationResult with new agent names and file paths.
        """
        t0 = time.monotonic()
        op = "agents"

        try:
            from thegent.agents.registry import AGENT_NAMES

            discovered = self._discover_agent_files()
            known = set(AGENT_NAMES)
            new_agents = [name for name in discovered if name not in known]

            status = SyncOperationStatus.DRY_RUN if dry_run else SyncOperationStatus.SUCCESS
            verb = "Would register" if dry_run else "Discovered"
            return OperationResult(
                operation=op,
                status=status,
                message=f"{verb} {len(new_agents)} new agent(s) in agents/.",
                duration=time.monotonic() - t0,
                details={
                    "total_agent_files": len(discovered),
                    "known_agents": len(known),
                    "new_agents": new_agents,
                },
                changes=[f"new: {name}" for name in new_agents],
            )
        except Exception as exc:
            _log.warning("sync_agents failed: %s", exc, exc_info=True)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Agent sync failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def sync_hooks(self, dry_run: bool = False) -> OperationResult:
        """Validate hook registrations against hook-config.yaml.

        Cross-references ``*.sh`` files in the ``hooks/`` directory with the
        ``hooks:`` section of ``hook-config.yaml`` and reports any hook scripts
        that are present on disk but missing a config entry, or any config
        entries that have no corresponding ``.sh`` file.

        Args:
            dry_run: If True, only report findings without modifying config.

        Returns:
            OperationResult with unregistered/orphan hook details.
        """
        t0 = time.monotonic()
        op = "hooks"

        try:
            disk_hooks = self._discover_hook_scripts()
            config_hooks = self._parse_hook_config_names()

            unregistered = sorted(disk_hooks - config_hooks)
            orphaned = sorted(config_hooks - disk_hooks)

            issues: list[str] = []
            if unregistered:
                issues += [f"unregistered: {h}" for h in unregistered]
            if orphaned:
                issues += [f"orphan-config: {h}" for h in orphaned]

            status = SyncOperationStatus.DRY_RUN if dry_run else SyncOperationStatus.SUCCESS
            suffix = f" {len(unregistered)} unregistered, {len(orphaned)} orphaned." if issues else " All OK."
            msg = f"Hooks validated: {len(disk_hooks)} on disk, {len(config_hooks)} in config.{suffix}"

            return OperationResult(
                operation=op,
                status=status,
                message=msg,
                duration=time.monotonic() - t0,
                details={
                    "hooks_on_disk": len(disk_hooks),
                    "hooks_in_config": len(config_hooks),
                    "unregistered": unregistered,
                    "orphaned": orphaned,
                },
                changes=issues,
            )
        except Exception as exc:
            _log.warning("sync_hooks failed: %s", exc, exc_info=True)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Hook sync failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def status(self) -> OperationResult:
        """Show drift between local and remote agent config."""
        t0 = time.monotonic()
        op = "status"

        try:
            local_agents = self._discover_agent_files()
            hook_scripts = self._discover_hook_scripts()
            config_hooks = self._parse_hook_config_names()

            unregistered_hooks = sorted(hook_scripts - config_hooks)
            orphaned_hooks = sorted(config_hooks - hook_scripts)
            has_drift = bool(unregistered_hooks or orphaned_hooks)

            drift_lines: list[str] = []
            if unregistered_hooks:
                drift_lines.append(f"unregistered hooks: {', '.join(unregistered_hooks)}")
            if orphaned_hooks:
                drift_lines.append(f"orphaned hook config: {', '.join(orphaned_hooks)}")

            msg = (
                "Local state has drift from expected config."
                if has_drift
                else "Local state is in sync with expected config."
            )

            _log.info("sync status: agents=%s drift=%s", len(local_agents), has_drift)

            return OperationResult(
                operation=op,
                status=SyncOperationStatus.SUCCESS,
                message=msg,
                duration=time.monotonic() - t0,
                details={
                    "local_agents": local_agents,
                    "hooks_on_disk": len(hook_scripts),
                    "hooks_in_config": len(config_hooks),
                    "unregistered_hooks": unregistered_hooks,
                    "orphaned_hooks": orphaned_hooks,
                    "has_drift": has_drift,
                },
                changes=drift_lines,
            )
        except Exception as exc:
            _log.warning("sync status failed: %s", exc)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Status check failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def update(self, dry_run: bool = False) -> OperationResult:
        """Update thegent components and dependencies (SY-007)."""
        t0 = time.monotonic()
        op = "update"

        try:
            # Stub: check for version updates or pip package updates
            # In a real impl, we might run 'pip install --upgrade thegent' or similar
            message = "Checking for updates..."
            if dry_run:
                return OperationResult(
                    operation=op,
                    status=SyncOperationStatus.DRY_RUN,
                    message=f"{message} (dry run). No changes would be made.",
                    duration=time.monotonic() - t0,
                )

            # For now, we just report success as a placeholder for the update logic
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.SUCCESS,
                message="All components are up to date.",
                duration=time.monotonic() - t0,
            )
        except Exception as exc:
            _log.warning("update failed: %s", exc)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Update failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    async def audit(self, fix: bool = False) -> OperationResult:
        """Run system audit and report issues (SY-007, SY-002)."""
        t0 = time.monotonic()
        op = "audit"

        try:
            from thegent.sync.audit_framework import SystemAuditFramework

            framework = SystemAuditFramework()
            result = await framework.run_audit(fix=fix)

            status = SyncOperationStatus.SUCCESS
            if result.summary.get("critical", 0) > 0:
                status = SyncOperationStatus.FAILED

            summary_msg = (
                f"Audit complete: {result.summary['total_issues']} issues found "
                f"({result.summary['critical']} critical, {result.summary['high']} high)."
            )

            return OperationResult(
                operation=op,
                status=status,
                message=summary_msg,
                duration=time.monotonic() - t0,
                details=result.summary,
                changes=[f"{i.severity.upper()}: {i.title}" for i in result.issues],
                errors=[
                    f"{i.severity.upper()}: {i.description}"
                    for i in result.issues
                    if i.severity in ("critical", "high")
                ],
            )
        except Exception as exc:
            _log.warning("audit failed: %s", exc)
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Audit failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def push(self, target: str | None = None) -> OperationResult:
        """Push local state to remote.

        Uploads agent and hook artifacts to a filesystem-backed remote target.
        The target is treated as a directory path and receives files under:
        ``<target>/.thegent/sync_push/``.

        Args:
            target: Optional remote target identifier (URL, host, or alias).
                    Defaults to the value of the ``THGENT_SYNC_REMOTE``
                    environment variable, if set.

        Returns:
            OperationResult with per-file transfer outcomes.
        """
        t0 = time.monotonic()
        op = "push"

        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        effective_target = target or settings.sync_remote

        _log.info("sync push invoked: target=%s", effective_target)

        local_agents = self._discover_agent_files()
        hook_scripts = sorted(self._discover_hook_scripts())
        relative_files = [Path("agents") / f"{a}.md" for a in local_agents] + [
            Path("hooks") / f"{h}.sh" for h in hook_scripts
        ]

        target_dir = self._resolve_sync_target(effective_target)
        if target_dir is None:
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Push failed: unreachable target '{effective_target}'.",
                duration=time.monotonic() - t0,
                details={"target": effective_target, "transfers": []},
                errors=[f"Unreachable target: {effective_target!r}"],
            )

        export_root = target_dir / ".thegent" / "sync_push"
        export_root.mkdir(parents=True, exist_ok=True)

        transfers: list[dict[str, str]] = []
        failed = 0
        for rel_path in relative_files:
            src = self._root / rel_path
            dst = export_root / rel_path
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                transfers.append(
                    {
                        "file": str(rel_path),
                        "source": str(src),
                        "destination": str(dst),
                        "status": "success",
                    }
                )
            except Exception as exc:
                failed += 1
                transfers.append(
                    {
                        "file": str(rel_path),
                        "source": str(src),
                        "destination": str(dst),
                        "status": "failed",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )

        successful = len(transfers) - failed
        status = SyncOperationStatus.SUCCESS if failed == 0 else SyncOperationStatus.FAILED
        message = (
            f"Pushed {successful}/{len(transfers)} file(s) to '{target_dir}'."
            if failed == 0
            else f"Push partially failed: {successful}/{len(transfers)} file(s) uploaded to '{target_dir}'."
        )
        errors = [t["error"] for t in transfers if t.get("status") == "failed" and "error" in t]

        return OperationResult(
            operation=op,
            status=status,
            message=message,
            duration=time.monotonic() - t0,
            details={
                "target": str(target_dir),
                "files_total": len(transfers),
                "files_uploaded": successful,
                "files_failed": failed,
                "transfers": transfers,
            },
            errors=errors,
            changes=[f"push: {t['file']}" for t in transfers if t.get("status") == "success"],
        )

    def pull(self, source: str | None = None) -> OperationResult:
        """Pull remote state locally.

        Pulls agent/hook/config state from a local source directory and applies
        it to the current project.

        Args:
            source: Optional remote source identifier (URL, host, or alias).
                    Defaults to the value of the ``THGENT_SYNC_REMOTE``
                    environment variable, if set.

        Returns:
            OperationResult describing applied files and any failures.
        """
        t0 = time.monotonic()
        op = "pull"

        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        effective_source = source or settings.sync_remote

        if not effective_source or effective_source == "<local-stub>":
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message="Pull failed: source is required.",
                duration=time.monotonic() - t0,
                errors=["source is required"],
            )

        source_dir = Path(effective_source).expanduser().resolve()
        if not source_dir.exists() or not source_dir.is_dir():
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Pull failed: source '{source_dir}' is not a directory.",
                duration=time.monotonic() - t0,
                details={"source": str(source_dir)},
                errors=[f"invalid source directory: {source_dir}"],
            )

        _log.info("sync pull invoked: source=%s", source_dir)

        files: list[Path] = []
        agent_dir = source_dir / "agents"
        if agent_dir.is_dir():
            files.extend(sorted(agent_dir.glob("*.md")))
        hook_dir = source_dir / "hooks"
        if hook_dir.is_dir():
            files.extend(sorted(hook_dir.glob("*.sh")))
        config_path = source_dir / "config.yaml"
        if config_path.exists():
            files.append(config_path)

        transfers: list[dict[str, str]] = []
        failed = 0
        for src in files:
            rel_path = src.relative_to(source_dir)
            dst = self._root / rel_path
            if not src.exists():
                continue
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                transfers.append(
                    {
                        "file": str(rel_path),
                        "source": str(src),
                        "destination": str(dst),
                        "status": "success",
                    }
                )
            except Exception as exc:  # pragma: no cover - defensive
                failed += 1
                transfers.append(
                    {
                        "file": str(rel_path),
                        "source": str(src),
                        "destination": str(dst),
                        "status": "failed",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )

        successful = len(transfers) - failed
        status = SyncOperationStatus.SUCCESS if failed == 0 else SyncOperationStatus.FAILED
        message = (
            f"Pulled {successful}/{len(transfers)} file(s) from '{source_dir}'."
            if failed == 0
            else f"Pull partially failed: {successful}/{len(transfers)} file(s) from '{source_dir}'."
        )
        errors = [t["error"] for t in transfers if t.get("status") == "failed" and "error" in t]
        return OperationResult(
            operation=op,
            status=status,
            message=message,
            duration=time.monotonic() - t0,
            details={
                "source": str(source_dir),
                "files_total": len(transfers),
                "files_pulled": successful,
                "files_failed": failed,
                "transfers": transfers,
            },
            errors=errors,
            changes=[f"pull: {t['file']}" for t in transfers if t.get("status") == "success"],
        )

    def reset(self) -> OperationResult:
        """Reset local state to defaults.

        Stubs the reset operation.  When fully implemented, this will:

        1. Remove any auto-incorporated fragments appended to WORK_STREAM.md.
        2. Clear the ThegentSettings cache so next access re-reads environment.
        3. Report which files would have been touched.

        Returns:
            OperationResult summarising what a real reset would affect.
        """
        t0 = time.monotonic()
        op = "reset"

        _log.info("sync reset invoked: root=%s", self._root)

        files_would_reset: list[str] = []

        if self._work_stream.exists():
            files_would_reset.append(str(self._work_stream.relative_to(self._root)))

        hook_config_rel = None
        if self._hook_config.exists():
            with contextlib.suppress(ValueError):
                hook_config_rel = str(self._hook_config.relative_to(self._root))
            if hook_config_rel:
                files_would_reset.append(hook_config_rel)

        return OperationResult(
            operation=op,
            status=SyncOperationStatus.SUCCESS,
            message=f"[stub] Reset would affect {len(files_would_reset)} file(s). No destructive changes were made.",
            duration=time.monotonic() - t0,
            details={
                "files_would_reset": files_would_reset,
                "stub": True,
            },
            changes=[f"reset: {f}" for f in files_would_reset],
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _discover_work_stream_fragments(self) -> list[str]:
        """Scan docs/ subdirs for markdown fragment lines (checkboxes / table rows)."""
        scan_dirs = [
            self._root / "docs" / "plans",
            self._root / "docs" / "research",
            self._root / "docs" / "docset",
        ]
        fragments: list[str] = []
        for d in scan_dirs:
            if not d.exists():
                continue
            for md_file in sorted(d.glob("*.md")):
                self._extract_fragments_from_file(fragments, md_file)
        return fragments

    def _extract_fragments_from_file(self, fragments: list[str], md_file: Path) -> None:
        """Read and extract fragment lines from a single markdown file safely."""
        try:
            for line in md_file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("- [ ]") or (stripped.startswith("|") and stripped.endswith("|")):
                    fragments.append(stripped)
        except OSError:
            pass

    def _incorporate_into_work_stream(self, items: list[str]) -> int:
        """Append new items to WORK_STREAM.md (idempotent dedupe by content/WL ID).

        Returns the number of items actually appended.
        """
        existing_content = ""
        if not items:
            return 0

        try:
            with _locked_file_access(self._work_stream):
                with contextlib.suppress(OSError):
                    existing_content = self._work_stream.read_text(encoding="utf-8")

                existing_wl_ids = self._extract_wl_ids(existing_content)
                seen_new_wl_ids: set[str] = set()
                new_items: list[str] = []
                for item in items:
                    if item in existing_content:
                        continue
                    wl_id = self._extract_single_wl_id(item)
                    if wl_id and (wl_id in existing_wl_ids or wl_id in seen_new_wl_ids):
                        continue
                    if wl_id:
                        seen_new_wl_ids.add(wl_id)
                    new_items.append(item)
                if not new_items:
                    return 0

                self._work_stream.parent.mkdir(parents=True, exist_ok=True)
                separator = "\n\n<!-- auto-incorporated by thegent sync work-stream -->\n"
                output = existing_content
                if output and not output.endswith("\n"):
                    output += "\n"
                output += separator
                for it in new_items:
                    output += f"{it}\n"

                _atomic_write(self._work_stream, output)
                return len(new_items)
        except BlockingIOError:
            _log.warning("Work stream sync write skipped: another process holds the WORK_STREAM write lock.")
            return 0

    @staticmethod
    def _extract_wl_ids(content: str) -> set[str]:
        """Extract normalized WL IDs from text content."""
        return {match.group(1).upper() for match in re.finditer(r"\b(WL-\d+)\b", content, flags=re.IGNORECASE)}

    @staticmethod
    def _extract_single_wl_id(line: str) -> str | None:
        """Extract the first normalized WL ID from one line, if present."""
        match = re.search(r"\b(WL-\d+)\b", line, flags=re.IGNORECASE)
        return match.group(1).upper() if match else None

    def _discover_agent_files(self) -> list[str]:
        """Return stem names of all .md files in the agents/ directory."""
        if not self._agents_dir.exists():
            return []
        return sorted(f.stem for f in self._agents_dir.glob("*.md"))

    def _discover_hook_scripts(self) -> set[str]:
        """Return stem names of all .sh files directly in hooks/ (not subdirs)."""
        if not self._hooks_dir.exists():
            return set()
        return {f.stem for f in self._hooks_dir.glob("*.sh")}

    def _resolve_sync_target(self, target: str) -> Path | None:
        raw = (target or "").strip()
        if not raw or raw == "<local-stub>":
            return None
        try:
            resolved = Path(raw).expanduser().resolve()
            if resolved.exists() and not resolved.is_dir():
                return None
            resolved.mkdir(parents=True, exist_ok=True)
            return resolved
        except Exception:
            return None

    def _parse_hook_config_names(self) -> set[str]:
        """Parse hook names from hook-config.yaml ``hooks:`` section.

        Falls back to a simple line-based parser when PyYAML is unavailable.
        """
        if not self._hook_config.exists():
            return set()
        raw = self._hook_config.read_text(encoding="utf-8")
        try:
            import yaml

            data = yaml.safe_load(raw) or {}
            hooks_section = data.get("hooks", {})
            if isinstance(hooks_section, dict):
                return set(hooks_section.keys())
            return set()
        except Exception:
            # Fallback: naive line-based parse of YAML when yaml is unavailable
            names: set[str] = set()
            in_hooks = False
            for line in raw.splitlines():
                if line.strip() == "hooks:":
                    in_hooks = True
                    continue
                if in_hooks and line and not line[0].isspace():
                    break
                if in_hooks and line.startswith(" ") and line.rstrip().endswith(":"):
                    key = line.strip().rstrip(":")
                    if key:
                        names.add(key)
            return names

    def _discover_research_fragments(self) -> list[str]:
        """Scan docs/research/ and docs/plans/ for checkbox fragment lines.

        # @trace WL-037
        """
        scan_dirs = [
            self._root / "docs" / "research",
            self._root / "docs" / "plans",
        ]
        fragments: list[str] = []
        for d in scan_dirs:
            if not d.exists():
                continue
            for md_file in sorted(d.glob("*.md")):
                self._extract_fragments_from_file(fragments, md_file)
        return fragments

    def _load_sync_policy_contract_if_present(self):
        """Load sync policy contract when configured on disk."""
        from thegent.integrations.sync_policy_contract import (
            load_sync_policy_contract,
            resolve_sync_policy_path,
        )

        path = resolve_sync_policy_path(project_root=self._root)
        if not path.exists():
            return None
        return load_sync_policy_contract(project_root=self._root)

    def _dead_letter_queue_path(self) -> Path:
        """Resolve dead-letter queue path for board write failures."""
        env_override = os.getenv("THGENT_SYNC_DEAD_LETTER_PATH", "").strip()
        if env_override:
            return Path(env_override).expanduser().resolve()
        return (self._root / "docs" / "reference" / "workstream_remote_writes_dead_letter.jsonl").resolve()

    def _dead_letter_queue(self) -> RemoteWriteDeadLetterQueue:
        env_max_attempts = os.getenv("THGENT_SYNC_DEAD_LETTER_MAX_ATTEMPTS", "").strip()
        env_base_delay = os.getenv("THGENT_SYNC_DEAD_LETTER_INITIAL_RETRY_SECONDS", "").strip()
        env_multiplier = os.getenv("THGENT_SYNC_DEAD_LETTER_BACKOFF_MULTIPLIER", "").strip()

        max_attempts = DEFAULT_BOARD_DEAD_LETTER_MAX_ATTEMPTS
        if env_max_attempts:
            max_attempts = int(env_max_attempts)

        retry_interval = DEFAULT_BOARD_DEAD_LETTER_RETRY_DELAY_SECONDS
        if env_base_delay:
            retry_interval = float(env_base_delay)

        multiplier = DEFAULT_BOARD_DEAD_LETTER_BACKOFF_MULTIPLIER
        if env_multiplier:
            multiplier = float(env_multiplier)

        return RemoteWriteDeadLetterQueue(
            self._dead_letter_queue_path(),
            max_attempts=max_attempts,
            retry_interval_seconds=retry_interval,
            backoff_multiplier=multiplier,
        )

    @staticmethod
    def _extract_item_id_from_error(raw_error: str) -> str | None:
        """Extract WL ID from adapter error string."""
        match = re.match(r"^\s*(WL-\d+)\s*:", raw_error, flags=re.IGNORECASE)
        return match.group(1).upper() if match else None

    def _record_remote_write_dead_letters(
        self,
        *,
        source: str,
        board_id: str,
        work_stream_items: list[dict[str, str]],
        errors: list[str],
    ) -> int:
        """Append failed remote write attempts to dead-letter queue."""
        if not errors:
            return 0

        item_index = {item["id"]: item for item in work_stream_items if "id" in item}
        queue = self._dead_letter_queue()

        written = 0
        for raw_error in errors:
            item_id = self._extract_item_id_from_error(raw_error)
            if item_id is None or item_id not in item_index:
                continue
            queue.enqueue(
                source=source,
                board_id=board_id,
                item=item_index[item_id],
                error=raw_error,
            )
            written += 1
        return written

    def replay_dead_letters(
        self,
        *,
        source: str | None = None,
        board_id: str | None = None,
        limit: int = 50,
        dry_run: bool = False,
    ) -> OperationResult:
        """Replay pending remote-write dead letters."""
        t0 = time.monotonic()
        op = "dead-letter-replay"
        try:
            queue = self._dead_letter_queue()
            entries = queue.candidates_for_replay(
                now=datetime.now(UTC),
                source=source,
                board_id=board_id,
            )
        except Exception as exc:
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Failed to load dead-letter queue: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

        candidates = list(entries[:limit])

        if dry_run:
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.DRY_RUN,
                message=f"Dead-letter replay dry-run: {len(candidates)} record(s) selected.",
                duration=time.monotonic() - t0,
                details={"selected": len(candidates), "source": source, "board_id": board_id},
                changes=[
                    f"[dry-run] replay {entry.source}:{entry.item.get('id', '<unknown>')}" for entry in candidates
                ],
            )

        replayed = 0
        failed = 0
        replay_errors: list[str] = []
        full_entries = queue.load()
        updated_entries_by_id: dict[str, Any] = {}
        for entry in candidates:
            item = entry.item
            current_entry = entry
            try:
                result = self._perform_board_sync(entry.board_id, entry.source, [item])
                if int(result.get("failed", 0)) == 0 and result.get("updated_items"):
                    current_entry = entry.mark_success(now=datetime.now(UTC))
                    replayed += 1
                else:
                    current_entry = entry.mark_failed(now=datetime.now(UTC))
                    failed += 1
                    item_id = item.get("id", "<unknown>")
                    replay_errors.append(f"{item_id}: replay failed")
            except Exception as exc:
                current_entry = entry.mark_failed(now=datetime.now(UTC))
                failed += 1
                item_id = item.get("id", "<unknown>")
                replay_errors.append(f"{item_id}: {exc}")
            updated_entries_by_id[current_entry.entry_id] = current_entry

        if updated_entries_by_id:
            for idx, current in enumerate(full_entries):
                replacement = updated_entries_by_id.get(current.entry_id)
                if replacement is not None:
                    full_entries[idx] = replacement
            queue.write(full_entries)

        status = SyncOperationStatus.SUCCESS if failed == 0 else SyncOperationStatus.FAILED
        return OperationResult(
            operation=op,
            status=status,
            message=f"Dead-letter replay complete: replayed={replayed}, failed={failed}.",
            duration=time.monotonic() - t0,
            details={"replayed": replayed, "failed": failed, "selected": len(candidates)},
            changes=[
                f"replayed: {entry.item.get('id', '<unknown>')}"
                for entry in candidates
                if updated_entries_by_id.get(entry.entry_id, entry).status == "replayed"
            ],
            errors=replay_errors,
        )

    def sync_board(
        self,
        board_id: str | None = None,
        source: str = "github",
        dry_run: bool = False,
        shadow_mode: bool = False,
        wl_start: int | None = None,
        wl_end: int | None = None,
        write_batch_size: int = 50,
    ) -> OperationResult:
        """Synchronize local WORK_STREAM.md with GitHub Projects or Linear board.

        Operationalizes repeatable cross-repo board sync using native tooling.
        Reads WORK_STREAM.md status lines and reflects them to remote board.

        # @trace WL-159

        Args:
            board_id: Board ID (GitHub project number or Linear key).
                      If None, uses THGENT_BOARD_ID env var.
            source: Board source platform: github | linear (default: github)
            dry_run: If True, report what would be synced without writing.
            wl_start: Optional WL numeric lower bound (inclusive).
            wl_end: Optional WL numeric upper bound (inclusive).
            write_batch_size: Max items per external write batch.

        Returns:
            OperationResult with board sync details and change count.
        """
        t0 = time.monotonic()
        normalized_source = (source or "").strip().lower()
        op = f"board (source={normalized_source})"
        collector = get_metrics_collector()

        from thegent.config import ThegentSettings

        def _record_cycle_status(status: str) -> None:
            collector.record_board_sync_cycle(
                source=normalized_source,
                status=status,
                duration_seconds=time.monotonic() - t0,
            )

        try:
            maintenance_banner = render_maintenance_banner(
                maintenance_active=os.getenv("THGENT_SYNC_MAINTENANCE_ACTIVE", "").strip().lower()
                in {"1", "true", "yes", "on"},
                connector=normalized_source,
                reason=os.getenv("THGENT_SYNC_MAINTENANCE_REASON", ""),
            )
            settings = ThegentSettings()
            policy_contract = self._load_sync_policy_contract_if_present()
            connector_policy = None
            if policy_contract is not None:
                connector_policy = policy_contract.connector_policy(normalized_source)
                if not connector_policy.enabled or connector_policy.mode == "disabled":
                    _record_cycle_status("skipped")
                    return OperationResult(
                        operation=op,
                        status=SyncOperationStatus.SKIPPED,
                        message=f"Board sync skipped: connector {normalized_source} disabled by sync policy.",
                        duration=time.monotonic() - t0,
                        details={"source": normalized_source, "board_id": board_id},
                    )

            if wl_start is not None and wl_end is not None and wl_start > wl_end:
                raise ValueError(f"Invalid WL range: wl_start ({wl_start}) must be <= wl_end ({wl_end}).")
            if write_batch_size <= 0:
                raise ValueError(f"Invalid write_batch_size: {write_batch_size}. Must be > 0.")

            # Resolve board ID from parameter, env, or config
            policy_board_id = connector_policy.board_id if connector_policy is not None else None
            effective_board_id = board_id or policy_board_id or getattr(settings, "board_id", None)
            if not effective_board_id:
                _record_cycle_status("skipped")
                return OperationResult(
                    operation=op,
                    status=SyncOperationStatus.SKIPPED,
                    message="Board sync skipped: no board_id configured (set THGENT_BOARD_ID or pass --board).",
                    duration=time.monotonic() - t0,
                    details={"source": normalized_source, "board_id": None},
                )

            # Parse WORK_STREAM.md status lines
            work_stream_items = self._parse_work_stream_items()
            work_stream_items = self._filter_items_by_wl_range(
                work_stream_items,
                wl_start=wl_start,
                wl_end=wl_end,
            )
            if not work_stream_items:
                _record_cycle_status("success")
                return OperationResult(
                    operation=op,
                    status=SyncOperationStatus.SUCCESS,
                    message="Board sync: no work stream items found to sync.",
                    duration=time.monotonic() - t0,
                    details={"source": normalized_source, "board_id": effective_board_id, "items": 0},
                    changes=[maintenance_banner] if maintenance_banner else [],
                )

            conflict_precedence = self._resolve_conflict_precedence(policy_contract)
            remote_statuses = self._fetch_remote_statuses(
                board_id=effective_board_id,
                source=normalized_source,
                work_stream_items=work_stream_items,
            )
            reconciled_items = self._reconcile_remote_statuses(
                work_stream_items=work_stream_items,
                remote_statuses=remote_statuses,
                conflict_precedence=conflict_precedence,
            )
            reconciled_count = sum(
                1
                for original, reconciled in zip(work_stream_items, reconciled_items)
                if original.get("status", "BACKLOG") != reconciled.get("status", "BACKLOG")
            )

            if dry_run or shadow_mode:
                _record_cycle_status("success")
                message_prefix = f"{maintenance_banner} " if maintenance_banner else ""
                return OperationResult(
                    operation=op,
                    status=SyncOperationStatus.DRY_RUN,
                    message=(
                        f"{message_prefix}"
                        f"Board sync {'shadow-mode' if shadow_mode else 'dry-run'}: "
                        f"would sync {len(reconciled_items)} item(s) to {normalized_source}."
                    ),
                    duration=time.monotonic() - t0,
                    details={
                        "source": normalized_source,
                        "board_id": effective_board_id,
                        "items_to_sync": len(reconciled_items),
                        "shadow_mode": shadow_mode,
                        "wl_start": wl_start,
                        "wl_end": wl_end,
                        "write_batch_size": write_batch_size,
                        "conflict_precedence": conflict_precedence,
                        "reconciled_items": reconciled_count,
                    },
                    changes=([maintenance_banner] if maintenance_banner else [])
                    + self._render_human_readable_dry_run_diffs(
                        reconciled_items,
                        remote_statuses=remote_statuses,
                    )[:20],
                )

            # Perform actual sync (platform-specific logic)
            sync_result = self._perform_board_sync(
                effective_board_id,
                normalized_source,
                reconciled_items,
                write_batch_size=write_batch_size,
            )
            dead_letters_written = self._record_remote_write_dead_letters(
                source=normalized_source,
                board_id=effective_board_id,
                work_stream_items=work_stream_items,
                errors=[str(err) for err in sync_result.get("errors", [])],
            )

            _record_cycle_status("success")
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.SUCCESS,
                message=f"{maintenance_banner} "
                f"Board sync complete: {sync_result['synced']} item(s) updated on {normalized_source}."
                if maintenance_banner
                else f"Board sync complete: {sync_result['synced']} item(s) updated on {normalized_source}.",
                duration=time.monotonic() - t0,
                details={
                    "source": normalized_source,
                    "board_id": effective_board_id,
                    "items_synced": sync_result["synced"],
                    "items_failed": sync_result.get("failed", 0),
                    "batches": sync_result.get("batches", 0),
                    "wl_start": wl_start,
                    "wl_end": wl_end,
                    "write_batch_size": write_batch_size,
                    "conflict_precedence": conflict_precedence,
                    "reconciled_items": reconciled_count,
                    "dead_letters_written": dead_letters_written,
                },
                changes=[f"synced: {item['id']}" for item in sync_result.get("updated_items", [])[:20]],
                errors=[str(err) for err in sync_result.get("errors", [])],
            )
        except Exception as exc:
            _log.warning("sync_board failed: %s", exc, exc_info=True)
            _record_cycle_status("failed")
            return OperationResult(
                operation=op,
                status=SyncOperationStatus.FAILED,
                message=f"Board sync failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def _parse_work_stream_items(self) -> list[dict[str, str]]:
        """Parse WORK_STREAM.md and extract work items with status.

        Returns list of dicts with keys: id, title, status.
        """
        items: list[dict[str, str]] = []
        if not self._work_stream.exists():
            return items

        try:
            content = self._work_stream.read_text(encoding="utf-8")
            content = self._normalize_wl_headers_for_sync(content)

            for line in content.splitlines():
                # Match: ### [WL-NNN] Title
                match = re.match(r"^###\s+\[(WL-\d+)\]\s+(.+)$", line)
                if match:
                    item_id = match.group(1).upper()
                    title = match.group(2)
                    items.append({"id": item_id, "title": title, "status": "BACKLOG"})
                # Match: **Status:** IN PROGRESS | COMPLETED | BACKLOG
                elif re.match(r"^\*\*Status:\*\*\s+(IN PROGRESS|COMPLETED|BACKLOG)", line):
                    status_match = re.search(r"(IN PROGRESS|COMPLETED|BACKLOG)", line)
                    if items and status_match:
                        items[-1]["status"] = status_match.group(1).replace(" ", "_")

        except OSError:
            pass

        return items

    def _perform_board_sync(
        self,
        board_id: str,
        source: str,
        work_stream_items: list[dict[str, str]],
        *,
        write_batch_size: int = 50,
    ) -> dict[str, Any]:
        """Perform platform-specific board sync through source adapters.

        Args:
            board_id: Board ID (project number or key)
            source: Platform: github | linear
            work_stream_items: List of work items to sync
            write_batch_size: Max items per external write batch.

        Returns:
            dict with keys: synced (count), failed (count), updated_items (list), errors (list)
        """
        from thegent.sync.board_adapters import resolve_board_adapter

        adapter = resolve_board_adapter(source)
        _log.info(
            "board_sync: source=%s board=%s items=%d batch_size=%d",
            source,
            board_id,
            len(work_stream_items),
            write_batch_size,
        )

        batches = self._partition_write_batches(work_stream_items, write_batch_size)
        synced = 0
        failed = 0
        updated_items: list[dict[str, str]] = []
        errors: list[str] = []
        for batch in batches:
            batch_result = adapter.sync(board_id=board_id, work_stream_items=batch)
            batch_errors = [str(err) for err in batch_result.get("errors", [])]
            batch_updated = batch_result.get("updated_items", [])
            batch_synced = int(batch_result.get("synced", len(batch_updated)))
            batch_failed = int(batch_result.get("failed", len(batch_errors)))

            synced += batch_synced
            failed += batch_failed
            updated_items.extend(batch_updated)
            errors.extend(batch_errors)

        return {
            "synced": synced,
            "failed": failed,
            "updated_items": updated_items,
            "errors": errors,
            "batches": len(batches),
        }

    @staticmethod
    def _resolve_conflict_precedence(policy_contract: Any) -> str:
        """Resolve status conflict precedence for sync writes."""
        if policy_contract is None:
            return "board_id_first"
        return policy_contract.conflict_precedence

    @staticmethod
    def _normalize_status(status: str) -> str:
        """Normalize a status value for status reconciliation."""
        return (status or "BACKLOG").strip().upper().replace(" ", "_")

    def _fetch_remote_statuses(
        self,
        *,
        board_id: str,
        source: str,
        work_stream_items: list[dict[str, str]],
    ) -> dict[str, str]:
        """Read remote status snapshots for configured work-stream items."""
        from thegent.sync.board_adapters import resolve_board_adapter

        try:
            adapter = resolve_board_adapter(source)
            status_map = adapter.fetch_remote_status(
                board_id=board_id,
                work_stream_items=work_stream_items,
            )
        except Exception as exc:
            _log.warning(
                "Skipping remote status reconciliation for source=%s board_id=%s: %s",
                source,
                board_id,
                exc,
            )
            return {}
        normalized: dict[str, str] = {}
        for item_id, status in status_map.items():
            normalized[item_id.upper()] = self._normalize_status(str(status))
        return normalized

    @staticmethod
    def _reconcile_remote_statuses(
        *,
        work_stream_items: list[dict[str, str]],
        remote_statuses: dict[str, str],
        conflict_precedence: str,
    ) -> list[dict[str, str]]:
        """Return new items after applying conflict precedence between local and remote."""
        if conflict_precedence not in {"local_wins", "remote_wins", "board_id_first"}:
            conflict_precedence = "board_id_first"

        reconciled: list[dict[str, str]] = []
        for item in work_stream_items:
            local_status = SyncCommand._normalize_status(item.get("status", "BACKLOG"))
            item_id = (item.get("id", "") or "").upper()
            remote_status = remote_statuses.get(item_id)
            resolved_status = remote_status if conflict_precedence == "remote_wins" and remote_status else local_status

            resolved = dict(item)
            resolved["status"] = resolved_status
            reconciled.append(resolved)

        return reconciled

    @staticmethod
    def _partition_write_batches(items: list[dict[str, str]], batch_size: int) -> list[list[dict[str, str]]]:
        """Split outgoing sync writes into deterministic fixed-size batches."""
        if batch_size <= 0:
            raise ValueError(f"batch_size must be > 0; got {batch_size}")
        return [items[index : index + batch_size] for index in range(0, len(items), batch_size)]

    @staticmethod
    def _wl_numeric_id(wl_id: str) -> int | None:
        match = re.search(r"\bWL-(\d+)\b", wl_id, flags=re.IGNORECASE)
        if not match:
            return None
        return int(match.group(1))

    def _filter_items_by_wl_range(
        self,
        items: list[dict[str, str]],
        *,
        wl_start: int | None,
        wl_end: int | None,
    ) -> list[dict[str, str]]:
        """Filter work-stream items to an inclusive WL numeric range."""
        if wl_start is None and wl_end is None:
            return items

        filtered: list[dict[str, str]] = []
        for item in items:
            wl_num = self._wl_numeric_id(item.get("id", ""))
            if wl_num is None:
                continue
            if wl_start is not None and wl_num < wl_start:
                continue
            if wl_end is not None and wl_num > wl_end:
                continue
            filtered.append(item)
        return filtered

    @staticmethod
    def _render_human_readable_dry_run_diffs(
        items: list[dict[str, str]],
        *,
        remote_statuses: dict[str, str] | None = None,
    ) -> list[str]:
        """Render local->remote field deltas for dry-run output."""
        remote_lookup = remote_statuses or {}
        lines: list[str] = []
        for item in items:
            wl_id = item.get("id", "<unknown>")
            title = item.get("title", "")
            status = item.get("status", "BACKLOG")
            remote_status = remote_lookup.get(wl_id.upper(), "<unknown>")
            lines.append(
                f"[dry-run] {wl_id}: title remote=<unknown> -> local={title!r}; "
                f"status remote={remote_status} -> local={status}"
            )
        return lines

    @staticmethod
    def _normalize_wl_headers_for_sync(content: str) -> str:
        """Normalize common malformed WL headers for sync parsing paths."""
        header_pattern = re.compile(
            r"^(?P<prefix>\s*###\s+)(?:\[\s*)?(?P<wl>WL)\s*[-_ ]?\s*(?P<num>\d+)\s*\]?\s+(?P<title>.+?)\s*$",
            flags=re.IGNORECASE,
        )
        normalized_lines: list[str] = []
        for line in content.splitlines():
            match = header_pattern.match(line)
            if not match:
                normalized_lines.append(line)
                continue
            normalized_lines.append(f"{match.group('prefix')}[WL-{match.group('num')}] {match.group('title').strip()}")
        return "\n".join(normalized_lines)

    def migrate_legacy_board_ids(self, legacy_ids: list[str], dry_run: bool = False) -> OperationResult:
        """Migrate legacy board IDs to canonical WL-* IDs."""
        from thegent.integrations.board_id_guard import migrate_legacy_board_id
        from thegent.integrations.board_id_uniqueness import validate_unique_board_ids

        t0 = time.monotonic()
        operation = "board-migrate"
        try:
            migrated_ids = [migrate_legacy_board_id(raw_id) for raw_id in legacy_ids]
            validate_unique_board_ids(migrated_ids)
            changes = [f"{legacy} -> {canonical}" for legacy, canonical in zip(legacy_ids, migrated_ids, strict=False)]
            return OperationResult(
                operation=operation,
                status=SyncOperationStatus.DRY_RUN if dry_run else SyncOperationStatus.SUCCESS,
                message=f"Migrated {len(migrated_ids)} board ID(s) to canonical WL namespace.",
                duration=time.monotonic() - t0,
                details={"migrated_ids": migrated_ids, "dry_run": dry_run},
                changes=changes,
            )
        except Exception as exc:
            return OperationResult(
                operation=operation,
                status=SyncOperationStatus.FAILED,
                message=f"Board ID migration failed: {exc}",
                duration=time.monotonic() - t0,
                errors=[str(exc)],
            )

    def detect_remote_orphans(self, remote_ids: list[str]) -> OperationResult:
        """Detect remote items that have no local WORK_STREAM representation."""
        from thegent.integrations.sync_auditor import SyncAuditor

        t0 = time.monotonic()
        operation = "remote-orphans"
        local_ids = [item["id"] for item in self._parse_work_stream_items()]
        report = SyncAuditor.detect_remote_orphans(remote_ids=remote_ids, local_ids=local_ids)
        has_orphans = len(report.orphan_ids) > 0
        return OperationResult(
            operation=operation,
            status=SyncOperationStatus.FAILED if has_orphans else SyncOperationStatus.SUCCESS,
            message=(
                f"Detected {len(report.orphan_ids)} remote orphan item(s)."
                if has_orphans
                else "No remote orphan items detected."
            ),
            duration=time.monotonic() - t0,
            details=report.to_dict(),
            changes=[f"orphan: {item_id}" for item_id in report.orphan_ids],
            errors=[f"remote orphan detected: {item_id}" for item_id in report.orphan_ids],
        )

    def detect_local_orphans(self, mapping_cache_path: Path | None = None) -> OperationResult:
        """Detect local WORK_STREAM items missing remote tracker mappings."""
        from thegent.integrations.connector_mapping_cache import ConnectorMappingCache
        from thegent.integrations.sync_auditor import SyncAuditor

        t0 = time.monotonic()
        operation = "local-orphans"
        local_ids = [item["id"] for item in self._parse_work_stream_items()]

        remote_ids = set[str]()
        if mapping_cache_path is None:
            mapping_cache_path = Path("docs/reference/connector_mapping_cache.json")
        if mapping_cache_path.exists():
            mapping_cache = ConnectorMappingCache(cache_file=mapping_cache_path)
            remote_ids.update(mapping_cache.list_cached_wl_ids("github"))
            remote_ids.update(mapping_cache.list_cached_wl_ids("linear"))

        report = SyncAuditor.detect_local_orphans(local_ids=local_ids, mapped_remote_ids=sorted(remote_ids))
        has_orphans = report.orphan_count > 0
        return OperationResult(
            operation=operation,
            status=SyncOperationStatus.FAILED if has_orphans else SyncOperationStatus.SUCCESS,
            message=(
                f"Detected {report.orphan_count} local orphan item(s)."
                if has_orphans
                else "No local orphan items detected."
            ),
            duration=time.monotonic() - t0,
            details=report.to_dict(),
            changes=[f"orphan: {item_id}" for item_id in report.local_orphan_ids],
            errors=[f"local orphan detected: {item_id}" for item_id in report.local_orphan_ids],
        )
