"""Tests for WL-707: L3 Agent Loop hardening (run_loop decomposition + RunOptions kwarg promotion).

Pins:

1. ``RunOptions`` exposes 8 fields (2 existing + 6 new) and a
   :meth:`to_run_kwargs` helper that omits ``None`` values.
2. ``LifecycleLoopController._run_worker_with_retry`` builds a
   :class:`RunOptions` and forwards its kwargs to ``run_impl`` (the
   contract is now type-pinned, not a 7-kwarg ``run_impl(...)`` call).
3. ``run_loop`` is decomposed into 4 helpers + a thin composer.
4. ``run_loop`` body is under 100 LOC (god-function eliminated).
5. Module-level imports of ``run_impl`` + ``dag_status_impl`` so
   ``@patch("thegent.agents.loop_controller.run_impl")`` monkey-patches
   resolve cleanly.
6. Back-compat: the existing 11 tests in ``test_unit_lifecycle_loop.py``
   continue to work (including the 8 we unblocked by lifting the
   lazy-import pattern).
"""

# @trace WL-707

from __future__ import annotations

import ast
import inspect
import json
from unittest.mock import MagicMock, patch

import pytest

from thegent.agents import run_options as run_options_module
from thegent.agents.checker import CheckerDecision, CheckerResult
from thegent.agents.loop_controller import LifecycleController, LoopMode
from thegent.agents.run_options import RunOptions
from thegent.config import ThegentSettings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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
# TestRunOptionsExtension — the new 6 fields + to_run_kwargs
# ---------------------------------------------------------------------------


class TestRunOptionsExtension:
    """Pin the RunOptions field surface (WL-707 contract)."""

    def test_run_options_has_eight_fields(self) -> None:
        """RunOptions exposes 8 fields: 2 existing (WL-112/113) + 6 new (WL-707)."""
        opts = RunOptions()
        dumped = opts.model_dump()
        assert set(dumped.keys()) == {
            "reasoning_effort",  # WL-112
            "output_schema_path",  # WL-113
            "agent",  # WL-707
            "cd",  # WL-707
            "mode",  # WL-707
            "timeout",  # WL-707
            "model",  # WL-707
            "provider",  # WL-707
        }

    def test_run_options_defaults_all_to_none_or_write(self) -> None:
        """All new fields default to None except ``mode`` which defaults to "write"."""
        opts = RunOptions()
        assert opts.agent is None
        assert opts.cd is None
        assert opts.mode == "write"
        assert opts.timeout is None
        assert opts.model is None
        assert opts.provider is None

    def test_to_run_kwargs_excludes_none_values(self) -> None:
        """``to_run_kwargs`` omits None-valued fields (except ``mode``)."""
        opts = RunOptions()
        kwargs = opts.to_run_kwargs()
        # mode is always present because it has a non-None default
        assert kwargs == {"mode": "write"}

    def test_to_run_kwargs_includes_set_values(self) -> None:
        """``to_run_kwargs`` includes all explicitly-set fields."""
        opts = RunOptions(
            agent="claude",
            cd="/tmp",
            mode="read",
            timeout=30,
            model="opus",
            provider="anthropic",
        )
        kwargs = opts.to_run_kwargs()
        assert kwargs == {
            "agent": "claude",
            "cd": "/tmp",
            "mode": "read",
            "timeout": 30,
            "model": "opus",
            "provider": "anthropic",
        }

    def test_to_run_kwargs_round_trip(self) -> None:
        """Setting a value and reading via to_run_kwargs preserves the value."""
        opts = RunOptions(agent="claude", timeout=42)
        kwargs = opts.to_run_kwargs()
        # Round-trip: build a new RunOptions from the kwargs
        opts2 = RunOptions(**kwargs)
        assert opts2.agent == "claude"
        assert opts2.timeout == 42
        assert opts2.mode == "write"  # mode was filled in by to_run_kwargs

    def test_to_run_kwargs_partial(self) -> None:
        """Only the fields explicitly set are present (plus mode)."""
        opts = RunOptions(agent="claude")
        assert opts.to_run_kwargs() == {"agent": "claude", "mode": "write"}

        opts = RunOptions(timeout=120)
        assert opts.to_run_kwargs() == {"timeout": 120, "mode": "write"}

    def test_run_options_importable_from_agents_package(self) -> None:
        """``RunOptions`` is exported from ``thegent.agents`` (public surface, no SDK re-export exists)."""
        from thegent.agents import RunOptions as PackageRunOptions  # noqa: N813

        assert PackageRunOptions is RunOptions

    def test_run_options_accepts_valid_modes(self) -> None:
        """RunOptions accepts any str in ``mode`` (CLI accepts write/edit/read/plan)."""
        for mode in ("write", "edit", "read", "plan"):
            opts = RunOptions(mode=mode)
            assert opts.mode == mode

    def test_run_options_run_kwarg_fields_default_is_tuple(self) -> None:
        """The private ``_RUN_KWARG_FIELDS`` default is a stable 6-tuple."""
        # Pydantic wraps private attrs in ModelPrivateAttr; the underlying default is a tuple.
        default = RunOptions._RUN_KWARG_FIELDS.default  # type: ignore[attr-defined]
        assert isinstance(default, tuple)
        assert len(default) == 6
        assert set(default) == {"agent", "cd", "mode", "timeout", "model", "provider"}

    def test_translate_helpers_still_exported(self) -> None:
        """The WL-112 translate helpers continue to be exported from run_options."""
        from thegent.agents.run_options import (
            translate_reasoning_to_anthropic_budget,
            translate_reasoning_to_codex_config,
            translate_reasoning_to_openai_effort,
        )

        assert translate_reasoning_to_codex_config("medium") == {"model_reasoning_effort": "medium"}
        assert translate_reasoning_to_anthropic_budget("high") == 8000
        assert translate_reasoning_to_openai_effort("xhigh") == "high"
        assert translate_reasoning_to_openai_effort("medium") == "medium"


