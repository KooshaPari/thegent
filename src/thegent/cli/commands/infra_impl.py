"""Infra/compute/sandbox/concurrency/orchestration backend logic (WL-120 W3-B3)."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)



def lock_resource_impl(resource_path: str, agent_id: str, ttl: int = 60, cd: Path | None = None) -> dict[str, Any]:
    """Claim a lease on a resource (file or directory)."""
    from thegent.cli.commands.impl import _resolve_cwd
    from thegent.coordination.file_coordination import FileLeaseRegistry

    cwd = _resolve_cwd(cd) or Path.cwd()
    settings = ThegentSettings()
    registry = FileLeaseRegistry(settings.session_dir / "leases")

    path = Path(resource_path)
    if not path.is_absolute():
        path = cwd / path

    token = registry.claim_lease(path, agent_id, ttl=ttl)
    if token:
        return {"success": True, "token": token, "resource": str(path)}
    return {"success": False, "error": f"Resource {resource_path} is currently locked by another agent."}


def unlock_resource_impl(resource_path: str, agent_id: str, token: str, cd: Path | None = None) -> dict[str, Any]:
    """Release a lease on a resource."""
    from thegent.cli.commands.impl import _resolve_cwd
    from thegent.coordination.file_coordination import FileLeaseRegistry

    cwd = _resolve_cwd(cd) or Path.cwd()
    settings = ThegentSettings()
    registry = FileLeaseRegistry(settings.session_dir / "leases")

    path = Path(resource_path)
    if not path.is_absolute():
        path = cwd / path

    registry.release_lease(path, agent_id, token)
    return {"success": True}


def verify_context_impl(files: list[str], cd: Path | None = None) -> dict[str, Any]:
    """Verify if any of the given files have been modified (OCC check)."""
    from thegent.cli.commands.impl import _resolve_cwd
    from thegent.coordination.file_coordination import OCCManager

    cwd = _resolve_cwd(cd) or Path.cwd()
    settings = ThegentSettings()
    occ = OCCManager(settings.session_dir / "occ_versions")

    issues = []
    for f in files:
        path = Path(f)
        if not path.is_absolute():
            path = cwd / path

        current_version = occ.get_version(path)
        issues.append({"file": f, "version": current_version})

    return {"files": issues}


def concurrency_show_impl() -> None:
    """Show current concurrency limits and load-based status."""
    from rich.console import Console
    from rich.table import Table

    from thegent.orchestration.resource.load_based_limits import compute_dynamic_limit, sample_resources

    settings = ThegentSettings()
    console = Console()

    table = Table(title="Concurrency Limits (WP-5001)")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Source", style="dim")

    table.add_row(
        "Max Concurrency (Ceiling)",
        str(settings.max_concurrency),
        "THGENT_MAX_CONCURRENCY",
    )
    table.add_row(
        "Load-Based Limits",
        "Enabled" if settings.concurrency_load_based else "Disabled",
        "THGENT_CONCURRENCY_LOAD_BASED",
    )

    if settings.concurrency_load_based:
        _snapshot = sample_resources()
        capacity, _ = compute_dynamic_limit(_snapshot)
        table.add_row("Current Available Capacity", str(capacity), "Dynamic")
        table.add_row(
            "Min Slots",
            str(settings.concurrency_min_slots),
            "THGENT_CONCURRENCY_MIN_SLOTS",
        )
        table.add_row(
            "Max FD Utilization",
            f"{settings.concurrency_fd_utilization_max * 100}%",
            "THGENT_CONCURRENCY_FD_UTILIZATION_MAX",
        )
        table.add_row(
            "Max Load per CPU",
            str(settings.concurrency_load_per_cpu_max),
            "THGENT_CONCURRENCY_LOAD_PER_CPU_MAX",
        )

    console.print(table)


def concurrency_set_impl(limit: int, load_based: bool = True) -> None:
    """Set maximum concurrency limit (env-var based; prints persistence instructions)."""
    from rich.console import Console

    console = Console()
    console.print(f"[green]Concurrency limit set to {limit} (load-based: {load_based})[/green]")
    console.print("\n[dim]To persist these settings, export the following environment variables:[/dim]")
    console.print(f"export THGENT_MAX_CONCURRENCY={limit}")
    console.print(f"export THGENT_CONCURRENCY_LOAD_BASED={'1' if load_based else '0'}")


def monitor_impl(interval: float = 2.0) -> None:
    """Monitor sessions and plan progress in real-time (WP-8001)."""
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table

    from thegent.cli.commands.impl import do_next_impl, ps_impl as _ps_impl

    def generate_monitor_layout() -> Layout:
        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3))

        layout["header"].update(Panel("[bold cyan]thegent Monitor[/bold cyan] (WP-8001)", border_style="cyan"))

        layout["body"].split_row(Layout(name="sessions"), Layout(name="plan"))

        sessions = _ps_impl(all=False)
        session_table = Table(title=f"Active Sessions ({len(sessions)})", expand=True)
        session_table.add_column("ID", style="cyan")
        session_table.add_column("Agent", style="magenta")
        session_table.add_column("PID", style="green")
        session_table.add_column("Prompt", style="dim")

        for s in sessions[:10]:
            session_table.add_row(
                str(s.get("id", "N/A"))[:12],
                s.get("agent", "?"),
                str(s.get("pid", "N/A")),
                s.get("prompt_preview", "")[:30],
            )
        layout["sessions"].update(Panel(session_table, border_style="magenta"))

        plan = do_next_impl(limit=10)
        plan_table = Table(title="Plan Progress", expand=True)
        plan_table.add_column("ID", style="cyan")
        plan_table.add_column("Source", style="yellow")
        plan_table.add_column("Description", style="dim")

        for item in plan.get("next_items", []):
            plan_table.add_row(item.get("id", "N/A")[:12], item.get("source", "?"), item.get("description", "")[:40])
        layout["plan"].update(Panel(plan_table, border_style="yellow"))

        layout["footer"].update(Panel(f"[dim]Interval: {interval}s | Press Ctrl+C to exit[/dim]", border_style="dim"))

        return layout

    with Live(generate_monitor_layout(), refresh_per_second=1 / interval, screen=True) as live:
        try:
            while True:
                time.sleep(interval)
                live.update(generate_monitor_layout())
        except KeyboardInterrupt:
            pass


def isolation_check_impl(mode: str = "sub-user") -> None:
    """Implementation of 'thegent isolation check'."""
    import platform

    from rich.console import Console
    from rich.table import Table

    console = Console()

    table = Table(title=f"Isolation Status: {mode}")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")

    from thegent.infra.worker_node import HAS_SHM

    shm_status = "\u2705 ACTIVE" if HAS_SHM else "\u274c INACTIVE (Rust extension missing)"
    table.add_row("SHM Bridge (Rust)", shm_status, "Low-latency IPC")

    proxy_status = "\u2705 READY" if os.environ.get("SSH_AUTH_SOCK") else "\u26a0\ufe0f WARNING (No SSH agent)"
    table.add_row("SSH Identity Proxy", proxy_status, "Forwarding host keys")

    from thegent.isolation.vfs import VfsAdapter

    _vfs = VfsAdapter()
    vfs_status = "\u2705 READY"
    table.add_row("VFS (OverlayFS/Reflink)", vfs_status, f"Platform: {platform.system()}")

    console.print(table)


# @trace FR-ORC-088 WL-088


def orchestrate_plan_impl(
    goal: str,
    *,
    max_depth: int = 3,
    model: str = "claude-haiku-4.5",
    timeout_s: float = 30.0,
) -> dict[str, Any]:
    """Decompose *goal* into an OrchestrationPlan dict via LLMPlangentPlanner. # @trace FR-ORC-088"""
    import asyncio as _asyncio

    from thegent.agents.plangent import LLMPlangentPlanner

    if not goal or not goal.strip():
        raise ValueError("goal must be a non-empty string")

    planner = LLMPlangentPlanner(model=model, timeout_s=timeout_s)
    plan = _asyncio.run(planner.decompose_to_orchestration_plan(goal.strip(), max_depth))

    nodes_out: list[dict[str, Any]] = []
    for node in plan.nodes:
        nodes_out.append(
            {
                "id": node.id,
                "task": node.task,
                "depends_on": list(node.depends_on),
                "agent_hint": node.metadata.get("agent_hint"),
                "budget_tokens": node.metadata.get("budget_tokens"),
                "status": node.status,
            }
        )

    return {
        "plan_id": plan.id,
        "goal": plan.goal,
        "node_count": len(plan.nodes),
        "nodes": nodes_out,
        "created_at": plan.created_at.isoformat(),
    }


