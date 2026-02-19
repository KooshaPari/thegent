"""Role-based agent runner - wraps another runner and injects a system prompt."""

from collections.abc import Callable
from pathlib import Path
from typing import Optional

from thegent.agents.base import AgentRunner, RunResult
from thegent.orchestration.tasks import TaskRole, get_role_prompt


class RoleAgentRunner(AgentRunner):
    """Wraps another runner and injects a role-based system prompt."""

    def __init__(self, role: TaskRole, base_runner: AgentRunner) -> None:
        self.role = role
        self.base_runner = base_runner

    def run(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        *,
        use_stream: bool = True,
        live_output: bool = False,
        on_stdout: Callable[[str], Optional[None]] | None = None,
        on_stderr: Callable[[str], Optional[None]] | None = None,
        run_id: str | None = None,
    ) -> RunResult:
        role_prompt = get_role_prompt(self.role)
        full_prompt = f"[ROLE: {self.role.value.upper()}]\n{role_prompt}\n\nTASK:\n{prompt}"

        return self.base_runner.run(
            prompt=full_prompt,
            cwd=cwd,
            mode=mode,
            timeout=timeout,
            use_stream=use_stream,
            live_output=live_output,
            on_stdout=on_stdout,
            on_stderr=on_stderr,
            run_id=run_id,
        )
