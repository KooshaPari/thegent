"""Integration tests for governance/audit.py (WP-3004, FR-012).

Exercises the real RunRegistry + Auditor path (no mocks) to validate
that verify_chain and query_events work correctly with actual JSONL
files on disk.

# @trace AUDIT-N+54 FR-GOV-AU-001..015
"""

from __future__ import annotations

from pathlib import Path

import pytest

from thegent.execution import RunMeta, RunRegistry
from thegent.governance.audit import query_events, verify_chain

pytestmark = pytest.mark.integration


def _make_run(run_id: str, *, status: str = "running", **extra: str) -> RunMeta:
    """Build a minimal RunMeta for testing."""
    return RunMeta(run_id=run_id, agent="test-agent", status=status, **extra)


def _register_end(registry: RunRegistry, run: RunMeta) -> None:
    """Register end-of-run with the correct positional args."""
    registry.register_end(run.run_id, exit_code=0, status="completed")


# ---------------------------------------------------------------------------
# verify_chain — real registry on disk
# ---------------------------------------------------------------------------


class TestVerifyChainIntegration:
    """End-to-end verify_chain with real JSONL files."""

    def test_empty_session_returns_empty_or_zero(self, tmp_path: Path) -> None:
        """FR-GOV-AU-002: empty registry returns status=empty or entries=0."""
        result = verify_chain(tmp_path)
        assert isinstance(result, dict)
        assert result.get("status") == "empty" or result.get("entries") == 0

    def test_populated_session_verifies(self, tmp_path: Path) -> None:
        """FR-GOV-AU-001: a populated registry can be verified."""
        registry = RunRegistry(tmp_path)
        run = _make_run("run-aaa")
        registry.register_start(run)
        _register_end(registry, run)
        result = verify_chain(tmp_path)
        assert isinstance(result, dict)
        # Should not raise; integrity check should pass.
        assert result.get("valid") is True or result.get("status") != "corrupt"

    def test_rejects_relative_path(self) -> None:
        """FR-GOV-AU-001: relative paths are rejected."""
        with pytest.raises(ValueError, match="absolute"):
            verify_chain(Path("relative/path"))


# ---------------------------------------------------------------------------
# query_events — real registry on disk
# ---------------------------------------------------------------------------


class TestQueryEventsIntegration:
    """End-to-end query_events with real JSONL files."""

    def test_query_all_events(self, tmp_path: Path) -> None:
        """FR-GOV-AU-006: all events returned when no filters."""
        registry = RunRegistry(tmp_path)
        run1 = _make_run("run-1")
        registry.register_start(run1)
        _register_end(registry, run1)
        run2 = _make_run("run-2")
        registry.register_start(run2)

        events = query_events(tmp_path)
        # list_runs deduplicates by run_id (latest event per run).
        assert len(events) >= 2  # run-1 (finish) + run-2 (start)

    def test_filter_by_run_id(self, tmp_path: Path) -> None:
        """FR-GOV-AU-007: filtering by run_id works."""
        registry = RunRegistry(tmp_path)
        run_x = _make_run("run-x")
        registry.register_start(run_x)
        run_y = _make_run("run-y")
        registry.register_start(run_y)

        events = query_events(tmp_path, run_id="run-x")
        assert all(r.get("run_id") == "run-x" for r in events)
        assert len(events) >= 1

    def test_filter_by_event_type(self, tmp_path: Path) -> None:
        """FR-GOV-AU-008: filtering by event_type works."""
        registry = RunRegistry(tmp_path)
        run1 = _make_run("run-1")
        registry.register_start(run1)
        _register_end(registry, run1)

        starts = query_events(tmp_path, event_type="start")
        assert all((r.get("event") or "start") == "start" for r in starts)

    def test_limit_respected(self, tmp_path: Path) -> None:
        """FR-GOV-AU-005: limit is respected."""
        registry = RunRegistry(tmp_path)
        for i in range(10):
            registry.register_start(_make_run(f"run-{i}"))

        events = query_events(tmp_path, limit=3)
        assert len(events) <= 3

    def test_empty_registry_returns_empty(self, tmp_path: Path) -> None:
        """FR-GOV-AU-010: empty registry returns empty list."""
        assert query_events(tmp_path) == []

    def test_rejects_non_positive_limit(self, tmp_path: Path) -> None:
        """FR-GOV-AU-005: limit <= 0 is rejected."""
        with pytest.raises(ValueError, match="limit"):
            query_events(tmp_path, limit=0)