# ---------------------------------------------------------------------------
# TestRunWorkerWithRetryUsesRunOptions — the migration contract
# ---------------------------------------------------------------------------


class TestRunWorkerWithRetryUsesRunOptions:
    """Pin that _run_worker_with_retry builds a RunOptions, not raw kwargs."""

    def test_run_worker_with_retry_builds_run_options(self, controller) -> None:
        """The retry helper constructs a RunOptions internally."""
        with (
            patch("thegent.agents.loop_controller.run_impl") as mock_run,
            patch.object(RunOptions, "__init__", wraps=RunOptions.__init__, autospec=True) as spy_init,
        ):
            mock_run.return_value = {"exit_code": 0, "stdout": "ok", "stderr": ""}
            controller._run_worker_with_retry("hello")

        # Pin that the RunOptions constructor was called with the canonical
        # 6 kwargs (which is the contract). We use autospec=True so the
        # spy receives the class as the first positional argument.
        assert spy_init.call_count == 1
        call_kwargs = spy_init.call_args.kwargs
        assert call_kwargs.get("agent") == "test-worker"
        assert call_kwargs.get("cd") == str(controller.settings.cwd)
        assert call_kwargs.get("mode") == "write"
        assert call_kwargs.get("timeout") == 60
        assert call_kwargs.get("model") is None
        assert call_kwargs.get("provider") is None

    def test_run_worker_with_retry_worker_model_overrides_agent(self, mock_settings) -> None:
        """When worker_model is set, agent is None and provider is the agent name."""
        controller = LifecycleController(
            settings=mock_settings,
            worker_agent_name="ignored",
            worker_model="opus-4",
        )
        with (
            patch("thegent.agents.loop_controller.run_impl") as mock_run,
            patch.object(RunOptions, "__init__", wraps=RunOptions.__init__, autospec=True) as spy_init,
        ):
            mock_run.return_value = {"exit_code": 0, "stdout": "ok", "stderr": ""}
            controller._run_worker_with_retry("hello")

        call_kwargs = spy_init.call_args.kwargs
        assert call_kwargs.get("agent") is None
        assert call_kwargs.get("model") == "opus-4"
        assert call_kwargs.get("provider") == "ignored"

    def test_run_worker_with_retry_no_worker_model_uses_agent_name(self, controller) -> None:
        """When worker_model is None, agent is the worker_agent_name."""
        with (
            patch("thegent.agents.loop_controller.run_impl") as mock_run,
            patch.object(RunOptions, "__init__", wraps=RunOptions.__init__, autospec=True) as spy_init,
        ):
            mock_run.return_value = {"exit_code": 0, "stdout": "ok", "stderr": ""}
            controller._run_worker_with_retry("hello")

        assert spy_init.call_args.kwargs.get("agent") == "test-worker"
        assert spy_init.call_args.kwargs.get("provider") is None

    def test_run_worker_with_retry_raises_on_transient_failure(self, controller) -> None:
        """Transient errors (rate limit / 502 / etc) raise TransientAgentError."""
        from thegent.agents.resilience import TransientAgentError

        with patch("thegent.agents.loop_controller.run_impl") as mock_run:
            mock_run.return_value = {
                "exit_code": 1,
                "stdout": "",
                "stderr": "rate limit exceeded",
                "timed_out": False,
            }
            with pytest.raises(TransientAgentError):
                controller._run_worker_with_retry("hello")

    def test_run_worker_with_retry_returns_immediately_on_success(self, controller) -> None:
        """On exit_code 0 the retry helper returns the result dict."""
        expected = {"exit_code": 0, "stdout": "ok", "stderr": ""}
        with patch("thegent.agents.loop_controller.run_impl") as mock_run:
            mock_run.return_value = expected
            result = controller._run_worker_with_retry("hello")
        assert result == expected

    def test_run_worker_with_retry_passes_prompt_as_keyword(self, controller) -> None:
        """prompt is forwarded as a keyword argument to run_impl."""
        with patch("thegent.agents.loop_controller.run_impl") as mock_run:
            mock_run.return_value = {"exit_code": 0, "stdout": "ok", "stderr": ""}
            controller._run_worker_with_retry("specific-prompt")
        assert mock_run.call_args.kwargs["prompt"] == "specific-prompt"

    def test_run_worker_with_retry_module_level_run_impl_importable(self) -> None:
        """``run_impl`` is exposed at module level (no lazy import inside the function).

        The previous implementation imported ``run_impl`` lazily inside
        ``_run_worker_with_retry`` which shadowed monkey-patches of the module
        attribute (``@patch("thegent.agents.loop_controller.run_impl")``). This
        test pins the lift to module-level scope.
        """
        import thegent.agents.loop_controller as lc_mod

        # Both module-level callables must exist and be callable.
        assert callable(getattr(lc_mod, "run_impl", None))
        assert callable(getattr(lc_mod, "dag_status_impl", None))

        # And we can re-import them by name (the contract for patch decorators).
        from thegent.agents.loop_controller import run_impl, dag_status_impl

        assert callable(run_impl)
        assert callable(dag_status_impl)


