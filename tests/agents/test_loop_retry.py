"""Tests for loop_controller.py tenacity-based retry logic.

Verifies that _run_worker_with_retry uses tenacity (via the with_retry decorator
from resilience.py) instead of manual retry loops, and that the retry behavior
is correct: retries on transient/rate-limit failures, raises after exhaustion,
and passes non-retryable failures through immediately.

# @trace FR-AGT-009
"""

from unittest.mock import MagicMock, patch

import pytest

from thegent.agents.base import RunResult
from thegent.agents.loop_controller import LifecycleController, LoopMode
from thegent.agents.resilience import TransientAgentError
from thegent.config import ThegentSettings


@pytest.fixture
def mock_settings(tmp_path):
    settings = MagicMock(spec=ThegentSettings)
    settings.cwd = tmp_path / "cwd"
    settings.cwd.mkdir()
    settings.session_dir = tmp_path / "sessions"
    settings.session_dir.mkdir()
    settings.default_timeout = 60
    return settings


@pytest.fixture
def controller(mock_settings):
    return LifecycleController(
        settings=mock_settings,
        worker_agent_name="test-worker",
        checker_agent_name="test-checker",
        mode=LoopMode.SOFT,
        max_iterations=3,
    )


# ---------------------------------------------------------------------------
# Tests for _run_worker_with_retry
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRunWorkerWithRetry:
    """Tests for LifecycleController._run_worker_with_retry tenacity integration."""

    def test_success_returns_result(self, controller):
        """_run_worker_with_retry returns the result dict on exit_code==0."""
        # @trace FR-AGT-009
        with patch("thegent.agents.loop_controller.run_impl") as mock_run:
            mock_run.return_value = {"exit_code": 0, "stdout": "ok", "stderr": ""}
            result = controller._run_worker_with_retry("do something")
        assert result == {"exit_code": 0, "stdout": "ok", "stderr": ""}

    def test_non_retryable_failure_returned_immediately(self, controller):
        """Non-retryable failures (exit_code!=0, no retryable keywords) are returned, not retried."""
        # @trace FR-AGT-009
        call_count = 0

        def flaky(**kwargs):
            nonlocal call_count
            call_count += 1
            return {"exit_code": 1, "stdout": "", "stderr": "unknown error"}

        with patch("thegent.agents.loop_controller.run_impl", side_effect=flaky):
            result = controller._run_worker_with_retry("do something")

        # Should only call once — non-retryable, so no retry
        assert call_count == 1
        assert result["exit_code"] == 1

    def test_retryable_failure_raises_transient_error_after_exhaustion(self, controller):
        """Retryable failures (rate limit keywords) raise TransientAgentError after max attempts."""
        # @trace FR-AGT-009
        call_count = 0

        def always_rate_limited(**kwargs):
            nonlocal call_count
            call_count += 1
            return {"exit_code": 1, "stdout": "", "stderr": "rate limit exceeded"}

        # Patch the decorator's wait to be instant (0) so the test is fast
        with patch("thegent.agents.loop_controller.run_impl", side_effect=always_rate_limited):
            with patch("tenacity.nap.time.sleep"):  # suppress sleeps
                with pytest.raises(TransientAgentError) as exc_info:
                    controller._run_worker_with_retry("do something")

        # max_attempts=3 means 3 total calls (1 initial + 2 retries)
        assert call_count == 3
        assert exc_info.value.result.exit_code == 1
        assert "rate limit" in exc_info.value.result.stderr

    def test_transient_error_retried_then_succeeds(self, controller):
        """Transient failure on first attempt retries and succeeds on second."""
        # @trace FR-AGT-009
        call_count = 0

        def flaky(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"exit_code": 1, "stdout": "", "stderr": "502 bad gateway"}
            return {"exit_code": 0, "stdout": "ok", "stderr": ""}

        with patch("thegent.agents.loop_controller.run_impl", side_effect=flaky):
            with patch("tenacity.nap.time.sleep"):  # suppress sleeps
                result = controller._run_worker_with_retry("do something")

        assert call_count == 2
        assert result["exit_code"] == 0

    def test_retryable_keywords_trigger_retry(self, controller):
        """Each retryable keyword in output causes a retry (rate limit, timeout, 5xx codes)."""
        # @trace FR-AGT-009
        retryable_outputs = [
            "rate limit",
            "timeout",
            "502",
            "503",
            "504",
            "transient",
        ]
        for keyword in retryable_outputs:
            call_count = 0

            def make_flaky(kw=keyword):
                def flaky(**kwargs):
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:
                        return {"exit_code": 1, "stdout": "", "stderr": kw}
                    return {"exit_code": 0, "stdout": "ok", "stderr": ""}

                return flaky

            with patch("thegent.agents.loop_controller.run_impl", side_effect=make_flaky()):
                with patch("tenacity.nap.time.sleep"):
                    result = controller._run_worker_with_retry("do something")

            assert call_count == 2, f"Expected retry for keyword '{keyword}'; got {call_count} calls"
            assert result["exit_code"] == 0

    def test_no_manual_sleep_or_loop_in_retry_path(self, controller):
        """Verify no time.sleep or manual while-loop is called; tenacity owns backoff."""
        # @trace FR-AGT-009
        # We confirm that the method does NOT call time.sleep directly (tenacity
        # handles all sleeping internally via its wait strategy).
        with patch("thegent.agents.loop_controller.run_impl") as mock_run:
            with patch("time.sleep") as mock_sleep:
                mock_run.return_value = {"exit_code": 0, "stdout": "ok", "stderr": ""}
                controller._run_worker_with_retry("do something")

        # time.sleep must not be called by loop_controller directly.
        # (tenacity uses its own internal sleep which is patched separately)
        mock_sleep.assert_not_called()

    def test_uses_with_retry_decorator(self, controller):
        """_run_worker_with_retry is wrapped by the tenacity-backed with_retry decorator."""
        # @trace FR-AGT-009
        # The with_retry decorator from resilience.py applies tenacity.retry.
        # We verify by checking that the __wrapped__ attribute exists (tenacity sets it).
        method = LifecycleController._run_worker_with_retry
        assert hasattr(method, "__wrapped__"), (
            "_run_worker_with_retry must be wrapped with the tenacity-backed @with_retry decorator"
        )

    def test_retry_only_on_transient_not_permanent(self, controller):
        """Permanent (non-retryable) failures are returned immediately without retry."""
        # @trace FR-AGT-009
        call_count = 0

        def permanent_failure(**kwargs):
            nonlocal call_count
            call_count += 1
            return {"exit_code": 1, "stdout": "", "stderr": "unknown model: bad-model-xyz"}

        with patch("thegent.agents.loop_controller.run_impl", side_effect=permanent_failure):
            result = controller._run_worker_with_retry("do something")

        assert call_count == 1  # no retry
        assert result["exit_code"] == 1


