"""Codex via CLIProxyAPIPlus - claude, codex, gemini, copilot, antigravity through our proxy."""

import os
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

from thegent.agents.base import AgentRunner, RunResult
from thegent.agents.cliproxy_manager import ensure_proxy_running
from thegent.agents.resilience import TransientAgentError, is_retryable, with_retry
from thegent.config import ThegentSettings

# Agent -> default model for CLIProxyAPIPlus. Match fork registry IDs (minimax-m2.5, glm-5).
_PROXY_MODEL: dict[str, str] = {
    "claude": "claude-sonnet-4.5",
    "codex": "gpt-5.3-codex",
    "gemini": "gemini-2.5-flash",
    "copilot": "claude-haiku-4.5",
    "antigravity": "gemini-3-flash",
    "minimax": "minimax-m2.5",
    "glm": "glm-5",
    "cliproxy": "gemini-3-flash",
    "roo": "roo-default",
    "kilo": "kilo-default",
}


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _resolve_codex() -> str:
    """Resolve codex CLI path."""
    found = shutil.which("codex")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "codex"
    if local.exists():
        return str(local)
    return "codex"


@with_retry(max_attempts=4, min_wait=2.0, max_wait=60.0)
def _run_with_retry(
    cmd: list[str],
    prompt: str,
    cwd: Path | None,
    timeout: int,
    env: dict[str, str],
) -> RunResult:
    """Run codex subprocess; raises TransientAgentError on retryable failure."""
    proc = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout + 5,
        cwd=str(cwd) if cwd else None,
        env=env,
    )
    result = RunResult(
        exit_code=proc.returncode,
        stdout=_strip_ansi(proc.stdout),
        stderr=_strip_ansi(proc.stderr),
        timed_out=proc.returncode == 124,
    )
    if result.exit_code != 0 and is_retryable(result):
        raise TransientAgentError(result)
    return result


class CodexProxyRunner(AgentRunner):
    """Runs claude, codex, gemini, copilot, antigravity via Codex CLI pointing at our CLIProxyAPIPlus."""

    def __init__(
        self,
        agent_name: str,
        settings: ThegentSettings | None = None,
        model: str = "",
    ) -> None:
        if agent_name not in _PROXY_MODEL:
            raise ValueError(f"Unknown proxy agent: {agent_name}")
        self.agent_name = agent_name
        self._settings = settings or ThegentSettings()
        self._model = model or _PROXY_MODEL[agent_name]

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
        agent_model: str | None = None,
    ) -> RunResult:
        model = agent_model or self._model
        try:
            base_url = ensure_proxy_running(self._settings)
        except (FileNotFoundError, RuntimeError) as e:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=str(e),
                timed_out=False,
            )

        env = os.environ.copy()
        env["OPENAI_BASE_URL"] = base_url.rstrip("/")
        env["OPENAI_API_KEY"] = "sk-dummy"

        codex_cmd = _resolve_codex()
        cmd = [codex_cmd, "exec", "-", "--skip-git-repo-check"]
        if cwd:
            cmd.extend(["--cd", str(cwd)])
        if use_stream:
            cmd.append("--json")
        if model:
            cmd.extend(["--model", model])
        if mode == "write":
            cmd.extend(["--sandbox", "workspace-write"])
        elif mode == "full":
            cmd.extend(["--full-auto"])

        try:
            return _run_with_retry(cmd, prompt, cwd, timeout, env)
        except TransientAgentError as e:
            return e.result
        except FileNotFoundError:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=(
                    "codex CLI not found. Install: npm i -g @openai/codex\n"
                    "Or add codex to PATH."
                ),
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                exit_code=124,
                stdout="",
                stderr=f"Agent timed out after {timeout}s",
                timed_out=True,
            )