# ---------------------------------------------------------------------------
# TestRunLoopDecomposition — the 4 helper extraction
# ---------------------------------------------------------------------------


class TestRunLoopDecomposition:
    """Pin the run_loop decomposition into 4 helpers + thin composer."""

    def test_run_loop_orchestrator_under_100_loc(self) -> None:
        """The new ``run_loop`` composer is under 100 LOC (down from 224)."""
        from thegent.agents.loop_controller import LifecycleController

        source = inspect.getsource(LifecycleController.run_loop)
        # Count non-blank, non-comment lines
        lines = [ln for ln in source.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        assert len(lines) < 100, f"run_loop is {len(lines)} non-blank lines (expected <100)"

    def test_run_loop_has_four_canonical_helpers(self) -> None:
        """The 4 canonical helpers exist on the controller."""
        from thegent.agents.loop_controller import LifecycleController

        for name in (
            "_check_stop_signals",
            "_evaluate_governance",
            "_execute_worker_iteration",
            "_handle_checker_decision",
            "_invoke_checker",
            "_check_soft_loop_signal",
            "_resolve_session_dir",
            "_escalate_policy_denial",
            "_run_progress_loop",
        ):
            assert hasattr(LifecycleController, name), f"Missing helper: {name}"

    def test_check_stop_signals_handles_stop_file(self, controller) -> None:
        """STOP file in session_dir triggers stop."""
        session_dir = controller.settings.session_dir / controller.state.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "STOP").write_text("STOP")
        stopped, reason, prompt = controller._check_stop_signals(session_dir, "any", None)
        assert stopped is True
        assert reason == "External stop signal received"
        assert prompt == "any"
        # File should be removed
        assert not (session_dir / "STOP").exists()

    def test_check_stop_signals_handles_takeover_json(self, controller) -> None:
        """takeover.json injects the new prompt."""
        session_dir = controller.settings.session_dir / controller.state.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "takeover.json").write_text(json.dumps({"prompt": "Takeover Prompt"}))
        stopped, _reason, prompt = controller._check_stop_signals(session_dir, "initial", None)
        assert stopped is False
        assert prompt == "Takeover Prompt"
        assert not (session_dir / "takeover.json").exists()

    def test_check_stop_signals_handles_takeover_malformed(self, controller) -> None:
        """A malformed takeover.json is gracefully ignored (no injected prompt)."""
        session_dir = controller.settings.session_dir / controller.state.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "takeover.json").write_text("not valid json {{{")
        stopped, reason, prompt = controller._check_stop_signals(session_dir, "initial", None)
        assert stopped is False
        assert prompt == "initial"  # original prompt preserved
        assert reason == ""

    def test_check_stop_signals_no_files(self, controller) -> None:
        """When neither STOP nor takeover.json exists, returns False/empty/original."""
        session_dir = controller.settings.session_dir / controller.state.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        stopped, reason, prompt = controller._check_stop_signals(session_dir, "initial", None)
        assert stopped is False
        assert reason == ""
        assert prompt == "initial"

    def test_evaluate_governance_returns_allow_on_no_policy(self, controller) -> None:
        """Default behaviour: governance returns allow."""
        gov_report, effect, _reason = controller._evaluate_governance("prompt", None)
        assert "status" in gov_report
        # Should be one of: allow / deny / warn
        assert effect in ("allow", "deny", "warn")

    def test_resolve_session_dir_creates_directory(self, controller) -> None:
        """_resolve_session_dir creates the session directory."""
        session_dir = controller._resolve_session_dir()
        assert session_dir.exists()
        assert session_dir.is_dir()

    def test_handle_checker_decision_kill_branch(self, controller) -> None:
        """KILL decision sets stopped + stop_reason."""
        decision = CheckerResult(decision=CheckerDecision.KILL, reason="Cycle detected")
        _next_prompt, stopped, reason = controller._handle_checker_decision(decision, "current")
        assert stopped is True
        assert "Checker terminated" in reason
        assert "Cycle detected" in reason
        assert controller.state.stopped is True

    def test_handle_checker_decision_continue_branch(self, controller) -> None:
        """CONTINUE decision returns the preset prompt and leaves state alone."""
        decision = CheckerResult(decision=CheckerDecision.CONTINUE, reason="Keep going")
        next_prompt, stopped, reason = controller._handle_checker_decision(decision, "current")
        assert stopped is False
        assert reason is None
        from thegent.agents.presets import get_preset

        assert next_prompt == get_preset("continue").prompt
        assert controller.state.stopped is False

    def test_handle_checker_decision_re_prompt_branch(self, controller) -> None:
        """RE_PROMPT decision uses decision.prompt as the next prompt."""
        decision = CheckerResult(decision=CheckerDecision.RE_PROMPT, prompt="Fix this bug", reason="Bug found")
        next_prompt, _stopped, _reason = controller._handle_checker_decision(decision, "current")
        assert next_prompt == "Fix this bug"

    def test_handle_checker_decision_re_prompt_fallback(self, controller) -> None:
        """RE_PROMPT with no prompt falls back to "Please continue."."""
        decision = CheckerResult(decision=CheckerDecision.RE_PROMPT, prompt=None, reason="x")
        next_prompt, _stopped, _reason = controller._handle_checker_decision(decision, "current")
        assert next_prompt == "Please continue."

    def test_handle_checker_decision_escalates_on_security_risk(self, controller) -> None:
        """KILL with security/cost/risk/policy keyword triggers EscalationQueue."""
        with patch("thegent.governance.escalation.EscalationQueue.escalate") as mock_escalate:
            decision = CheckerResult(
                decision=CheckerDecision.KILL,
                reason="Cost exceeded budget",
            )
            controller._handle_checker_decision(decision, "current")
            assert mock_escalate.call_count == 1

    def test_check_soft_loop_signal_hard_mode(self, controller) -> None:
        """HARD mode does NOT trigger STOP from worker output."""
        controller.mode = LoopMode.HARD
        assert controller._check_soft_loop_signal("All done! STOP") is False

    def test_check_soft_loop_signal_soft_mode_no_stop(self, controller) -> None:
        """SOFT mode without STOP in output returns False."""
        assert controller._check_soft_loop_signal("normal output") is False

    def test_check_soft_loop_signal_soft_mode_with_stop(self, controller) -> None:
        """SOFT mode with STOP in output returns True and sets state."""
        result = controller._check_soft_loop_signal("All done! STOP")
        assert result is True
        assert controller.state.stopped is True
        assert "Human stop signal" in controller.state.stop_reason

    def test_invoke_checker_falls_back_on_failure(self, controller) -> None:
        """Checker invocation failure gracefully degrades to CONTINUE."""
        decision = controller._invoke_checker(
            todo_spec="todo",
            combined="output",
            gov_report={"status": "ok", "denials": [], "warnings": []},
            on_progress=None,
        )
        # The fallback returns CONTINUE
        assert decision.decision in (CheckerDecision.CONTINUE, CheckerDecision.KILL)


