"""ExecutionEngine for coordinating agent runs with MAIF, policies, and resource management."""

import contextlib
import logging
from pathlib import Path
from typing import Any

from thegent.agents.base import AgentRunner, RunResult
from thegent.config import ThegentSettings
from thegent.execution import Auditor, RunMeta
from thegent.maif import MAIFRunner
from thegent.routing.route_executor import (
    RoutingDecision,
    RoutingOrchestratorBridge,
    make_routing_decision_from_factors,
)

_log = logging.getLogger(__name__)

# Global orchestrator for multi-agent routing coordination
_orchestrator: RoutingOrchestratorBridge | None = None


def get_orchestrator() -> RoutingOrchestratorBridge:
    """Get or create the global routing orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RoutingOrchestratorBridge(policy="MajorityWins")
    return _orchestrator


class ExecutionEngine:
    """Orchestrates agent execution with integrated MAIF artifact generation.

    This engine coordinates:
    1. Routing decision (Pareto router with hysteresis)
    2. Pre-execution signing (MAIF run_start)
    3. Agent execution (via AgentRunner)
    4. Post-execution artifact generation (MAIF run_complete)
    5. Routing audit logging (Phase 3.3)
    """

    def __init__(self, settings: ThegentSettings | None = None) -> None:
        self.settings = settings or ThegentSettings()
        # Initialize auditor with the registry path from settings
        registry_path = self.settings.session_dir / "run_registry.jsonl"
        self.auditor = Auditor(registry_path)
        self._maif_runner = MAIFRunner()
        self._orchestrator = get_orchestrator()

    def _determine_complexity(self, run_meta: RunMeta) -> str:
        """Determine task complexity from run metadata for routing.

        Uses heuristics based on prompt length, known agent types, and mode.
        """
        # Default to moderate complexity
        complexity = "moderate"

        # Heuristic: longer prompts often indicate more complex tasks
        prompt_len = len(run_meta.prompt or "")
        if prompt_len > 5000:
            complexity = "complex"
        elif prompt_len > 2000:
            complexity = "moderate"
        elif prompt_len < 500:
            complexity = "simple"

        # Agent type can influence complexity
        agent = (run_meta.agent or "").lower()
        if "review" in agent or "audit" in agent:
            complexity = "complex"
        elif "read" in agent or "info" in agent:
            complexity = "simple"

        return complexity

    def _make_routing_decision(self, run_meta: RunMeta) -> RoutingDecision:
        """Make a routing decision based on task factors (Phase 3.1)."""
        complexity = self._determine_complexity(run_meta)
        decision = make_routing_decision_from_factors(
            complexity=complexity,
            cost_sensitive=False,
            latency_critical=False,
            settings=self.settings,
        )

        # Record decision in orchestrator for multi-agent coordination (Phase 3.2)
        agent_id = run_meta.run_id or "unknown"
        self._orchestrator.record_decision(agent_id, decision)

        _log.debug(
            "ExecutionEngine: Routing decision for %s: mode=%s, risk=%.2f",
            agent_id,
            decision.mode,
            decision.risk_score,
        )

        return decision

    def execute(
        self,
        runner: AgentRunner,
        run_meta: RunMeta,
        cwd: Path | None = None,
        mode: str = "write",
        timeout: int = 90,
        skip_routing: bool = False,
        **kwargs: Any,
    ) -> tuple[RunResult, RoutingDecision]:
        """Execute an agent task with routing and generate MAIF artifacts.

        Args:
            runner: The AgentRunner implementation to use.
            run_meta: Metadata for the run (run_id, prompt, owner, etc.).
            cwd: Working directory for the agent.
            mode: Execution mode (e.g. "read-only", "write").
            timeout: Time budget in seconds.
            skip_routing: If True, skip routing decision (for internal use).
            **kwargs: Additional options for the runner.

        Returns:
            Tuple of (RunResult, RoutingDecision).
        """

        # 0. Make routing decision (Phase 3.1 - Route Executor)
        if skip_routing:
            routing_decision = RoutingDecision(
                mode="Lifecycle",
                risk_score=0.0,
                rationale="routing skipped",
            )
        else:
            routing_decision = self._make_routing_decision(run_meta)

        # 1. Record run start (MAIF lifecycle + auditor signing)
        with contextlib.suppress(Exception):
            self._maif_runner.record_run_start(
                run_id=run_meta.run_id,
                owner=run_meta.owner or "unknown",
                prompt=run_meta.prompt or "",
                agent=run_meta.agent or "unknown",
            )
        try:
            self.auditor.sign_run(run_meta)
            _log.debug("ExecutionEngine: Signed run start for %s", run_meta.run_id)
        except Exception as e:
            _log.debug("ExecutionEngine: Failed to sign run start for %s: %s", run_meta.run_id, e)

        # 2. Run the agent (using routed provider based on decision.mode)
        # The runner implementation should use routing_decision.mode to determine provider
        _log.info(
            "ExecutionEngine: Starting execution for %s (agent=%s, route=%s)",
            run_meta.run_id,
            run_meta.agent,
            routing_decision.mode,
        )
        result = runner.run(prompt=run_meta.prompt, cwd=cwd, mode=mode, timeout=timeout, **kwargs)

        # 3. Record run end (MAIF lifecycle)
        status = "completed" if result.exit_code == 0 else ("timed_out" if result.timed_out else "failed")
        output_summary = (result.stdout or result.stderr or "")[:500]
        self._maif_runner.record_run_end(
            run_id=run_meta.run_id,
            status=status,
            output_summary=output_summary,
        )

        # 4. Generate and persist auditor artifact (run registry)
        try:
            artifact = self.auditor.generate_maif_artifact(run_meta, output=result.stdout)
            self.auditor.persist_maif_artifact(self.settings.session_dir, artifact)
            _log.debug("ExecutionEngine: Generated completion artifact for %s", run_meta.run_id)
        except Exception as e:
            _log.debug("ExecutionEngine: Failed to generate MAIF artifact for %s: %s", run_meta.run_id, e)

        return result, routing_decision
