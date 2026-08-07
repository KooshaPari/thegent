"""Lifecycle Loop Controller with Checker Agent oversight."""

import json
import logging
import time
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from pydantic import BaseModel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeRemainingColumn

# Type for verification callback: (task_id, result) -> Any
VerificationCallback = Callable[[str, Any], Any]

from thegent.agents.base import RunResult
from thegent.agents.checker import CheckerAgent, CheckerDecision, CheckerResult
from thegent.agents.presets import get_preset, match_preset
from thegent.agents.resilience import TransientAgentError, with_retry
from thegent.agents.run_options import RunOptions
from thegent.config import ThegentSettings

# Module-level imports of the cli dispatch shims so tests can monkey-patch
# ``thegent.agents.loop_controller.run_impl`` / ``dag_status_impl`` via
# ``@patch(...)``. The lazy-import pattern inside each helper would shadow
# the module-level attribute, so we lift them here (the ``tach-ignore``
# markers remain on the call sites to document the dependency).
# @trace WL-707
# tach-ignore(agents should not architecturally depend on cli)
from thegent.cli.commands.impl import run_impl  # noqa: E402

# ``dag_status_impl`` lives in the dag_impl subpackage; lift it here so the
# ``@patch`` target on ``thegent.agents.loop_controller.dag_status_impl``
# resolves cleanly during monkey-patch.
# @trace WL-707
# tach-ignore(agents should not architecturally depend on cli)
from thegent.cli.commands.dag_impl import dag_status_impl  # noqa: E402

_log = logging.getLogger(__name__)

# Reason keywords that route a KILL into the EscalationQueue (WL-707).
# Pinned to the existing inline list so the helper extraction is
# behaviour-preserving.
_ESCALATION_REASON_KEYWORDS: tuple[str, ...] = ("security", "cost", "risk", "policy")

# Retryable failure substrings (WL-707 — moved to module constant so the
# ``_run_worker_with_retry`` helper extraction stays under 10 CC).
_RETRYABLE_FAILURE_KEYWORDS: tuple[str, ...] = (
    "rate limit",
    "timeout",
    "502",
    "503",
    "504",
    "transient",
)


class LoopMode(StrEnum):
    """Lifecycle loop modes."""

    SOFT = "soft"
    HARD = "hard"


class LoopState(BaseModel):
    """Current state of a Lifecycle loop."""

    session_id: str
    iteration: int = 0
    last_response: str = ""
    mode: LoopMode = LoopMode.SOFT
    stopped: bool = False
    stop_reason: str | None = None
    last_cost_usd: float | None = None
    last_model: str | None = None


