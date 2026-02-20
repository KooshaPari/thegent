"""Base agent runner interface."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunResult:
    """Result of an agent run."""

    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


class AgentRunner:
    """Base interface for agent runners."""

    def run(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        *,
        use_stream: bool = True,
        live_output: bool = False,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
        env: dict[str, str] | None = None,
    ) -> RunResult:
        """Run the agent with the given prompt and options."""
        raise NotImplementedError
