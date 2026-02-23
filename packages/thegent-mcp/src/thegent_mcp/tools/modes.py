"""MCP tools for Plan, Delegate, Discussion, Research, Validation modes and protocols.

Supports structured agent work: plans, elicitation briefs, research reports,
validation checklists, and mode-aware team orchestration.
"""

import json
import logging
import re
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastmcp.tools.tool import ToolResult

if TYPE_CHECKING:
    from fastmcp import FastMCP

import contextlib

from thegent.cli.commands.impl import _resolve_cwd
from thegent.config import ThegentSettings
from thegent.utils import is_dev_mode

_log = logging.getLogger(__name__)


async def _ctx_info(ctx: Any, message: str) -> None:
    """Send an info log message via FastMCP Context if available, else Python logging."""
    if ctx is not None:
        try:
            await ctx.info(message)
            return
        except Exception:
            pass
    _log.info(message)


def _get_project_root(cd: Path | None) -> Path | None:
    """Resolve project root from cwd.

    If in dev mode (running from source/git), returns the absolute project root.
    When installed as a package, returns the resolved work directory.
    """
    base = _resolve_cwd(cd)
    if base is None:
        return None

    if is_dev_mode():
        # In dev mode, we might want to return the actual git root
        # but _resolve_cwd already handles .git check
        pass

    return base


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _slugify(text: str, max_len: int = 32) -> str:
    """Create a filesystem-safe slug from text."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "_", slug).strip("_")
    return slug[:max_len] or "plan"


def register_modes(mcp: "FastMCP") -> None:
    """Register Plan, Delegate, Discussion, Research, Validation, and Protocol tools."""
    # Import CurrentContext for FastMCP dependency injection
    try:
        from fastmcp.server.dependencies import CurrentContext

        _current_context = CurrentContext()
    except Exception:
        _current_context = None  # type: ignore[assignment]

    # --- Plan tools ---

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_plan_status(cd: str | None = None) -> ToolResult:
        """
        Get current plan status: plan file path, approval state, last modified.
        Use when agent needs to know if a plan exists or where it is.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root", "remediation": "Set cwd or cd"}),
                structured_content={"error": "No project root", "remediation": "Set cwd or cd"},
                meta={"execution_time_ms": 0},
            )
        plans_dir = root / "docs" / "plans"
        plans = list(plans_dir.glob("*.md")) if plans_dir.exists() else []
        latest = max(plans, key=lambda p: p.stat().st_mtime) if plans else None
        elapsed = int((time.perf_counter() - start) * 1000)
        result = {
            "plans_dir": str(plans_dir),
            "plan_count": len(plans),
            "latest_plan": str(latest) if latest else None,
            "latest_modified": latest.stat().st_mtime if latest else None,
        }
        return ToolResult(
            content=json.dumps(result),
            structured_content=result,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_plan_get(plan_id: str | None = None, cd: str | None = None) -> ToolResult:
        """
        Get plan content by ID or path. If plan_id is a path, read it. Else find in docs/plans/.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        path = Path(plan_id) if plan_id else (root / "docs" / "plans")
        if not path.is_absolute():
            path = root / path
        if path.is_dir():
            plans = list(path.glob("*.md"))
            latest = max(plans, key=lambda p: p.stat().st_mtime) if plans else None
            path = latest or path
        from thegent.utils.helpers import read_file_optimized

        content = read_file_optimized(path)
        if content is None:
            return ToolResult(
                content=json.dumps({"error": "Failed to read plan", "path": str(path)}),
                structured_content={"error": "Failed to read plan", "path": str(path)},
                meta={"execution_time_ms": int((time.perf_counter() - start) * 1000)},
            )
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=content,
            structured_content={"path": str(path), "content": content},
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_plan_save(
        content: str,
        plan_id: str | None = None,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Save plan content to docs/plans/. plan_id becomes filename (e.g. PLAN_oauth2.md).
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        plans_dir = _ensure_dir(root / "docs" / "plans")
        name = plan_id or "PLAN"
        if not name.endswith(".md"):
            name = f"{name}.md"
        path = plans_dir / name
        path.write_text(content, encoding="utf-8")
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"path": str(path), "saved": True}),
            structured_content={"path": str(path), "saved": True},
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_plan_approve(
        plan_id: str,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Mark plan as approved. Writes approval marker (e.g. .approved) for downstream automation.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        plans_dir = root / "docs" / "plans"
        path = plans_dir / plan_id if not Path(plan_id).is_absolute() else Path(plan_id)
        if not path.exists():
            path = plans_dir / f"{plan_id}.md"
        marker = path.with_suffix(path.suffix + ".approved")
        marker.write_text("approved", encoding="utf-8")
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"plan_id": plan_id, "approved": True, "marker": str(marker)}),
            structured_content={"plan_id": plan_id, "approved": True, "marker": str(marker)},
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_plan_create(
        prompt: str,
        plan_id: str | None = None,
        brief_path: str | None = None,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Create a new plan file from a prompt. Writes a structured template to docs/plans/.
        Optionally reference brief_path (e.g. docs/briefs/ELICIT_xxx.md) for context.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        plans_dir = _ensure_dir(root / "docs" / "plans")
        slug = _slugify(plan_id or prompt)
        name = f"PLAN_{slug}.md"
        path = plans_dir / name

        # Build template from prompt
        brief = ""
        if brief_path:
            bp = root / brief_path if not Path(brief_path).is_absolute() else Path(brief_path)
            from thegent.utils.helpers import safe_read_file

            brief = safe_read_file(bp) or ""
        template = f"""# Plan: {prompt[:80]}{"..." if len(prompt) > 80 else ""}

## Context
{prompt}

## Brief (if provided)
{brief[:500] + "..." if len(brief) > 500 else brief or "(none)"}

## Approach
<!-- Define implementation steps here -->

## Tasks
- [ ]
- [ ]
- [ ]

## Risks / Notes
"""
        path.write_text(template, encoding="utf-8")
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"path": str(path), "plan_id": name, "created": True}),
            structured_content={"path": str(path), "plan_id": name, "created": True},
            meta={"execution_time_ms": elapsed},
        )

    # --- Protocol tools ---

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_protocol_list(cd: str | None = None) -> ToolResult:
        """
        List available protocols from .thegent/protocols/.
        Returns protocol names and modes (discussion, research, validation).
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root", "protocols": []}),
                structured_content={"error": "No project root", "protocols": []},
                meta={"execution_time_ms": 0},
            )
        protocols_dir = root / ".thegent" / "protocols"
        protocols = []
        if protocols_dir.exists():
            for p in protocols_dir.glob("*.md"):
                protocols.append({"name": p.stem, "path": str(p)})
            for p in protocols_dir.glob("*.yaml"):
                protocols.append({"name": p.stem, "path": str(p)})
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"protocols": protocols}),
            structured_content={"protocols": protocols},
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_protocol_get(
        mode: str | None = None,
        name: str | None = None,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Get protocol content by mode (discussion, research, validation) or name.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        protocols_dir = root / ".thegent" / "protocols"
        candidates = []
        if mode:
            candidates.extend(protocols_dir.glob(f"*{mode}*"))
        if name:
            candidates.extend(protocols_dir.glob(f"{name}*"))
        if not mode and not name:
            candidates = list(protocols_dir.glob("*.md")) + list(protocols_dir.glob("*.yaml"))
        path = candidates[0] if candidates else None
        from thegent.utils.helpers import read_file_optimized

        if path is None:
            return ToolResult(
                content=json.dumps({"error": "Protocol not found or empty", "mode": mode, "name": name}),
                structured_content={"error": "Protocol not found or empty", "mode": mode, "name": name},
                meta={"execution_time_ms": int((time.perf_counter() - start) * 1000)},
            )
        content = read_file_optimized(path)
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=content,
            structured_content={"path": str(path), "content": content},
            meta={"execution_time_ms": elapsed},
        )

    # --- Discussion (Elicitation) tools ---

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_discussion_finalize(
        brief_content: str,
        brief_id: str | None = None,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Save elicitation brief to docs/briefs/. Use after discussion/elicitation phase.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        briefs_dir = _ensure_dir(root / "docs" / "briefs")
        name = brief_id or "ELICIT"
        if not name.endswith(".md"):
            name = f"{name}.md"
        path = briefs_dir / name
        path.write_text(brief_content, encoding="utf-8")
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"path": str(path), "saved": True}),
            structured_content={"path": str(path), "saved": True},
            meta={"execution_time_ms": elapsed},
        )

    # --- Research tools ---

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_research_finalize(
        report_content: str,
        report_id: str | None = None,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Save research report to docs/research/. Use after research phase.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        research_dir = _ensure_dir(root / "docs" / "research")
        name = report_id or "RESEARCH"
        if not name.endswith(".md"):
            name = f"{name}.md"
        path = research_dir / name
        path.write_text(report_content, encoding="utf-8")
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"path": str(path), "saved": True}),
            structured_content={"path": str(path), "saved": True},
            meta={"execution_time_ms": elapsed},
        )

    # --- Validation tools ---

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_validation_report(
        cd: str | None = None,
        protocol: str | None = None,
    ) -> ToolResult:
        """
        Get validation report if one exists. Use after validation phase.
        protocol: optional protocol name to load checklist from.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root", "report": None}),
                structured_content={"error": "No project root", "report": None},
                meta={"execution_time_ms": 0},
            )
        validation_dir = root / "docs" / "validation"
        reports = list(validation_dir.glob("*.md")) if validation_dir.exists() else []
        latest = max(reports, key=lambda p: p.stat().st_mtime) if reports else None
        from thegent.utils.helpers import safe_read_file

        content = safe_read_file(latest) if latest else None
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"path": str(latest) if latest else None, "content": content}),
            structured_content={"path": str(latest) if latest else None, "content": content},
            meta={"execution_time_ms": elapsed},
        )

    # --- DAG tools ---

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_dag_ready(cd: str | None = None) -> ToolResult:
        """
        List DAG task IDs that are ready (pending with all deps Union[done, cancelled]|skipped).
        Use before thegent_dag_run to see what can be spawned.
        """
        start = time.perf_counter()
        from thegent.cli.commands.impl import dag_ready_impl

        res = dag_ready_impl(Path(cd) if cd else None)
        elapsed = int((time.perf_counter() - start) * 1000)
        if "error" in res:
            return ToolResult(
                content=json.dumps(res),
                structured_content=res,
                meta={"execution_time_ms": elapsed},
            )
        return ToolResult(
            content=json.dumps(res),
            structured_content=res,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def thegent_dag_run(
        cd: str | None = None,
        dry_run: bool = False,
        task: str | None = None,
        max_parallel: int | None = None,
        lane: str | None = None,
        ctx: Any = _current_context,
    ) -> ToolResult:
        """
        Spawn agents for ready DAG tasks. Use thegent_dag_ready first to see ready tasks.
        dry_run: list what would run without spawning. task: run only this task id.
        max_parallel: cap concurrent running tasks.
        """
        await _ctx_info(
            ctx,
            f"thegent_dag_run dry_run={dry_run} task={task} max_parallel={max_parallel} lane={lane}",
        )
        await ctx.report_progress(progress=0, total=2) if ctx is not None else None
        start = time.perf_counter()
        from thegent.cli.commands.impl import dag_run_impl

        res = dag_run_impl(
            cd=Path(cd) if cd else None,
            dry_run=dry_run,
            task=task,
            max_parallel=max_parallel,
            lane=lane,
        )
        elapsed = int((time.perf_counter() - start) * 1000)
        spawned = len(res.get("spawned", [])) if isinstance(res, dict) else 0
        await _ctx_info(ctx, f"thegent_dag_run spawned={spawned} elapsed={elapsed}ms")
        if ctx is not None:
            with contextlib.suppress(Exception):
                await ctx.report_progress(progress=2, total=2)
        return ToolResult(
            content=json.dumps(res),
            structured_content=res,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_dag_sync(cd: str | None = None, auto_run_next: bool = False) -> ToolResult:
        """
        Sync DAG task status from session exit (running -> done/failed).
        auto_run_next: spawn next ready tasks after sync (auto-spawn loop).
        """
        start = time.perf_counter()
        from thegent.cli.commands.impl import dag_sync_impl

        res = dag_sync_impl(cd=Path(cd) if cd else None, auto_run_next=auto_run_next)
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps(res),
            structured_content=res,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_dag_recover(cd: str | None = None, action: str = "retry-failed") -> ToolResult:
        """
        Perform recovery playbook actions on the DAG.
        action: retry-Union[failed, clear]-Union[stuck, reset]-Union[retries, fallback].
        """
        start = time.perf_counter()
        from thegent.cli.commands.impl import dag_recover_impl

        res = dag_recover_impl(cd=Path(cd) if cd else None, action=action)
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps(res),
            structured_content=res,
            meta={"execution_time_ms": elapsed},
        )

    # --- Team tools ---

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_team_create(
        prompt: str,
        mode: str = "normal",
        teammates: int = 1,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Create a team record for orchestration. mode: normal, discussion, research, plan, delegate, validation.
        Returns team_id. Use thegent_team_delegate to assign work to teammates.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        settings = ThegentSettings()
        teams_dir = _ensure_dir(settings.cache_dir / "teams")
        team_id = f"team-{uuid.uuid4().hex[:8]}"
        config_path = teams_dir / team_id / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {
            "team_id": team_id,
            "prompt": prompt,
            "mode": mode,
            "teammates": teammates,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"team_id": team_id, "config": config}),
            structured_content={"team_id": team_id, "config": config},
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_team_list(cd: str | None = None) -> ToolResult:
        """
        List teams and delegations. Returns active teams and TeammateManager delegations.
        """
        start = time.perf_counter()
        settings = ThegentSettings()
        teams_dir = settings.cache_dir / "teams"
        teams = []
        if teams_dir.exists():
            for d in teams_dir.iterdir():
                if d.is_dir():
                    cfg = d / "config.json"
                    if cfg.exists():
                        try:
                            teams.append(json.loads(cfg.read_text()))
                        except json.JSONDecodeError:
                            teams.append({"team_id": d.name, "error": "invalid config"})
        delegations = []
        try:
            from thegent.governance.teammates import TeammateManager

            tm = TeammateManager(settings.cache_dir / "teammates.json")
            for d in tm.get_delegations():
                delegations.append(
                    {"id": d.id, "teammate_id": d.teammate_id, "status": d.status, "prompt": d.prompt[:80]}
                )
        except Exception as e:
            _log.debug("TeammateManager: %s", e)
        elapsed = int((time.perf_counter() - start) * 1000)
        result = {"teams": teams, "delegations": delegations}
        return ToolResult(
            content=json.dumps(result),
            structured_content=result,
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_team_delegate(
        teammate_id: str,
        prompt: str,
        parent_run_id: str | None = None,
    ) -> ToolResult:
        """
        Delegate a task to a teammate. Uses TeammateManager. teammate_id from agents/*.md.
        """
        start = time.perf_counter()
        settings = ThegentSettings()
        try:
            from thegent.governance.teammates import TeammateManager

            tm = TeammateManager(settings.cache_dir / "teammates.json")
            parent_id = parent_run_id or f"mcp-{uuid.uuid4().hex[:8]}"
            req = tm.delegate(teammate_id, parent_id, prompt)
            elapsed = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                content=json.dumps(
                    {
                        "delegation_id": req.id,
                        "teammate_id": teammate_id,
                        "status": req.status,
                        "parent_run_id": parent_id,
                    }
                ),
                structured_content={
                    "delegation_id": req.id,
                    "teammate_id": teammate_id,
                    "status": req.status,
                    "parent_run_id": parent_id,
                },
                meta={"execution_time_ms": elapsed},
            )
        except Exception as e:
            return ToolResult(
                content=json.dumps({"error": str(e), "remediation": "Run: thegent teammates list"}),
                structured_content={"error": str(e), "remediation": "Run: thegent teammates list"},
                meta={"execution_time_ms": int((time.perf_counter() - start) * 1000)},
            )

    # --- Discussion session tools ---

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_discussion_start(
        topic: str,
        cd: str | None = None,
    ) -> ToolResult:
        """
        Start a discussion/elicitation session. Returns session_id for thegent_discussion_add_question.
        """
        start = time.perf_counter()
        root = _get_project_root(Path(cd) if cd else None)
        if not root:
            return ToolResult(
                content=json.dumps({"error": "No project root"}),
                structured_content={"error": "No project root"},
                meta={"execution_time_ms": 0},
            )
        settings = ThegentSettings()
        sessions_dir = _ensure_dir(settings.cache_dir / "discussions")
        session_id = f"disc-{uuid.uuid4().hex[:8]}"
        session_path = sessions_dir / f"{session_id}.json"
        session = {
            "session_id": session_id,
            "topic": topic,
            "questions": [],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        session_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"session_id": session_id, "topic": topic}),
            structured_content={"session_id": session_id, "topic": topic},
            meta={"execution_time_ms": elapsed},
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_discussion_add_question(
        session_id: str,
        question: str,
        answer: str | None = None,
    ) -> ToolResult:
        """
        Add a question (and optional answer) to a discussion session.
        Use after thegent_discussion_start. Call thegent_discussion_finalize to save the brief.
        """
        start = time.perf_counter()
        settings = ThegentSettings()
        sessions_dir = settings.cache_dir / "discussions"
        session_path = sessions_dir / f"{session_id}.json"
        if not session_path.exists():
            return ToolResult(
                content=json.dumps({"error": "Session not found", "session_id": session_id}),
                structured_content={"error": "Session not found", "session_id": session_id},
                meta={"execution_time_ms": int((time.perf_counter() - start) * 1000)},
            )
        session = json.loads(session_path.read_text())
        session.setdefault("questions", []).append({"question": question, "answer": answer})
        session_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
        elapsed = int((time.perf_counter() - start) * 1000)
        return ToolResult(
            content=json.dumps({"session_id": session_id, "question_count": len(session["questions"])}),
            structured_content={"session_id": session_id, "question_count": len(session["questions"])},
            meta={"execution_time_ms": elapsed},
        )

    _ = (
        thegent_plan_status,
        thegent_plan_get,
        thegent_plan_save,
        thegent_plan_approve,
        thegent_plan_create,
        thegent_protocol_list,
        thegent_protocol_get,
        thegent_discussion_finalize,
        thegent_research_finalize,
        thegent_validation_report,
        thegent_dag_ready,
        thegent_dag_run,
        thegent_dag_sync,
        thegent_dag_recover,
        thegent_team_create,
        thegent_team_list,
        thegent_team_delegate,
        thegent_discussion_start,
        thegent_discussion_add_question,
    )
    _log.info(
        "registered mode tools: plan_*, protocol_*, discussion_*, research_finalize, validation_report, dag_ready/run/sync, team_*"
    )
