"""Unit tests for WP-1001: Dependency-aware routing engine."""

import pytest

from thegent.orchestration.execution.router import DependencyRouter


def test_router_single_task():
    """Router handles a single task with no dependencies."""
    tasks = [{"id": "A"}]
    router = DependencyRouter.from_tasks(tasks)

    ready = router.get_ready_tasks()
    assert ready == ("A",)

    router.mark_started("A")
    router.mark_completed("A")
    assert router.is_finished() is True


def test_router_sequential_tasks():
    """Router handles tasks in sequence."""
    tasks = [
        {"id": "A"},
        {"id": "B", "depends_on": ["A"]},
    ]
    router = DependencyRouter.from_tasks(tasks)

    # Only A is ready
    assert router.get_ready_tasks() == ("A",)

    router.mark_completed("A")

    # Now B is ready
    assert router.get_ready_tasks() == ("B",)

    router.mark_completed("B")
    assert router.is_finished() is True


def test_router_parallel_tasks():
    """Router handles parallel tasks."""
    tasks = [
        {"id": "A"},
        {"id": "B", "depends_on": ["A"]},
        {"id": "C", "depends_on": ["A"]},
        {"id": "D", "depends_on": ["B", "C"]},
    ]
    router = DependencyRouter.from_tasks(tasks)

    assert router.get_ready_tasks() == ("A",)
    router.mark_completed("A")

    # B and C are ready
    ready = sorted(router.get_ready_tasks())
    assert ready == ["B", "C"]

    router.mark_completed("B")
    # D is not ready yet (waiting for C)
    assert router.get_ready_tasks() == ()

    router.mark_completed("C")
    assert router.get_ready_tasks() == ("D",)

    router.mark_completed("D")
    assert router.is_finished() is True


def test_router_invalid_dag():
    """Router raises error for cycles or invalid DAGs."""
    tasks = [
        {"id": "A", "depends_on": ["B"]},
        {"id": "B", "depends_on": ["A"]},
    ]
    with pytest.raises(Exception):
        DependencyRouter.from_tasks(tasks)
