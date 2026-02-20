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

try:
    import structlog

    _log = structlog.get_logger(__name__)
except ModuleNotFoundError:  # structlog not installed — fall back to stdlib
    import logging as _logging

    _log = _logging.getLogger(__name__)  # type: ignore[assignment]


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
            suffix = (
                f" {len(unregistered)} unregistered, {len(orphaned)} orphaned." if issues else " All OK."
            )
            msg = (
                f"Hooks validated: {len(disk_hooks)} on disk, {len(config_hooks)} in config.{suffix}"
            )

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
        """Show drift between local and remote agent config.

        Compares local agent persona files in ``agents/`` and local settings
        fields against what would be expected on a pristine remote.  Because
        actual remote connectivity is stubbed, this currently reports the
        local-only view; the detailed comparison will be wired up when the
        remote sync backend is implemented.

        Returns:
            OperationResult with drift summary in ``details``.
        """
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
        import os

        t0 = time.monotonic()
        op = "push"

        effective_target = target or os.environ.get("THGENT_SYNC_REMOTE", "<local-stub>")

        _log.info("sync push invoked: target=%s", effective_target)

        # Stub: collect what would be pushed
        local_agents = self._discover_agent_files()
        hook_scripts = sorted(self._discover_hook_scripts())
        files_would_push = [f"agents/{a}.md" for a in local_agents] + [
            f"hooks/{h}.sh" for h in hook_scripts
        ]

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
        import os

        t0 = time.monotonic()
        op = "pull"

        effective_source = source or os.environ.get("THGENT_SYNC_REMOTE", "<local-stub>")

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
            message=f"[stub] Reset would affect {len(files_would_reset)} file(s). "
            "No destructive changes were made.",
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
                if stripped.startswith("- [ ]") or (
                    stripped.startswith("|") and stripped.endswith("|")
                ):
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