# ---------------------------------------------------------------------------
# Integration: run_loop uses _run_worker_with_retry (not a raw loop)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLoopControllerRetryIntegration:
    """Integration tests: run_loop retry handling via _run_worker_with_retry."""

    @patch("thegent.agents.loop_controller.run_impl")
    def test_loop_stops_after_exhausted_retries(self, mock_run, controller):
        """run_loop stops and sets stop_reason when retries are exhausted."""
        # @trace FR-AGT-009
        mock_run.return_value = {"exit_code": 1, "stdout": "", "stderr": "rate limit exceeded"}

        with patch("tenacity.nap.time.sleep"):
            state = controller.run_loop("Start prompt", "todo spec")

        assert state.stopped is True
        assert "retries" in (state.stop_reason or "").lower()

    @patch("thegent.agents.loop_controller.run_impl")
    def test_loop_recovers_after_transient_failure(self, mock_run, controller):
        """run_loop continues normally when worker recovers after a transient failure."""
        # @trace FR-AGT-009
        from thegent.agents.checker import CheckerDecision, CheckerResult

        call_count = 0

        def flaky(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call: transient failure → tenacity retries
                return {"exit_code": 1, "stdout": "", "stderr": "503 Service Unavailable"}
            # Second call (tenacity retry): success
            return {"exit_code": 0, "stdout": "ok", "stderr": ""}

        mock_run.side_effect = flaky

        with patch("tenacity.nap.time.sleep"):
            with patch.object(controller.checker, "decide") as mock_decide:
                mock_decide.return_value = CheckerResult(
                    decision=CheckerDecision.KILL, reason="Done"
                )
                state = controller.run_loop("Start prompt", "todo spec")

        # Loop completed one iteration successfully after a retry
        assert state.iteration == 1
        assert "Checker terminated" in (state.stop_reason or "")
        # run_impl was called twice: 1 transient + 1 retry success
        assert call_count == 2