class LifecycleController:
    """Handles agent execution loops (Ralph Wiggum loops) with Checker Agent oversight."""

    def __init__(
        self,
        settings: ThegentSettings,
        worker_agent_name: str,
        checker_agent_name: str = "antigravity",
        mode: LoopMode = LoopMode.SOFT,
        max_iterations: int = 10,
        worker_model: str | None = None,
        task_id: str | None = None,
        verification_callback: VerificationCallback | None = None,
    ) -> None:
        self.settings = settings
        self.worker_agent_name = worker_agent_name
        self.worker_model = worker_model
        self.checker = CheckerAgent(settings, agent_name=checker_agent_name)
        self.task_id = task_id
        self.verification_callback = verification_callback
        self.mode = mode
        self.max_iterations = max_iterations
        self.state = LoopState(
            session_id=f"rw-{int(time.time())}",
            mode=mode,
        )

    @with_retry(max_attempts=3, min_wait=2.0, max_wait=60.0)
    def _run_worker_with_retry(self, current_prompt: str) -> dict[str, Any]:
        """Run worker agent; raises TransientAgentError on retryable failure.

        Routes the canonical ``run_impl`` kwargs through :class:`RunOptions`
        so the call-site shape is pinned by the contract model (WL-707).
        The :func:`run_impl` signature still accepts ``**kwargs`` so any
        future field added to ``RunOptions`` continues to flow through
        without breaking the consumer.
        """
        opts = RunOptions(
            agent=None if self.worker_model else self.worker_agent_name,
            cd=str(self.settings.cwd),
            mode="write",
            timeout=self.settings.default_timeout,
            model=self.worker_model,
            provider=self.worker_agent_name if self.worker_model else None,
        )
        result = run_impl(prompt=current_prompt, **opts.to_run_kwargs())
        if result.get("exit_code") == 0:
            return result
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        combined = f"{stdout}\n{stderr}"
        retryable = any(kw in combined.lower() for kw in _RETRYABLE_FAILURE_KEYWORDS)
        if retryable:
            rr = RunResult(
                exit_code=result.get("exit_code", 1),
                stdout=stdout,
                stderr=stderr,
                timed_out=result.get("timed_out", False),
            )
            raise TransientAgentError(rr)
        return result

    def _resolve_session_dir(self) -> Any:
        """Create and return the per-session directory.

        # @trace WL-707
        """
        session_dir = self.settings.session_dir / self.state.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def _check_stop_signals(
        self,
        session_dir: Any,
        current_prompt: str,
        on_progress: Callable[[int, int, str], None] | None,
    ) -> tuple[bool, str, str]:
        """Check for external STOP file and takeover.json.

        Returns ``(stopped, stop_reason, current_prompt)``.

        - STOP file → ``(True, "External stop signal received", prompt)``
        - takeover.json → ``(False, "", takeover_prompt)`` + file removed
        - neither → ``(False, "", current_prompt)``

        # @trace WL-707
        """
        # External stop signal (Phase 4: Human Takeover)
        if (session_dir / "STOP").exists():
            (session_dir / "STOP").unlink()
            return True, "External stop signal received", current_prompt

        # Human takeover prompt injection
        takeover_file = session_dir / "takeover.json"
        if takeover_file.exists():
            try:
                data = json.loads(takeover_file.read_text(encoding="utf-8"))
                new_prompt = data["prompt"]
                _log.info("Human takeover detected. Injecting prompt.")
                if on_progress:
                    on_progress(self.state.iteration, self.max_iterations, "Human takeover detected. Injecting prompt.")
                takeover_file.unlink()
                return False, "", new_prompt
            except Exception as e:
                _log.error("Failed to read takeover file: %s", e)

        return False, "", current_prompt

    def _evaluate_governance(
        self,
        current_prompt: str,
        on_progress: Callable[[int, int, str], None] | None,
    ) -> tuple[dict[str, Any], str, str | None]:
        """Run PolicyEngine pre-check (WP-3001).

        Returns ``(gov_report, effect, reason)``. On any internal error
        or missing policy module, defaults to ``allow`` with the error
        message as the reason so the loop continues.

        # @trace WL-707
        """
        try:
            from thegent.execution import PolicyEngine, RunMeta

            pe = PolicyEngine(self.settings)
            temp_run = RunMeta(
                run_id=self.state.session_id,
                agent=self.worker_agent_name,
                prompt=current_prompt,
                cwd=str(self.settings.cwd),
                owner="loop_controller",
                lane="standard",
            )
            effect, reason = pe.evaluate(temp_run)
            gov_report = {
                "status": effect,
                "denials": [reason] if effect == "deny" else [],
                "warnings": [reason] if effect == "warn" else [],
            }
        except Exception as e:
            _log.error("Governance pre-check failed: %s. Using default allow.", e)
            effect, reason = "allow", str(e)
            gov_report = {"status": "ok", "denials": [], "warnings": []}

        if on_progress:
            on_progress(self.state.iteration, self.max_iterations, f"Policy check: {effect}")
        return gov_report, effect, reason

    def _escalate_policy_denial(self, reason: str) -> None:
        """Route a policy denial into the EscalationQueue.

        # @trace WL-707
        """
        from thegent.governance.escalation import EscalationQueue

        eq = EscalationQueue(self.settings)
        eq.add(run_id=self.state.session_id, reason=f"Policy denial: {reason}", priority=3)

    def _execute_worker_iteration(
        self,
        current_prompt: str,
        on_progress: Callable[[int, int, str], None] | None,
    ) -> dict[str, Any] | None:
        """Run one worker iteration with retry + exception handling.

        Returns the worker result dict on success, or ``None`` when the
        loop has been stopped (state.stopped is set on the controller).

        # @trace WL-707
        """
        try:
            if on_progress:
                on_progress(
                    self.state.iteration,
                    self.max_iterations,
                    f"Running worker agent: {self.worker_agent_name}",
                )
            result = self._run_worker_with_retry(current_prompt)
            if result.get("exit_code") != 0:
                self.state.stopped = True
                self.state.stop_reason = f"Worker failed (code {result.get('exit_code')})"
                return None
            return result
        except TransientAgentError as e:
            _log.warning(
                "Worker failed after retries: %s",
                e.result.stderr[:200] if e.result.stderr else str(e),
            )
            self.state.stopped = True
            self.state.stop_reason = f"Worker failed after retries (code {e.result.exit_code})"
            return None
        except Exception as e:
            _log.error("Worker execution failed: %s", e)
            self.state.stopped = True
            self.state.stop_reason = f"Worker exception: {e}"
            return None

    def _handle_checker_decision(
        self,
        decision_result: CheckerResult,
        current_prompt: str,
    ) -> tuple[str, bool, str | None]:
        """Apply the checker decision and return ``(next_prompt, stopped, reason)``.

        - KILL → ``(current_prompt, True, "Checker terminated: <reason>")`` and
          escalates if the reason contains a security/cost/risk/policy keyword
        - CONTINUE → ``(preset_prompt, False, None)``
        - RE_PROMPT → ``(decision.prompt, False, None)``

        # @trace WL-707
        """
        _log.info("Checker decision: %s (reason: %s)", decision_result.decision, decision_result.reason)

        if decision_result.decision == CheckerDecision.KILL:
            self.state.stopped = True
            reason = decision_result.reason or ""
            self.state.stop_reason = f"Checker terminated: {reason}"
            if any(kw in reason.lower() for kw in _ESCALATION_REASON_KEYWORDS):
                from thegent.governance.escalation import EscalationPriority, EscalationQueue

                eq = EscalationQueue(self.settings)
                eq.escalate(
                    run_id=self.state.session_id,
                    prompt=current_prompt,
                    reason=f"Checker termination: {reason}",
                    agent=self.worker_agent_name,
                    priority=EscalationPriority.NORMAL,
                )
            return current_prompt, True, self.state.stop_reason

        if decision_result.decision == CheckerDecision.CONTINUE:
            preset = get_preset("continue")
            return (preset.prompt if preset else "Continue"), False, None

        # RE_PROMPT (and any unknown future decision)
        return decision_result.prompt or "Please continue.", False, None

    def _check_soft_loop_signal(self, combined: str) -> bool:
        """Return True if SOFT mode and the worker output contains a STOP signal.

        # @trace WL-707
        """
        if self.mode != LoopMode.SOFT:
            return False
        if "STOP" in combined:
            self.state.stopped = True
            self.state.stop_reason = "Human stop signal detected (SOFT mode)"
            return True
        return False

    def _invoke_checker(
        self,
        todo_spec: str,
        combined: str,
        gov_report: dict[str, Any],
        on_progress: Callable[[int, int, str], None] | None,
    ) -> CheckerResult:
        """Invoke the checker agent; gracefully degrade to CONTINUE on any failure.

        # @trace WL-707
        """
        try:
            wbs_status = dag_status_impl(self.settings.cwd)
            if on_progress:
                on_progress(
                    self.state.iteration,
                    self.max_iterations,
                    f"Invoking checker agent: {self.checker.agent_name}",
                )
            return self.checker.decide(
                governance_report=gov_report,
                todo_spec=todo_spec,
                wbs_status=wbs_status,
                agent_response=combined,
            )
        except Exception as e:
            _log.error("Checker failed: %s. Using default CONTINUE.", e)
            return CheckerResult(decision=CheckerDecision.CONTINUE, reason=str(e))

    def _run_progress_loop(
        self,
        todo_spec: str,
        on_worker_output: Callable[[str], None] | None,
        on_progress: Callable[[int, int, str], None] | None,
    ) -> str:
        """Drive the rich-progress lifecycle iteration loop.

        Returns the final ``current_prompt`` (used for state tracking;
        the canonical return is the controller's ``self.state``).

        # @trace WL-707
        """
        current_prompt = ""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[dim]{task.fields[status]}[/dim]"),
            TimeRemainingColumn(),
            transient=False,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Lifecycle loop ({self.mode.value} mode)",
                total=self.max_iterations,
                status="starting...",
            )

            while self.state.iteration < self.max_iterations and not self.state.stopped:
                self.state.iteration += 1
                _log.info("Iteration %d/%d", self.state.iteration, self.max_iterations)
                progress.update(
                    task,
                    completed=self.state.iteration,
                    status=f"iteration {self.state.iteration}/{self.max_iterations}",
                )
                if on_progress:
                    on_progress(
                        self.state.iteration,
                        self.max_iterations,
                        f"Starting iteration {self.state.iteration}",
                    )

                # Lazy session_dir resolution on first iteration
                if not current_prompt:
                    session_dir = self._resolve_session_dir()
                    current_prompt = self._initial_prompt  # type: ignore[attr-defined]

                # 1. Stop / takeover signals
                stopped, reason, current_prompt = self._check_stop_signals(session_dir, current_prompt, on_progress)
                if stopped:
                    self.state.stopped = True
                    self.state.stop_reason = reason
                    break

                # 2. Governance pre-check
                gov_report, effect, gov_reason = self._evaluate_governance(current_prompt, on_progress)
                if effect == "deny":
                    self.state.stopped = True
                    self.state.stop_reason = f"Policy denied: {gov_reason}"
                    self._escalate_policy_denial(gov_reason or "")
                    break

                # 3. Worker iteration (with retry)
                result = self._execute_worker_iteration(current_prompt, on_progress)
                if self.state.stopped:
                    break

                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                combined = f"{stdout}\n{stderr}"
                self.state.last_response = combined
                self.state.last_cost_usd = result.get("cost_usd")
                self.state.last_model = result.get("model")
                if on_worker_output:
                    on_worker_output(combined)

                # 4. Soft-loop STOP signal
                if self._check_soft_loop_signal(combined):
                    break

                # 5. Preset prompt routing (WP-1201 Phase 1)
                matched_preset = match_preset(combined)
                if matched_preset:
                    current_prompt = matched_preset.prompt
                    _log.info("Matched output to preset: %s", matched_preset.id)
                    if on_progress:
                        on_progress(
                            self.state.iteration,
                            self.max_iterations,
                            f"Matched preset: {matched_preset.id}",
                        )
                    continue

                # 6. Checker decision (WP-1201 Phase 2/3)
                decision_result = self._invoke_checker(todo_spec, combined, gov_report, on_progress)
                if on_progress:
                    on_progress(
                        self.state.iteration,
                        self.max_iterations,
                        f"Checker decision: {decision_result.decision}",
                    )
                current_prompt, stopped, _reason = self._handle_checker_decision(decision_result, current_prompt)
                if stopped:
                    break

            progress.update(task, status=f"done: {self.state.stop_reason or 'completed'}")
        return current_prompt

    def run_loop(
        self,
        initial_prompt: str,
        todo_spec: str,
        on_worker_output: Callable[[str], None] | None = None,
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> LoopState:
        """Execute the Lifecycle loop.

        This is a thin composer that delegates to:

        - :meth:`_run_progress_loop` — the rich-progress iteration loop
        - :meth:`_resolve_session_dir` — per-session directory creation
        - :meth:`_check_stop_signals` — STOP file + takeover.json
        - :meth:`_evaluate_governance` — PolicyEngine pre-check
        - :meth:`_escalate_policy_denial` — EscalationQueue routing
        - :meth:`_execute_worker_iteration` — worker + retry + exception handling
        - :meth:`_check_soft_loop_signal` — SOFT-mode STOP in worker output
        - :meth:`_invoke_checker` — CheckerAgent.decide with graceful degrades
        - :meth:`_handle_checker_decision` — KILL/CONTINUE/RE_PROMPT branches

        # @trace WL-707
        """
        # Stash the initial prompt so the lazy ``_run_progress_loop``
        # can fetch it on the first iteration without changing the
        # behavioural signature of the public surface.
        self._initial_prompt = initial_prompt

        _log.info("Starting Lifecycle loop session=%s mode=%s", self.state.session_id, self.mode)
        self._run_progress_loop(todo_spec, on_worker_output, on_progress)

        if self.state.iteration >= self.max_iterations and not self.state.stopped:
            self.state.stop_reason = "Max iterations reached"

        if self.verification_callback and self.task_id:
            try:
                self.verification_callback(self.task_id, self.state)
            except Exception as e:
                _log.warning("Verification callback failed: %s", e)

        return self.state


# Aliases for backward compatibility and internal branding
LifecycleLoopController = LifecycleController
RalphWiggumController = LifecycleController
