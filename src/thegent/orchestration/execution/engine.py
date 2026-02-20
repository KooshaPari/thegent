"""ExecutionEngine for coordinating agent runs with MAIF, policies, and resource management."""

import logging
from pathlib import Path
from typing import Any, Optional

from thegent.agents.base import AgentRunner, RunResult
from thegent.config import ThegentSettings
from thegent.execution import Auditor, RunMeta
from thegent.maif import MAIFRunner

_log = logging.getLogger(__name__)


class ExecutionEngine:
    """Orchestrates agent execution with integrated MAIF artifact generation.

    This engine coordinates:
    1. Pre-execution signing (MAIF run_start)
    2. Agent execution (via AgentRunner)
    3. Post-execution artifact generation (MAIF run_complete)
    """

    def __init__(self, settings: ThegentSettings | None = None) -> None:
        self.settings = settings or ThegentSettings()
        # Initialize auditor with the registry path from settings
        registry_path = self.settings.session_dir / "run_registry.jsonl"
        self.auditor = Auditor(registry_path)
        self._maif_runner = MAIFRunner()

    def execute(
        self,
        runner: AgentRunner,
        run_meta: RunMeta,
        cwd: Path | None = None,
        mode: str = "write",
        timeout: int = 90,
        **kwargs: Any,
    ) -> RunResult:
        """Execute an agent task and generate MAIF artifacts.

        Args:
            runner: The AgentRunner implementation to use.
            run_meta: Metadata for the run (run_id, prompt, owner, etc.).
            cwd: Working directory for the agent.
            mode: Execution mode (e.g. "read-only", "write").
            timeout: Time budget in seconds.
            **kwargs: Additional options for the runner.

        Returns:
            RunResult from the agent execution.
        """

        # 1. Record run start (MAIF lifecycle + auditor signing)
        try:
            self._maif_runner.record_run_start(
                run_id=run_meta.run_id,
                owner=run_meta.owner or "unknown",
                prompt=run_meta.prompt or "",
                agent=run_meta.agent or "unknown",
            )
        except Exception:
            pass
        try:
            self.auditor.sign_run(run_meta)
            _log.debug("ExecutionEngine: Signed run start for %s", run_meta.run_id)
        except Exception as e:
            _log.debug("ExecutionEngine: Failed to sign run start for %s: %s", run_meta.run_id, e)

        # 2. Run the agent
        _log.info("ExecutionEngine: Starting execution for %s (agent=%s)", run_meta.run_id, run_meta.agent)
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

        return result
