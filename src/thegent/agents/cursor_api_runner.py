"""Cursor via cursor-api (wisdgod) - OpenAI-compatible HTTP backend."""

import os
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

from thegent.agents.base import AgentRunner, RunResult
from thegent.agents.resilience import TransientAgentError, is_retryable, with_retry
from thegent.config import ThegentSettings

_PROXY_MODEL = "claude-4.5-opus-high-thinking"


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


def _is_cursor_api_reachable(base_url: str, token: str, timeout: float = 3.0) -> bool:
    """Check if cursor-api is reachable (GET /v1/models)."""
    import urllib.request

    url = f"{base_url.rstrip('/')}/v1/models"
    req = urllib.request.Request(url, method="GET")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as _:
            return True
    except Exception:
        return False


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


class CursorApiRunner(AgentRunner):
    """Runs Cursor models via cursor-api (wisdgod) - OpenAI-compatible HTTP backend."""

    def __init__(
        self,
        settings: ThegentSettings | None = None,
        model: str = "",
    ) -> None:
        self._settings = settings or ThegentSettings()
        self._model = model or _PROXY_MODEL

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
        base_url = self._settings.cursor_api_url.rstrip("/")
        token = self._settings.cursor_api_token or os.environ.get("THGENT_CURSOR_API_TOKEN", "")

        if not _is_cursor_api_reachable(base_url, token):
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=(
                    "cursor-api not reachable. Start cursor-api (wisdgod) at "
                    f"{base_url} or set THGENT_CURSOR_API_URL. "
                    "Set THGENT_CURSOR_API_TOKEN for auth."
                ),
                timed_out=False,
            )

        env = os.environ.copy()
        env["OPENAI_BASE_URL"] = base_url
        env["OPENAI_API_KEY"] = token or "sk-dummy"

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