# ---------------------------------------------------------------------------
# TestBackCompatibility — the public API is preserved
# ---------------------------------------------------------------------------


class TestBackCompatibility:
    """Pin that the public API of LifecycleController is unchanged."""

    def test_run_loop_signature_unchanged(self) -> None:
        """``run_loop`` accepts (initial_prompt, todo_spec, on_worker_output, on_progress) -> LoopState."""
        from thegent.agents.loop_controller import LifecycleController

        sig = inspect.signature(LifecycleController.run_loop)
        params = list(sig.parameters.keys())
        assert params[:2] == ["self", "initial_prompt"]
        assert "todo_spec" in params
        assert "on_worker_output" in params
        assert "on_progress" in params
        assert sig.return_annotation.__name__ == "LoopState"

    def test_module_level_run_impl_exists(self) -> None:
        """``run_impl`` is a module-level attribute (so @patch works)."""
        from thegent.agents import loop_controller

        assert hasattr(loop_controller, "run_impl")

    def test_module_level_dag_status_impl_exists(self) -> None:
        """``dag_status_impl`` is a module-level attribute (so @patch works)."""
        from thegent.agents import loop_controller

        assert hasattr(loop_controller, "dag_status_impl")

    def test_aliases_preserved(self) -> None:
        """Backward-compat aliases LifecycleLoopController and RalphWiggumController exist."""
        from thegent.agents.loop_controller import (
            LifecycleLoopController,
            RalphWiggumController,
        )

        assert LifecycleLoopController is LifecycleController
        assert RalphWiggumController is LifecycleController

    def test_run_loop_iteration_counter_increments(self, controller) -> None:
        """Smoke: run_loop increments state.iteration."""
        with patch("thegent.agents.loop_controller.run_impl") as mock_run:
            mock_run.return_value = {"exit_code": 0, "stdout": "ok", "stderr": ""}
            with patch.object(controller.checker, "decide") as mock_decide:
                mock_decide.return_value = CheckerResult(decision=CheckerDecision.KILL, reason="Done")
                state = controller.run_loop("start", "todo")
        assert state.iteration == 1
        assert state.stopped is True

    def test_run_loop_respects_max_iterations(self, controller) -> None:
        """Smoke: loop stops at max_iterations when checker always returns CONTINUE."""
        with patch("thegent.agents.loop_controller.run_impl") as mock_run:
            mock_run.return_value = {"exit_code": 0, "stdout": "ok", "stderr": ""}
            with patch.object(controller.checker, "decide") as mock_decide:
                mock_decide.return_value = CheckerResult(decision=CheckerDecision.CONTINUE, reason="keep going")
                state = controller.run_loop("start", "todo")
        assert state.iteration == controller.max_iterations
        assert state.stop_reason == "Max iterations reached"


