"""DAG-based remediation plan generation.

Converts prioritised findings from the analyzer into an executable DAG of
remediation tasks that the agent deployer can dispatch.  Uses
``graphlib.TopologicalSorter`` (stdlib) for DAG resolution and reuses the
PERT forward-pass from ``thegent.planning.simulation`` for critical-path
estimation.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from graphlib import TopologicalSorter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
else:
    Path = str  # runtime-only placeholder for type checkers
from typing import TYPE_CHECKING
from uuid import uuid4

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from thegent.governance.analyzer import Finding
else:

    class Finding:  # runtime shim for type checkers only
        finding_id: str
        dimension: str
        estimated_effort_tool_calls: int
        affected_files: list[str]
        description: str
        delta: float


from thegent.planning.simulation import PERTNode, pert_forward_pass

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# dimension -> (agent_role, prompt_template)
# ---------------------------------------------------------------------------

_DIMENSION_CONFIG: dict[str, tuple[str, str]] = {
    "test_coverage": (
        "writer_fast",
        "Write tests for {files} to improve coverage",
    ),
    "lint_violations": (
        "writer_fast",
        "Fix lint errors in {files}",
    ),
    "technical_debt": (
        "writer_standard",
        "Refactor {files} to reduce cyclomatic complexity below 10",
    ),
    "security_findings": (
        "mission_critical",
        "Fix security vulnerability: {description}",
    ),
    "doc_disorganization": (
        "writer_fast",
        "Organize documentation files into correct directories",
    ),
    "fragmented_research": (
        "writer_fast",
        "Organize documentation files into correct directories",
    ),
    "missing_specs": (
        "planner",
        "Generate FR traceability for untested requirements",
    ),
    "stale_items": (
        "workhorse",
        "Update stale items: {items}",
    ),
    "agent_failure": (
        "researcher",
        "Diagnose and resolve agent failures: {agents}",
    ),
}

# Dimensions that must complete before others can start.
_ORDERING_RULES: list[tuple[str, str]] = [
    # security before everything else (handled specially below)
    ("lint_violations", "test_coverage")(  # lint fix before test writing
        "technical_debt", "test_coverage"
    )  # complexity refactoring before test writing
]


# ---------------------------------------------------------------------------
# models
# ---------------------------------------------------------------------------


class RemediationTask(BaseModel):
    """A single task in a remediation plan."""

    task_id: str = Field(default_factory=lambda: f"rt_{uuid4().hex[:8]}")
    finding_id: str
    dimension: str = ""
    agent_type: str = "claude"
    agent_role: str = "workhorse"
    prompt_template: str = ""
    dependencies: list[str] = Field(default_factory=list)
    estimated_cost_calls: int = 1
    verification_criteria: dict[str, float] = Field(default_factory=dict)
    priority: int = 0


class RemediationPlan(BaseModel):
    """An executable DAG of remediation tasks."""

    plan_id: str = Field(default_factory=lambda: f"rp_{uuid4().hex[:8]}")
    cycle_id: str = ""
    tasks: list[RemediationTask] = Field(default_factory=list)
    dag_edges: dict[str, list[str]] = Field(default_factory=dict)
    critical_path: list[str] = Field(default_factory=list)
    total_estimated_calls: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# ---------------------------------------------------------------------------
# planner
# ---------------------------------------------------------------------------


class RemediationPlanner:
    """Converts findings into an executable remediation DAG."""

    def __init__(self, health_targets_path: Path) -> None:
        import json

        with open(health_targets_path) as fh:
            data = json.load(fh)
        self._targets: dict[str, dict] = data["dimensions"]

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def plan(
        self,
        findings: list[Finding],
        budget_remaining_calls: int,
    ) -> RemediationPlan:
        """Build a remediation plan from *findings* within *budget*."""
        tasks = self._generate_tasks(findings)
        dag_edges = self._build_dag(tasks)

        # validate the DAG is acyclic (TopologicalSorter raises on cycles)
        ts = TopologicalSorter(dag_edges)
        ts.prepare()

        critical_path = self._compute_critical_path(tasks, dag_edges)

        # trim tasks that exceed the remaining budget
        included: list[RemediationTask] = []
        remaining = budget_remaining_calls
        for task in tasks:
            if task.estimated_cost_calls <= remaining:
                included.append(task)
                remaining -= task.estimated_cost_calls

        total = sum(t.estimated_cost_calls for t in included)

        return RemediationPlan(
            tasks=included,
            dag_edges=dag_edges,
            critical_path=critical_path,
            total_estimated_calls=total,
        )

    # ------------------------------------------------------------------
    # task generation
    # ------------------------------------------------------------------

    def _generate_tasks(self, findings: list[Finding]) -> list[RemediationTask]:
        """Create one RemediationTask per finding, ordered by priority."""
        tasks: list[RemediationTask] = []
        for idx, finding in enumerate(findings):
            cfg = _DIMENSION_CONFIG.get(finding.dimension)
            if cfg is None:
                _log.warning("no remediation config for dimension %r", finding.dimension)
                continue

            agent_role, prompt_tpl = cfg
            prompt = self._render_prompt(prompt_tpl, finding)

            tasks.append(
                RemediationTask(
                    finding_id=finding.finding_id,
                    dimension=finding.dimension,
                    agent_role=agent_role,
                    prompt_template=prompt,
                    estimated_cost_calls=finding.estimated_effort_tool_calls,
                    verification_criteria={
                        finding.dimension: finding.delta,
                    },
                    priority=len(findings) - idx,
                ),
            )
        return tasks

    # ------------------------------------------------------------------
    # DAG construction
    # ------------------------------------------------------------------

    def _build_dag(self, tasks: list[RemediationTask]) -> dict[str, list[str]]:
        """Build dependency edges between tasks.

        Rules:
        - Security tasks must complete before all other tasks.
        - Lint fixes before test writing.
        - Complexity refactoring before test writing.
        """
        by_dimension: dict[str, list[str]] = {}
        for t in tasks:
            by_dimension.setdefault(t.dimension, []).append(t.task_id)

        edges: dict[str, list[str]] = {t.task_id: [] for t in tasks}

        # security_findings -> everything else
        security_ids = by_dimension.get("security_findings", [])
        if security_ids:
            for t in tasks:
                if t.dimension != "security_findings":
                    for sec_id in security_ids:
                        if sec_id not in edges[t.task_id]:
                            edges[t.task_id].append(sec_id)

        # explicit ordering rules
        for before_dim, after_dim in _ORDERING_RULES:
            before_ids = by_dimension.get(before_dim, [])
            after_ids = by_dimension.get(after_dim, [])
            for after_id in after_ids:
                for before_id in before_ids:
                    if before_id not in edges[after_id]:
                        edges[after_id].append(before_id)

        # write back dependencies to task objects
        task_map = {t.task_id: t for t in tasks}
        for tid, deps in edges.items():
            task_map[tid].dependencies = deps

        return edges

    # ------------------------------------------------------------------
    # critical path
    # ------------------------------------------------------------------

    def _compute_critical_path(
        self,
        tasks: list[RemediationTask],
        dag_edges: dict[str, list[str]],
    ) -> list[str]:
        """Compute the critical path using PERT forward pass."""
        if not tasks:
            return []

        nodes = [
            PERTNode(
                task_id=t.task_id,
                optimistic_days=float(t.estimated_cost_calls) * 0.5,
                most_likely_days=float(t.estimated_cost_calls),
                pessimistic_days=float(t.estimated_cost_calls) * 2.0,
                predecessors=dag_edges.get(t.task_id, []),
            )
            for t in tasks
        ]

        pert_results = pert_forward_pass(nodes)

        # topological order, then pick the longest-duration chain
        ts = TopologicalSorter(dag_edges)
        topo_order = list(ts.static_order())

        # forward pass: earliest finish for each task
        earliest_finish: dict[str, float] = {}
        for tid in topo_order:
            if tid not in pert_results:
                continue
            pred_max = 0.0
            for dep in dag_edges.get(tid, []):
                if dep in earliest_finish:
                    pred_max = max(pred_max, earliest_finish[dep])
            earliest_finish[tid] = pred_max + pert_results[tid].expected_duration

        if not earliest_finish:
            return []

        # the critical path ends at the task with the latest finish
        project_end = max(earliest_finish.values())

        # backward pass: latest finish
        latest_finish: dict[str, float] = dict.fromkeys(earliest_finish, project_end)
        for tid in reversed(topo_order):
            if tid not in pert_results:
                continue
            for dep in dag_edges.get(tid, []):
                if dep in latest_finish:
                    candidate = latest_finish[tid] - pert_results[tid].expected_duration
                    latest_finish[dep] = min(latest_finish[dep], candidate)

        # critical = tasks with zero float
        critical = [
            tid
            for tid in topo_order
            if tid in earliest_finish and abs(latest_finish[tid] - earliest_finish[tid]) < 1e-9
        ]
        return critical

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _render_prompt(template: str, finding: Finding) -> str:
        """Fill prompt template placeholders from *finding*."""
        files_str = ", ".join(finding.affected_files) if finding.affected_files else "affected modules"
        return template.format(
            files=files_str,
            description=finding.description,
            items=files_str,
            agents=files_str,
        )
