"""Tests for WL-076: Worker pool in-process agent execution.

Verifies that PersistentWorkerPool dispatches tasks via in-process
agent runner calls instead of spawning a subprocess per task.

# @trace FR-OPT-006
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from thegent.agents.base import RunResult


@pytest.mark.requirement("FR-OPT-006")
class TestWorkerPoolInProcess:
    """Verify the worker bootstrap calls agent runners in-process, not via subprocess."""

    def test_task_dispatched_in_process(self):
        """_run_task_in_process must NOT call subprocess.run."""
        from thegent.core.worker_pool import _run_task_in_process

        task = {
            "task_id": "test-1",
            "prompt": "hello",
            "cwd": "/tmp",
            "mode": "write",
            "timeout": 60,
            "env": {},
            "agent_name": "claude",
        }

        mock_runner = MagicMock()
        mock_runner.run.return_value = RunResult(
            exit_code=0,
            stdout="done",
            stderr="",
            timed_out=False,
        )

        with (
            patch("thegent.core.worker_pool.get_runner", return_value=mock_runner),
            patch("subprocess.run") as mock_subprocess,
        ):
            result = _run_task_in_process(task)

        mock_subprocess.assert_not_called()
        mock_runner.run.assert_called_once()
        assert result["exit_code"] == 0
        assert result["stdout"] == "done"

    def test_task_result_returned(self):
        """_run_task_in_process returns correct result dict with all expected fields."""
        from thegent.core.worker_pool import _run_task_in_process

        task = {
            "task_id": "test-2",
            "prompt": "world",
            "cwd": "/tmp",
            "mode": "write",
            "timeout": 60,
            "env": {},
            "agent_name": "claude",
        }

        mock_runner = MagicMock()
        mock_runner.run.return_value = RunResult(
            exit_code=0,
            stdout="output text",
            stderr="warn text",
            timed_out=False,
        )

        with patch("thegent.core.worker_pool.get_runner", return_value=mock_runner):
            result = _run_task_in_process(task)

        assert result["task_id"] == "test-2"
        assert result["exit_code"] == 0
        assert result["stdout"] == "output text"
        assert result["stderr"] == "warn text"
        assert result["timed_out"] is False
        assert "duration_ms" in result
        assert result["duration_ms"] >= 0
        assert "worker_pid" in result

    def test_task_failure_raises(self):
        """_run_task_in_process raises on runner errors instead of silently returning defaults."""
        from thegent.core.worker_pool import _run_task_in_process

        task = {
            "task_id": "test-3",
            "prompt": "fail me",
            "cwd": "/tmp",
            "mode": "write",
            "timeout": 60,
            "env": {},
            "agent_name": "claude",
        }

        mock_runner = MagicMock()
        mock_runner.run.side_effect = RuntimeError("Agent crashed")

        with patch("thegent.core.worker_pool.get_runner", return_value=mock_runner):
            with pytest.raises(RuntimeError, match="Agent crashed"):
                _run_task_in_process(task)

    def test_runner_exit_code_nonzero_propagated(self):
        """Non-zero exit codes from the runner are faithfully propagated."""
        from thegent.core.worker_pool import _run_task_in_process

        task = {
            "task_id": "test-4",
            "prompt": "bad prompt",
            "cwd": "/tmp",
            "mode": "write",
            "timeout": 60,
            "env": {},
            "agent_name": "claude",
        }

        mock_runner = MagicMock()
        mock_runner.run.return_value = RunResult(
            exit_code=1,
            stdout="",
            stderr="error output",
            timed_out=False,
        )

        with patch("thegent.core.worker_pool.get_runner", return_value=mock_runner):
            result = _run_task_in_process(task)

        assert result["exit_code"] == 1
        assert result["stderr"] == "error output"

    def test_timed_out_flag_propagated(self):
        """Timeout flag from the runner is faithfully propagated."""
        from thegent.core.worker_pool import _run_task_in_process

        task = {
            "task_id": "test-5",
            "prompt": "slow prompt",
            "cwd": "/tmp",
            "mode": "write",
            "timeout": 1,
            "env": {},
            "agent_name": "claude",
        }

        mock_runner = MagicMock()
        mock_runner.run.return_value = RunResult(
            exit_code=124,
            stdout="",
            stderr="timed out",
            timed_out=True,
        )

        with patch("thegent.core.worker_pool.get_runner", return_value=mock_runner):
            result = _run_task_in_process(task)

        assert result["timed_out"] is True
        assert result["exit_code"] == 124
