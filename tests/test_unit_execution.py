"""Unit tests for execution registry and state-aware orchestration (G-KD-03)."""

import tempfile
from pathlib import Path

import pytest

from thegent.execution import RunMeta, RunRegistry, RunState


class TestRunRegistryStateAware:
    """Tests for register_pause, register_resume, get_run_state."""

    def test_get_run_state_none_for_unknown_run(self) -> None:
        """Unknown run_id returns None."""
        with tempfile.TemporaryDirectory() as d:
            r = RunRegistry(Path(d))
            assert r.get_run_state("run_unknown") is None

    def test_get_run_state_running_after_start(self) -> None:
        """After register_start, state is RUNNING (no finish event)."""
        with tempfile.TemporaryDirectory() as d:
            r = RunRegistry(Path(d))
            m = RunMeta(run_id="run_1", agent="gemini", prompt="x", cwd="/tmp", owner="u")
            r.register_start(m)
            assert r.get_run_state("run_1") == RunState.RUNNING

    def test_get_run_state_paused_after_pause(self) -> None:
        """After register_pause, state is PAUSED."""
        with tempfile.TemporaryDirectory() as d:
            r = RunRegistry(Path(d))
            m = RunMeta(run_id="run_1", agent="gemini", prompt="x", cwd="/tmp", owner="u")
            r.register_start(m)
            r.register_pause("run_1", "manual", {"phase": "operator"})
            assert r.get_run_state("run_1") == RunState.PAUSED

    def test_get_run_state_running_after_resume(self) -> None:
        """After register_resume, state is RUNNING."""
        with tempfile.TemporaryDirectory() as d:
            r = RunRegistry(Path(d))
            m = RunMeta(run_id="run_1", agent="gemini", prompt="x", cwd="/tmp", owner="u")
            r.register_start(m)
            r.register_pause("run_1", "manual")
            r.register_resume("run_1")
            assert r.get_run_state("run_1") == RunState.RUNNING

    def test_get_run_state_completed_after_finish(self) -> None:
        """After register_end with completed, state is COMPLETED."""
        with tempfile.TemporaryDirectory() as d:
            r = RunRegistry(Path(d))
            m = RunMeta(run_id="run_1", agent="gemini", prompt="x", cwd="/tmp", owner="u")
            r.register_start(m)
            r.register_end("run_1", 0, "completed", "2026-02-14T12:00:00Z", 1.0)
            assert r.get_run_state("run_1") == RunState.COMPLETED

    def test_get_run_state_failed_after_finish(self) -> None:
        """After register_end with failed, state is FAILED."""
        with tempfile.TemporaryDirectory() as d:
            r = RunRegistry(Path(d))
            m = RunMeta(run_id="run_1", agent="gemini", prompt="x", cwd="/tmp", owner="u")
            r.register_start(m)
            r.register_end("run_1", 1, "failed", "2026-02-14T12:00:00Z", 1.0)
            assert r.get_run_state("run_1") == RunState.FAILED
