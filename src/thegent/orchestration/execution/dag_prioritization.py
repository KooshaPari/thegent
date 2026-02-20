"""DAG-aware critical-path task prioritization for swarm scheduling.

Computes the critical path through a directed acyclic graph (DAG) of tasks
and surfaces priority scores so the swarm scheduler can schedule the most
blocking work first.

Usage::

    from thegent.orchestration.execution.dag_prioritization import DagPrioritizer, DagTask

    p = DagPrioritizer()
    p.add_task(DagTask("a", estimated_duration_s=3.0))
    p.add_task(DagTask("b", estimated_duration_s=5.0, dependencies=["a"]))
    p.add_task(DagTask("c", estimated_duration_s=2.0, dependencies=["a"]))

    critical = p.compute_critical_path()   # ["a", "b"]
    order    = p.topological_sort()        # valid execution order
    ready    = p.ready_tasks(completed=set())   # ["a"]
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public exceptions
# ---------------------------------------------------------------------------


class DagCycleError(Exception):
    """Raised when the task graph contains a cycle."""


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class DagTask:
    """A single node in the scheduling DAG."""

    task_id: str
    estimated_duration_s: float = 1.0
    dependencies: list[str] = field(default_factory=list)
    priority: int = 0


# ---------------------------------------------------------------------------
# Core prioritizer
# ---------------------------------------------------------------------------


class DagPrioritizer:
    """Compute critical paths and priority scores for a DAG of tasks.

    All methods are synchronous and read-only after tasks are added.
    The internal graph is rebuilt lazily when :meth:`compute_critical_path`
    or :meth:`topological_sort` is called.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, DagTask] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_task(self, task: DagTask) -> None:
        """Register *task* with the prioritizer.

        Duplicate ``task_id`` values overwrite the previous entry.
        """
        self._tasks[task.task_id] = task

    # ------------------------------------------------------------------
    # Graph utilities (internal)
    # ------------------------------------------------------------------

    def _validate_all_deps_known(self) -> None:
        """Raise ValueError if any dependency references an unknown task."""
        for task in self._tasks.values():
            for dep in task.dependencies:
                if dep not in self._tasks:
                    raise ValueError(f"Task '{task.task_id}' depends on unknown task '{dep}'")

    def _kahn_sort(self) -> list[str]:
        """Return a topological ordering via Kahn's algorithm.

        Raises :class:`DagCycleError` if the graph contains a cycle.
        Stable: ties broken by ``task_id`` for determinism.
        """
        # Build in-degree map and adjacency list (dependant → successors).
        in_degree: dict[str, int] = dict.fromkeys(self._tasks, 0)
        successors: dict[str, list[str]] = {tid: [] for tid in self._tasks}

        for task in self._tasks.values():
            for dep in task.dependencies:
                successors[dep].append(task.task_id)
                in_degree[task.task_id] += 1

        # Initialise queue with zero-in-degree nodes (sorted for stability).
        queue: deque[str] = deque(sorted(k for k, v in in_degree.items() if v == 0))
        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for succ in sorted(successors[node]):
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        if len(order) != len(self._tasks):
            raise DagCycleError("Cycle detected in task graph; topological sort is not possible.")

        return order

    def _compute_earliest_finish(self, topo_order: list[str]) -> dict[str, float]:
        """Compute earliest finish time for each task (forward pass).

        earliest_finish[t] = sum of durations along the longest path
        ending at *t* (inclusive).
        """
        ef: dict[str, float] = {}
        for tid in topo_order:
            task = self._tasks[tid]
            if not task.dependencies:
                ef[tid] = task.estimated_duration_s
            else:
                max_dep_ef = max(ef[dep] for dep in task.dependencies)
                ef[tid] = max_dep_ef + task.estimated_duration_s
        return ef

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def topological_sort(self) -> list[str]:
        """Return a valid execution order respecting all dependencies.

        Raises :class:`DagCycleError` if the graph contains a cycle.
        Raises :class:`ValueError` if any dependency references an unknown task.
        """
        self._validate_all_deps_known()
        return self._kahn_sort()

    def compute_critical_path(self) -> list[str]:
        """Return the ordered list of task IDs on the critical path.

        The critical path is the longest path (by total ``estimated_duration_s``)
        from any source node to any sink node.  The returned list is ordered
        from the first task to execute to the last.

        Raises :class:`DagCycleError` if the graph contains a cycle.
        Raises :class:`ValueError` if any dependency references an unknown task.
        """
        if not self._tasks:
            return []

        self._validate_all_deps_known()
        topo_order = self._kahn_sort()
        ef = self._compute_earliest_finish(topo_order)

        # The critical path ends at the task with the maximum earliest-finish time.
        # Tiebreak by task_id for determinism.
        sink = max(self._tasks, key=lambda tid: (ef[tid], tid))

        # Trace back from sink to source following the dependency that gave us
        # the maximum finish time at each step.
        path: list[str] = []
        current: str | None = sink
        while current is not None:
            path.append(current)
            task = self._tasks[current]
            if not task.dependencies:
                break
            # The predecessor on the critical path is the one with the highest
            # earliest-finish time (it is the bottleneck).
            current = max(task.dependencies, key=lambda dep: (ef[dep], dep))

        path.reverse()
        return path

    def get_priority_score(self, task_id: str) -> float:
        """Return a priority score for *task_id*.

        Higher values indicate that the task is on (or close to) the critical
        path.  The score equals the ``estimated_duration_s`` of the longest
        path that passes *through* this task — that is, the sum of the
        critical sub-path from this task to any sink.

        Raises :class:`KeyError` if *task_id* is not registered.
        Raises :class:`DagCycleError` if the graph contains a cycle.
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task '{task_id}' is not registered.")

        if len(self._tasks) == 1:
            return self._tasks[task_id].estimated_duration_s

        self._validate_all_deps_known()
        topo_order = self._kahn_sort()
        ef = self._compute_earliest_finish(topo_order)

        # Compute "latest start" for each task via a backward pass.
        # latest_start[t] = project_makespan - latest_finish[t]
        # latest_finish[t] = min over all successors s of (latest_finish[s] - dur[s])
        #                     (or project_makespan if t is a sink)
        project_makespan = max(ef.values())

        # Map task → its successors
        successors: dict[str, list[str]] = {tid: [] for tid in self._tasks}
        for task in self._tasks.values():
            for dep in task.dependencies:
                successors[dep].append(task.task_id)

        # Latest finish initialised to project_makespan for sinks.
        # Standard CPM backward pass:
        #   lf[sink] = project_makespan
        #   lf[t]    = min(lf[s] - dur[s])  for each successor s
        # Total float = lf[t] - ef[t]  (zero on critical path).
        lf: dict[str, float] = dict.fromkeys(self._tasks, project_makespan)

        for tid in reversed(topo_order):
            if successors[tid]:
                lf[tid] = min(lf[succ] - self._tasks[succ].estimated_duration_s for succ in successors[tid])

        # Priority score = project_makespan - total_float.
        # A task on the critical path has zero total float → score = project_makespan.
        # Off-critical tasks have positive float → lower score.
        total_float = lf[task_id] - ef[task_id]
        return project_makespan - total_float

    def ready_tasks(self, completed: set[str]) -> list[str]:
        """Return tasks whose dependencies are all satisfied, sorted by priority.

        *completed* is the set of already-finished ``task_id`` values.  Tasks
        in *completed* are excluded from the result.

        Tasks are returned in descending priority order (highest
        :meth:`get_priority_score` first); ties are broken by ``task_id``.

        Raises :class:`DagCycleError` if the graph contains a cycle.
        """
        if not self._tasks:
            return []

        self._validate_all_deps_known()
        # Compute priority scores once (triggers cycle check internally).
        topo_order = self._kahn_sort()
        ef = self._compute_earliest_finish(topo_order)
        project_makespan = max(ef.values()) if ef else 0.0

        successors: dict[str, list[str]] = {tid: [] for tid in self._tasks}
        for task in self._tasks.values():
            for dep in task.dependencies:
                successors[dep].append(task.task_id)

        # Standard CPM backward pass: lf[t] = min(lf[s] - dur[s]) for successors s.
        lf: dict[str, float] = dict.fromkeys(self._tasks, project_makespan)
        for tid in reversed(topo_order):
            if successors[tid]:
                lf[tid] = min(lf[succ] - self._tasks[succ].estimated_duration_s for succ in successors[tid])

        def _score(tid: str) -> float:
            total_float = lf[tid] - ef[tid]
            return project_makespan - total_float

        candidates = [
            tid
            for tid, task in self._tasks.items()
            if tid not in completed and all(dep in completed for dep in task.dependencies)
        ]

        return sorted(candidates, key=lambda tid: (-_score(tid), tid))