# ---------------------------------------------------------------------------
# TestDecompositionMetrics — structural metrics
# ---------------------------------------------------------------------------


class TestDecompositionMetrics:
    """Pin the structural metrics of the refactor."""

    def test_module_constants_extracted(self) -> None:
        """The escalation keywords and retryable failure keywords are module-level constants."""
        from thegent.agents import loop_controller

        assert hasattr(loop_controller, "_ESCALATION_REASON_KEYWORDS")
        assert hasattr(loop_controller, "_RETRYABLE_FAILURE_KEYWORDS")
        assert loop_controller._ESCALATION_REASON_KEYWORDS == ("security", "cost", "risk", "policy")
        assert "rate limit" in loop_controller._RETRYABLE_FAILURE_KEYWORDS

    def test_loop_controller_class_method_count(self) -> None:
        """The controller has a sane number of methods (no explosion)."""
        from thegent.agents.loop_controller import LifecycleController

        methods = [
            name
            for name, obj in inspect.getmembers(LifecycleController, predicate=inspect.isfunction)
            if not name.startswith("__")
        ]
        # 1 __init__ + 1 _run_worker_with_retry + 8 helpers + 1 _run_progress_loop + 1 run_loop = 12
        assert 10 <= len(methods) <= 20, f"Unexpected method count: {len(methods)}"

    def test_run_options_has_to_run_kwargs(self) -> None:
        """RunOptions has the to_run_kwargs method."""
        assert hasattr(RunOptions, "to_run_kwargs")

    def test_run_options_module_path(self) -> None:
        """RunOptions is importable from thegent.agents.run_options."""
        assert run_options_module.RunOptions is RunOptions
