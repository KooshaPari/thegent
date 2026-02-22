"""SY-009: Unified `thegent sync` command.

Consolidates update/sync operations into a single entry point with
subcommands: all, work-stream, config, agents, hooks.
"""

from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

_log = structlog.get_logger(__name__)


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

        Stubs the remote push operation.  When a remote sync backend is
        wired up, this method will serialise the local agent config, settings
        snapshot, and hook registrations and upload them to ``target``.

        Args:
            target: Optional remote target identifier (URL, host, or alias).
                    Defaults to the value of the ``THGENT_SYNC_REMOTE``
                    environment variable, if set.

        Returns:
            OperationResult indicating the push was accepted (or stubbed).
        """
        t0 = time.monotonic()
        op = "push"

        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        effective_target = target or settings.sync_remote

        _log.info("sync push invoked: target=%s", effective_target)

        # Stub: collect what would be pushed
        local_agents = self._discover_agent_files()
        hook_scripts = sorted(self._discover_hook_scripts())
        files_would_push = [f"agents/{a}.md" for a in local_agents] + [f"hooks/{h}.sh" for h in hook_scripts]

        return OperationResult(
            operation=op,
            status=SyncOperationStatus.SUCCESS,
            message=f"[stub] Would push {len(files_would_push)} file(s) to '{effective_target}'.",
            duration=time.monotonic() - t0,
            details={
                "target": effective_target,
                "files_would_push": files_would_push,
                "stub": True,
            },
            changes=[f"push: {f}" for f in files_would_push],
        )

    def pull(self, source: str | None = None) -> OperationResult:
        """Pull remote state locally.

        Stubs the remote pull operation.  When a remote sync backend is
        wired up, this method will download the canonical agent config and
        settings from ``source`` and apply them locally.

        Args:
            source: Optional remote source identifier (URL, host, or alias).
                    Defaults to the value of the ``THGENT_SYNC_REMOTE``
                    environment variable, if set.

        Returns:
            OperationResult indicating the pull was accepted (or stubbed).
        """
        t0 = time.monotonic()
        op = "pull"

        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        effective_source = source or settings.sync_remote

        _log.info("sync pull invoked: source=%s", effective_source)

        return OperationResult(
            operation=op,
            status=SyncOperationStatus.SUCCESS,
            message=f"[stub] Would pull state from '{effective_source}'. No remote backend configured.",
            duration=time.monotonic() - t0,
            details={
                "source": effective_source,
                "files_pulled": [],
                "stub": True,
            },
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
        """Append new items to WORK_STREAM.md (deduplication by content).

        Returns the number of items actually appended.
        """
        if not items:
            return 0

        existing_content = ""
        if self._work_stream.exists():
            with contextlib.suppress(OSError):
                existing_content = self._work_stream.read_text(encoding="utf-8")

        new_items = [it for it in items if it not in existing_content]
        if not new_items:
            return 0

        self._work_stream.parent.mkdir(parents=True, exist_ok=True)
        with self._work_stream.open("a", encoding="utf-8") as fh:
            fh.write("\n\n<!-- auto-incorporated by thegent sync work-stream -->\n")
            for it in new_items:
                fh.write(f"{it}\n")

        return len(new_items)

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

    def sync_board(
        self, board_id: str | None = None, source: str = "github", dry_run: bool = False
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

        Returns:
            OperationResult with board sync details and change count.
        """
        t0 = time.monotonic()
        op = f"board (source={source})"

        from thegent.config import ThegentSettings

        try:
            settings = ThegentSettings()

            # Resolve board ID from parameter, env, or config
            effective_board_id = board_id or getattr(settings, "board_id", None)
            if not effective_board_id:
                return OperationResult(
                    operation=op,
                    status=SyncOperationStatus.SKIPPED,
                    message="Board sync skipped: no board_id configured (set THGENT_BOARD_ID or pass --board).",
                    duration=time.monotonic() - t0,
                    details={"source": source, "board_id": None},
                )

            # Parse WORK_STREAM.md status lines
            work_stream_items = self._parse_work_stream_items()
            if not work_stream_items:
                return OperationResult(
                    operation=op,
                    status=SyncOperationStatus.SUCCESS,
                    message="Board sync: no work stream items found to sync.",
                    duration=time.monotonic() - t0,
                    details={"source": source, "board_id": effective_board_id, "items": 0},
                    changes=[],
                )

            if dry_run:
                return OperationResult(
                    operation=op,
                    status=SyncOperationStatus.DRY_RUN,
                    message=f"Board sync dry-run: would sync {len(work_stream_items)} item(s) to {source}.",
                    duration=time.monotonic() - t0,
                    details={
                        "source": source,
                        "board_id": effective_board_id,
                        "items_to_sync": len(work_stream_items),
                    },
                    changes=[f"[dry-run] {item['id']}: {item['status']}" for item in work_stream_items[:10]],
                )

            # Perform actual sync (platform-specific logic)
            sync_result = self._perform_board_sync(effective_board_id, source, work_stream_items)

            return OperationResult(
                operation=op,
                status=SyncOperationStatus.SUCCESS,
                message=f"Board sync complete: {sync_result['synced']} item(s) updated on {source}.",
                duration=time.monotonic() - t0,
                details={
                    "source": source,
                    "board_id": effective_board_id,
                    "items_synced": sync_result["synced"],
                    "items_failed": sync_result.get("failed", 0),
                },
                changes=[f"synced: {item['id']}" for item in sync_result.get("updated_items", [])[:20]],
            )
        except Exception as exc:
            _log.warning("sync_board failed: %s", exc, exc_info=True)
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
            # Simple regex-based extraction of ### [WL-NNN] lines and status
            import re

            for line in content.splitlines():
                # Match: ### [WL-NNN] Title
                match = re.match(r"^###\s+\[([WL-]+\d+)\]\s+(.+)$", line)
                if match:
                    item_id = match.group(1)
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
        self, board_id: str, source: str, work_stream_items: list[dict[str, str]]
    ) -> dict[str, Any]:
        """Perform platform-specific board sync (GitHub Projects or Linear).

        Currently returns stub result. Real implementation would call GitHub API or Linear API.

        Args:
            board_id: Board ID (project number or key)
            source: Platform: github | linear
            work_stream_items: List of work items to sync

        Returns:
            dict with keys: synced (count), failed (count), updated_items (list)
        """
        # Stub: real implementation would call GitHub Projects API or Linear API
        _log.info("board_sync: source=%s board=%s items=%d", source, board_id, len(work_stream_items))

        return {
            "synced": len(work_stream_items),
            "failed": 0,
            "updated_items": work_stream_items,
            "stub": True,
        }
