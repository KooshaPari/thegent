"""Journal/orchestration-event MCP tool registration helpers."""

from __future__ import annotations

import orjson as json
import time
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_journal_tools(*, mcp: FastMCP, logger: Any) -> tuple[object, ...]:
    """Register journal and orchestration-event MCP tools."""

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def journal_create_session(
        session_id: str,
        repo_path: str = ".",
        track_secrets: bool = True,
    ) -> dict[str, Any]:
        """Create a new git journal session for micro-commit audit trail."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournal

        journal = GitJournal(
            Path(repo_path).resolve(),
            session_id,
            track_secrets=track_secrets,
            auto_commit=True,
        )

        return {
            "status": "created",
            "session_id": session_id,
            "audit_ref": journal.audit_ref,
            "message": "Git journal session created. Changes will be tracked with micro-commits.",
            "note": "Audit refs are local-only and never pushed to remote.",
        }

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def journal_record_change(
        session_id: str,
        file_path: str,
        action: str = "modified",
        repo_path: str = ".",
        content: str | None = None,
    ) -> dict[str, Any]:
        """Record a file change as a micro-commit in the journal."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournal

        journal = GitJournal(Path(repo_path).resolve(), session_id)

        if content is not None:
            file_content = content.encode()
        else:
            full_path = Path(repo_path).resolve() / file_path
            if full_path.exists():
                file_content = full_path.read_bytes()
            else:
                file_content = None

        sha = journal.record_file_change(
            file_path,
            content=file_content,
            action=action,
        )

        return {
            "status": "recorded",
            "sha": sha,
            "file_path": file_path,
            "action": action,
            "session_id": session_id,
        }

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def journal_snapshot(
        session_id: str,
        message: str = "snapshot",
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """Create a snapshot of the current working tree state."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournal

        journal = GitJournal(Path(repo_path).resolve(), session_id)
        sha = journal.record_snapshot(message)

        return {
            "status": "snapshot_created",
            "sha": sha,
            "session_id": session_id,
            "message": message,
        }

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def journal_get_log(
        session_id: str,
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """Get the audit log for a journal session."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournal

        journal = GitJournal(Path(repo_path).resolve(), session_id)
        log_entries = journal.get_audit_log()

        return {
            "session_id": session_id,
            "entries": log_entries,
            "total": len(log_entries),
        }

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def journal_list_sessions(
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """List all git journal sessions in a repository."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournal

        sessions = GitJournal.list_sessions(Path(repo_path).resolve())

        return {
            "sessions": sessions,
            "total": len(sessions),
            "note": "All audit refs are local-only and never pushed to remote.",
        }

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def journal_finalize(
        session_id: str,
        message: str = "session complete",
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """Finalize a journal session with a summary commit."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournal

        journal = GitJournal(Path(repo_path).resolve(), session_id)
        sha = journal.finalize_session(message)

        return {
            "status": "finalized",
            "sha": sha,
            "session_id": session_id,
            "audit_ref": journal.audit_ref,
        }

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def journal_prune(
        repo_path: str = ".",
        max_age_days: int = 30,
    ) -> dict[str, Any]:
        """Prune old journal sessions."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournal

        pruned = GitJournal.prune_old_sessions(Path(repo_path).resolve(), max_age_days)

        return {
            "pruned_count": pruned,
            "max_age_days": max_age_days,
            "message": f"Pruned {pruned} sessions older than {max_age_days} days",
        }

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def journal_create_enhanced(
        session_id: str,
        repo_path: str = ".",
        track_secrets: bool = True,
        enable_watching: bool = False,
        enable_attestation: bool = False,
        batch_size: int = 10,
    ) -> dict[str, Any]:
        """Create an enhanced git journal session with P1 features."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournalEnhanced

        journal = GitJournalEnhanced(
            Path(repo_path).resolve(),
            session_id,
            track_secrets=track_secrets,
            auto_commit=True,
            enable_watching=enable_watching,
            enable_attestation=enable_attestation,
            batch_size=batch_size,
        )

        stats = journal.get_performance_stats()

        return {
            "status": "created",
            "session_id": session_id,
            "audit_ref": journal.audit_ref,
            "message": "Enhanced git journal session created.",
            "features": {
                "native_scanner": stats["native_scanner"],
                "watcher": stats["watcher"],
                "attestation": enable_attestation,
                "batch_size": batch_size,
            },
            "note": "Audit refs are local-only and never pushed to remote.",
        }

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def journal_start_watching(
        session_id: str,
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """Start real-time file watching for a journal session."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournalEnhanced

        journal = GitJournalEnhanced(
            Path(repo_path).resolve(),
            session_id,
            enable_watching=True,
        )

        journal.start_watching()
        stats = journal.get_performance_stats()

        return {
            "status": "watching_started",
            "session_id": session_id,
            "watcher": stats["watcher"],
            "message": f"File watching started using {stats['watcher'] or 'none'}",
        }

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def journal_get_attestations(
        session_id: str,
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """Get cryptographic attestations for a journal session."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournalEnhanced

        journal = GitJournalEnhanced(
            Path(repo_path).resolve(),
            session_id,
            enable_attestation=True,
        )

        attestations = journal.get_attestations()

        verified = []
        for att in attestations:
            is_valid = journal.verify_attestation(att)
            verified.append(
                {
                    "commit_sha": att["commit_sha"],
                    "timestamp": att["timestamp"],
                    "algorithm": att["algorithm"],
                    "verified": is_valid,
                }
            )

        return {
            "session_id": session_id,
            "attestations": verified,
            "total": len(attestations),
            "all_verified": all(a["verified"] for a in verified),
        }

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def journal_get_stats(
        session_id: str,
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """Get performance statistics for a journal session."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournalEnhanced

        journal = GitJournalEnhanced(Path(repo_path).resolve(), session_id)
        stats = journal.get_performance_stats()

        return {
            "session_id": session_id,
            "stats": stats,
        }

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    async def journal_record_async(
        session_id: str,
        file_path: str,
        action: str = "modified",
        repo_path: str = ".",
        content: str | None = None,
    ) -> dict[str, Any]:
        """Record a file change asynchronously in the journal."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournalAsync

        journal = GitJournalAsync.create(
            Path(repo_path).resolve(),
            session_id,
            enhanced=True,
        )

        file_content = content.encode() if content else None
        sha = await journal.record_file_change(file_path, file_content, action=action)

        return {
            "status": "recorded_async",
            "sha": sha,
            "file_path": file_path,
            "action": action,
            "session_id": session_id,
        }

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    def journal_flush_batch(
        session_id: str,
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """Flush pending batched changes as a single commit."""
        from phenotype_thegent_audit.audit.shadow_audit_git import GitJournalEnhanced

        journal = GitJournalEnhanced(Path(repo_path).resolve(), session_id)
        sha = journal._flush_batch()

        return {
            "status": "flushed",
            "sha": sha,
            "session_id": session_id,
            "message": "Batched changes flushed to single commit",
        }

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False})
    def phenotype_thegent_orchestration_events(
        max_events: int = 100,
        timeout_ms: int = 0,
    ) -> ToolResult:
        """WL-085: Drain SubAgentEvents from the process-global event queue."""
        import asyncio as _asyncio

        from phenotype_thegent_execution.orchestration.event_queue import get_global_event_queue

        logger.debug("phenotype_thegent_orchestration_events max_events=%d timeout_ms=%d", max_events, timeout_ms)
        start_time = time.perf_counter()

        queue = get_global_event_queue()
        events: list[dict[str, Any]] = []

        if timeout_ms > 0 and queue.empty:

            async def _wait_one() -> None:
                try:
                    evt = await _asyncio.wait_for(queue.get(), timeout=timeout_ms / 1000.0)
                    events.append(evt.model_dump())
                except TimeoutError:
                    pass

            _asyncio.run(_wait_one())

        remaining = max_events - len(events)
        for _ in range(remaining):
            if queue.empty:
                break
            evt = queue.get_nowait()
            events.append(evt.model_dump())

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        payload: dict[str, Any] = {"events": events, "count": len(events)}
        return ToolResult(
            content=json.dumps(payload).decode(),
            structured_content=payload,
            meta={"execution_time_ms": elapsed_ms},
        )

    return (
        journal_create_session,
        journal_record_change,
        journal_snapshot,
        journal_get_log,
        journal_list_sessions,
        journal_finalize,
        journal_prune,
        journal_create_enhanced,
        journal_start_watching,
        journal_get_attestations,
        journal_get_stats,
        journal_record_async,
        journal_flush_batch,
        phenotype_thegent_orchestration_events,
    )