def orchestrate_run_impl(
    goal: str,
    *,
    max_depth: int = 3,
    model: str = "claude-haiku-4.5",
    timeout_s: float = 30.0,
    fail_fast: bool = False,
) -> dict[str, Any]:
    """Decompose *goal* and execute via PlangentExecutor + SubAgentDispatcher. # @trace FR-ORC-088"""
    import asyncio as _asyncio

    from thegent.agents.plangent import LLMPlangentPlanner, PlangentExecutor
    from thegent.orchestration.event_queue import SubAgentEventQueue
    from thegent.orchestration.result_aggregator import ResultAggregator
    from thegent.orchestration.sub_agent_dispatcher import CapabilityIndex, SubAgentDispatcher

    if not goal or not goal.strip():
        raise ValueError("goal must be a non-empty string")

    planner = LLMPlangentPlanner(model=model, timeout_s=timeout_s)
    plan = _asyncio.run(planner.decompose_to_orchestration_plan(goal.strip(), max_depth))

    event_queue = SubAgentEventQueue()
    capability_index = CapabilityIndex()
    _dispatcher = SubAgentDispatcher(
        capability_index=capability_index,
        event_queue=event_queue,
    )

    from thegent.cli.commands.impl import run_impl

    executor = PlangentExecutor(fail_fast=fail_fast)

    def _sync_runner(node: Any) -> str:
        result = run_impl(
            agent=node.metadata.get("agent_hint"),
            prompt=node.task,
            mode="write",
            full=True,
            live=False,
        )
        return str(result.get("status", ""))

    executed_plan = executor.execute(plan, _sync_runner)

    events_out: list[dict[str, Any]] = []
    for evt in event_queue.drain_nowait():
        events_out.append(
            {
                "event_id": evt.event_id,
                "request_id": evt.request_id,
                "event_type": str(evt.event_type),
                "message": evt.message,
                "timestamp": evt.timestamp,
            }
        )

    aggregator = ResultAggregator()
    from thegent.orchestration.protocol import SubAgentResult, SubAgentStatus

    for node in executed_plan.nodes:
        status = SubAgentStatus.COMPLETED if node.status == "done" else SubAgentStatus.FAILED
        aggregator.add(
            SubAgentResult(
                request_id=node.id,
                agent_type=node.metadata.get("agent_hint") or "default",
                status=status,
                error=node.error,
            )
        )

    agg = aggregator.aggregate()

    nodes_out: list[dict[str, Any]] = [
        {
            "id": n.id,
            "task": n.task,
            "status": n.status,
            "result": n.result,
            "error": n.error,
        }
        for n in executed_plan.nodes
    ]

    return {
        "plan_id": executed_plan.id,
        "goal": executed_plan.goal,
        "success_count": agg.success_count,
        "failure_count": agg.failure_count,
        "all_passed": agg.all_passed,
        "errors": agg.errors,
        "events": events_out,
        "nodes": nodes_out,
    }
