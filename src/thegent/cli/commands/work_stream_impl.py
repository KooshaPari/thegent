"""Work stream management: parse, collect, claim, complete, incorporate, do-next, wait-next, spawn-next.

Extracted from impl.py as part of WL-120 LOC Reduction Program (Phase 2).
Contains:
- WORK_STREAM.md parsing and dependency checking
- Priority sorting and item collection
- Queue collection (PromptQueue, EscalationQueue, DeferralManager, BacklogManager)
- Pre-work governance hard gate
- do_next_impl, wait_next_impl, spawn_next_impl
- work_stream_claim_impl, work_stream_complete_impl, incorporate_impl
- continuity_snapshot_impl
- _validate_task_and_record_errors
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from thegent.cli.services import pre_work_gate_helpers
from thegent.cli.services import work_stream_orchestration
from thegent.config import ThegentSettings


def _parse_work_stream_md(work_stream_path: Path) -> dict[str, Any]:
    """Parse WORK_STREAM.md into structured data."""
    if not work_stream_path.exists():
        return {"backlog": [], "claimed": [], "completed": []}

    content = work_stream_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    backlog: list[dict[str, Any]] = []
    claimed: set[str] = set()
    completed: set[str] = set()

    current_section: str | None = None
    in_table = False
    header_seen = False

    for _i, line in enumerate(lines):
        stripped = line.strip()

        # Detect section headers
        if stripped.startswith(("## BACKLOG", "## PENDING")):
            current_section = "backlog"
            in_table = False
            header_seen = False
            continue
        if stripped.startswith("## CLAIMED"):
            current_section = "claimed"
            in_table = False
            header_seen = False
            continue
        if stripped.startswith("## COMPLETED"):
            current_section = "completed"
            in_table = False
            header_seen = False
            continue

        # If we hit another ## section, only reset if it's not one of our known sections
        # and we are NOT in backlog (backlog can have multiple ## subsections like ## heliosShield)
        if stripped.startswith("## ") and current_section != "backlog":
            current_section = None
            continue

        # Detect table headers within a section (even under ### subheaders)
        if (
            current_section
            and stripped.startswith("|")
            and "ID" in stripped.upper()
            and ("Title" in stripped or "Description" in stripped)
        ):
            header_seen = True
            in_table = True
            continue

        # Parse table rows
        if current_section and stripped.startswith("|") and "|" in stripped[1:]:
            if not header_seen:
                # Skip header row
                if "ID" in stripped.upper() or "----" in stripped:
                    header_seen = True
                    in_table = True
                    continue
            elif in_table or header_seen:
                # Parse data row: | ID | Title | Source | Priority | Depends |
                parts = [p.strip() for p in stripped.split("|") if p.strip()]
                if len(parts) >= 2:
                    item_id = parts[0]
                    # Skip separator or header-like rows
                    if item_id.startswith("---") or item_id.upper() == "ID":
                        continue

                    # Check for row-level status override (Status is column 6)
                    row_status = parts[5].upper() if len(parts) >= 6 else ""

                    if current_section == "backlog" or row_status == "PENDING":
                        # If row says COMPLETED or CLAIMED, ignore it for backlog
                        if "COMPLETED" in row_status:
                            completed.add(item_id)
                            continue
                        if "CLAIMED" in row_status or "IN_PROGRESS" in row_status:
                            claimed.add(item_id)
                            continue

                        title = parts[1] if len(parts) > 1 else ""
                        task_type = parts[2] if len(parts) > 2 else "feature"
                        depends_str = parts[3] if len(parts) > 3 else ""
                        depends = [d.strip() for d in depends_str.split(",") if d.strip()] if depends_str else []

                        backlog.append(
                            {
                                "id": item_id,
                                "title": title,
                                "description": title,
                                "source": task_type,  # Using Type column as source
                                "priority": "P2",  # Default to P2 if not found
                                "depends": depends,
                            }
                        )
                    elif current_section == "claimed" or "CLAIMED" in row_status or "IN_PROGRESS" in row_status:
                        claimed.add(item_id)
                    elif current_section == "completed" or "COMPLETED" in row_status:
                        completed.add(item_id)

    return {"backlog": backlog, "claimed": claimed, "completed": completed}


def _check_dependencies_satisfied(item: dict[str, Any], completed: set[str], claimed: set[str]) -> bool:
    """Check if all dependencies for an item are satisfied (completed or claimed)."""
    depends = item.get("depends", [])
    if not depends:
        return True

    # Filter out common placeholders/status markers that aren't task IDs
    ignore_patterns = ["-", "\u2014", "\u2705", "COMPLETE", "HYBRID_ENV", "PROMPT_HISTORY"]

    actual_depends = []
    for dep in depends:
        dep_clean = dep.strip()
        if not dep_clean:
            continue
        # Skip if it looks like a note or status rather than an ID
        if any(p in dep_clean.upper() for p in ignore_patterns):
            continue
        actual_depends.append(dep_clean)

    if not actual_depends:
        return True

    # Dependencies should be completed (not just claimed)
    return all(dep in completed for dep in actual_depends)


def _priority_sort_key(priority: str) -> int:
    """Convert priority string (P1, P2, P3) to sortable integer."""
    if priority.startswith("P"):
        try:
            return int(priority[1:])
        except ValueError:
            pass
    return 999  # Unknown priorities go last


def _collect_work_stream_items(work_stream_path: Path, limit: int) -> tuple[list[dict[str, Any]], list[str]]:
    """Collect available items from WORK_STREAM.md. Returns (items, sources_checked)."""
    if not work_stream_path.exists():
        return [], []
    parsed = _parse_work_stream_md(work_stream_path)
    backlog = parsed["backlog"]
    claimed = parsed["claimed"]
    completed = parsed["completed"]
    available = []
    for item in backlog:
        item_id = item["id"]
        if item_id in claimed or item_id in completed:
            continue
        if not _check_dependencies_satisfied(item, completed, claimed):
            continue
        available.append(item)
    available.sort(key=lambda x: _priority_sort_key(x.get("priority", "P2")))
    items = []
    for item in available[:limit]:
        title = item.get("title", item.get("description", item["id"]))
        items.append(
            {
                "id": item["id"],
                "description": title,
                "source": item.get("source", "WORK_STREAM"),
                "priority": item.get("priority", "P2"),
                "prompt_suggestion": f"Complete {item['id']}: {title}",
                "_sort_order": 4,  # WORK_STREAM after queues
            }
        )
    return items, ["WORK_STREAM.md"]


def _collect_queued_items(settings: ThegentSettings, limit: int) -> tuple[list[dict[str, Any]], list[str]]:
    """Collect defers and other queued work from PromptQueue, EscalationQueue, DeferralQueue, BacklogManager."""
    items: list[dict[str, Any]] = []
    sources: list[str] = []
    session_dir = Path(settings.session_dir).expanduser().resolve()

    # 1. PromptQueue ($defer prompts)
    try:
        from thegent.queue.storage import PromptQueue

        pq = PromptQueue(session_dir)
        all_items = pq.list_all(include_done=False, include_expired=True, limit=limit)
        pending_items = [(it["id"], it) for it in all_items if it.get("status") == "pending"]
        for queue_item_id, p in pending_items:
            prompt = p.get("prompt", "")
            project = p.get("project", "")
            items.append(
                {
                    "id": f"defer-{queue_item_id}",
                    "description": prompt[:80] + ("..." if len(prompt) > 80 else ""),
                    "source": "PROMPT_QUEUE",
                    "priority": "P1",
                    "prompt_suggestion": prompt,
                    "queue_item_id": queue_item_id,
                    "project": project,
                    "_sort_order": 1,
                }
            )
        if pending_items:
            sources.append("PROMPT_QUEUE")
    except Exception:
        pass

    # 2. EscalationQueue (past-SLA blocked runs)
    try:
        from thegent.execution import EscalationQueue

        eq = EscalationQueue(session_dir)
        past_sla = eq.list_pending(past_sla_only=True, limit=limit)
        for e in past_sla:
            run_id = e.get("run_id", "?")
            reason = e.get("reason", "")
            items.append(
                {
                    "id": f"escalation-{run_id}",
                    "description": f"Resolve escalation: {reason[:60]}",
                    "source": "ESCALATION",
                    "priority": "P0",
                    "prompt_suggestion": f"Resolve escalation {run_id}: {reason}",
                    "run_id": run_id,
                    "_sort_order": 0,
                }
            )
        if past_sla:
            sources.append("ESCALATION")
    except Exception:
        pass

    # 3. DeferralManager (deferred_tasks.jsonl) + DeferralQueue (deferral_queue.jsonl)
    try:
        from thegent.orchestration.resilience.deferral import DeferralManager

        dm = DeferralManager(settings)
        deferred = dm.list_deferred()
        for d in deferred[:limit]:
            task_id = d.get("task_id", "?")
            reason = d.get("reason", "")
            items.append(
                {
                    "id": f"deferral-{task_id}",
                    "description": f"Resume deferred: {reason[:60]}",
                    "source": "DEFERRAL",
                    "priority": "P1",
                    "prompt_suggestion": f"Resume deferred task {task_id}",
                    "task_id": task_id,
                    "_sort_order": 2,
                }
            )
        # Also read deferral_queue.jsonl (run-level deferrals)
        dq_path = session_dir / "deferral_queue.jsonl"
        if dq_path.exists():
            with dq_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                        if d.get("status") != "deferred":
                            continue
                        run_id = d.get("run_id", "?")
                        reason = d.get("reason", "")
                        items.append(
                            {
                                "id": f"deferral-{run_id}",
                                "description": f"Resume deferred run: {reason[:60]}",
                                "source": "DEFERRAL",
                                "priority": "P1",
                                "prompt_suggestion": f"Resume deferred run {run_id}",
                                "run_id": run_id,
                                "_sort_order": 2,
                            }
                        )
                        if len([i for i in items if i.get("source") == "DEFERRAL"]) >= limit:
                            break
                    except Exception:
                        continue
        if any(i.get("source") == "DEFERRAL" for i in items):
            sources.append("DEFERRAL")
    except Exception:
        pass

    # 4. BacklogManager (AgilePlus pending findings)
    try:
        from thegent.governance.backlog import BacklogManager

        bm = BacklogManager(session_dir)
        pending = bm.get_pending()
        for p in pending[:limit]:
            item_id = p.item_id
            desc = p.description[:60] + ("..." if len(p.description) > 60 else "")
            items.append(
                {
                    "id": f"backlog-{item_id}",
                    "description": desc,
                    "source": "BACKLOG",
                    "priority": "P2",
                    "prompt_suggestion": f"Address finding {p.finding_id}: {p.description}",
                    "backlog_item_id": item_id,
                    "_sort_order": 3,
                }
            )
        if pending:
            sources.append("BACKLOG")
    except Exception:
        pass

    return items, sources


def _pre_work_gate_defaults() -> dict[str, Any]:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.pre_work_gate_defaults()


def _pre_work_gate_thresholds(project_dir: Path) -> tuple[dict[str, Any], str]:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.pre_work_gate_thresholds(project_dir)


def _evidence_age_minutes(path: Path) -> int:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.evidence_age_minutes(path)


def _pre_work_governance_block_payload(
    *,
    project_dir: Path,
    thresholds: dict[str, Any],
    violations: list[dict[str, Any]],
    config_source: str,
) -> dict[str, Any]:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.pre_work_governance_block_payload(
        project_dir=project_dir,
        thresholds=thresholds,
        violations=violations,
        config_source=config_source,
    )


def _enforce_pre_work_hard_gate(project_dir: Path) -> dict[str, Any] | None:
    """Backward-compatible wrapper for extracted pre-work gate helper service."""
    return pre_work_gate_helpers.enforce_pre_work_hard_gate(project_dir)


# ---------------------------------------------------------------------------
# Public API: do-next, wait-next, spawn-next, claim, complete, incorporate
# ---------------------------------------------------------------------------

_log = __import__("logging").getLogger(__name__)


def do_next_impl(cd: Path | None = None, limit: int = 5) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.do_next_impl(cd=cd, limit=limit)


def wait_next_impl(
    cd: Path | None = None,
    poll_interval: float = 2.0,
    timeout: float = 0.0,
    sources: tuple[str, ...] = ("do_next",),
) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.wait_next_impl(
        cd=cd,
        poll_interval=poll_interval,
        timeout=timeout,
        sources=sources,
    )


def spawn_next_impl(
    cd: Path | None = None,
    limit: int = 10,
    agent: str = "free",
    timeout: int | None = None,
    lane: str = "critical",
    override_reason: str = "manual-next-step",
    claim: bool = True,
) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.spawn_next_impl(
        cd=cd,
        limit=limit,
        agent=agent,
        timeout=timeout,
        lane=lane,
        override_reason=override_reason,
        claim=claim,
    )


def work_stream_claim_impl(item_id: str, agent_id: str, cd: Path | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.work_stream_claim_impl(item_id=item_id, agent_id=agent_id, cd=cd)


def work_stream_complete_impl(item_id: str, agent_id: str, cd: Path | None = None) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.work_stream_complete_impl(item_id=item_id, agent_id=agent_id, cd=cd)


def incorporate_impl(cd: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.incorporate_impl(cd=cd, dry_run=dry_run)


def _validate_task_and_record_errors(tf: Path, validation_errors: list[dict[str, Any]]) -> None:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    work_stream_orchestration._validate_task_and_record_errors(tf=tf, validation_errors=validation_errors)


def continuity_snapshot_impl(
    owner: str,
    run_ids: list[str],
    state_summary: dict[str, Any] | None = None,
    next_steps: list[str] | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for shared work-stream orchestration service."""
    return work_stream_orchestration.continuity_snapshot_impl(
        owner=owner,
        run_ids=run_ids,
        state_summary=state_summary,
        next_steps=next_steps,
    )
