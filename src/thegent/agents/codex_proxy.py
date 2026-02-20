"""Codex via CLIProxyAPIPlus - claude, codex, gemini, copilot, antigravity through our proxy. Native gemini/copilot swapped to Codex (proxy API)."""

import logging
import os
import shutil
import subprocess
import threading
import time
from collections.abc import Callable
from pathlib import Path

from thegent.agents.base import AgentRunner, RunResult
from thegent.agents.cliproxy_manager import ensure_proxy_running
from thegent.agents.resilience import TransientAgentError, is_retryable, with_retry
from thegent.config import ThegentSettings
from thegent.discovery import _is_triggered_by_agent_process
from thegent.infra.power import wrap_with_caffeinate
from thegent.routing.models import TaskMetadata
from thegent.routing.provider_types import ExecutionPath, get_execution_path
from thegent.utils import strip_ansi

logger = logging.getLogger(__name__)

# Agent -> default model. All proxy agents use CLIProxyAPIPlus (merged into one proxy).
_PROXY_MODEL: dict[str, str] = {
    "claude": "claude-opus-4.6",
    "codex": "gpt-5.3-codex-spark",
    "gemini": "gemini-3-flash",
    "copilot": "gpt-5-mini",
    "antigravity": "gemini-3-flash",
    "minimax": "minimax-m2.5",
    "glm": "glm-5",
    "cliproxy": "gemini-3-flash",  # generic proxy fallback
    "kilo": "minimax-m2.5",
    "kiro": "claude-haiku-4.5",
    "nim": "step-3.5-flash",
    "zen": "glm-5",
    "summarizer": "gemini-3-flash",
}


def _resolve_codex() -> str:
    """Resolve codex CLI path."""
    found = shutil.which("codex")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "codex"
    if local.exists():
        return str(local)
    return "codex"


def _run_with_activity_monitoring(
    cmd: list[str],
    prompt: str,
    cwd: Path | None,
    env: dict[str, str],
    max_idle_seconds: int,
    max_wall_time: int,
    on_stdout: Callable[[str], None] | None,
    on_stderr: Callable[[str], None] | None,
) -> RunResult:
    """Run codex with activity-based hang detection. Kills only when no stdout/stderr for max_idle_seconds (hung), or when max_wall_time exceeded (if > 0)."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1,
        cwd=str(cwd) if cwd else None,
        env=env,
    )
    if proc.stdin:
        proc.stdin.write(prompt)
        proc.stdin.close()

    out_lines: list[str] = []
    err_lines: list[str] = []
    last_activity = {"t": time.monotonic()}
    lock = threading.Lock()

    def _on_chunk(_: str) -> None:
        with lock:
            last_activity["t"] = time.monotonic()

    def _drain(stream, collector: list[str], cb: Callable[[str], None] | None) -> None:
        for line in stream:
            clean = strip_ansi(line)
            collector.append(clean)
            _on_chunk(clean)
            if cb:
                cb(clean.rstrip("\n"))

    t_out = threading.Thread(target=_drain, args=(proc.stdout, out_lines, on_stdout), daemon=True)
    t_err = threading.Thread(target=_drain, args=(proc.stderr, err_lines, on_stderr), daemon=True)
    t_out.start()
    t_err.start()

    start = time.monotonic()
    rc: int | None = None
    kill_reason: str | None = None

    while True:
        ret = proc.poll()
        if ret is not None:
            rc = ret
            break

        now = time.monotonic()
        with lock:
            idle = now - last_activity["t"]
        elapsed = now - start

        if max_wall_time > 0 and elapsed >= max_wall_time:
            proc.kill()
            rc = 124
            kill_reason = f"absolute wall time ({max_wall_time}s)"
            break
        if idle >= max_idle_seconds:
            proc.kill()
            rc = 124
            kill_reason = f"no output for {max_idle_seconds}s (hung)"
            break

        time.sleep(0.5)

    t_out.join(timeout=2)
    t_err.join(timeout=2)

    stderr_msg = ""
    if kill_reason:
        stderr_msg = f"Agent stopped: {kill_reason}"
        if err_lines:
            stderr_msg = "".join(err_lines) + "\n" + stderr_msg

    result = RunResult(
        exit_code=rc if rc is not None else 1,
        stdout="".join(out_lines),
        stderr=stderr_msg or "".join(err_lines),
        timed_out=rc == 124,
    )
    return result


@with_retry(max_attempts=4, min_wait=2.0, max_wait=60.0)
def _run_with_retry(
    cmd: list[str],
    prompt: str,
    cwd: Path | None,
    timeout: int,
    env: dict[str, str],
    max_idle_seconds: int,
    max_wall_time: int,
    live_output: bool = False,
    on_stdout: Callable[[str], None] | None = None,
    on_stderr: Callable[[str], None] | None = None,
) -> RunResult:
    """Run codex subprocess with activity-based hang detection; raises TransientAgentError on retryable failure."""
    effective_wall = max(0, max_wall_time)
    result = _run_with_activity_monitoring(
        cmd,
        prompt,
        cwd,
        env,
        max_idle_seconds=max_idle_seconds,
        max_wall_time=effective_wall,
        on_stdout=on_stdout if live_output else None,
        on_stderr=on_stderr if live_output else None,
    )
    if result.exit_code != 0 and is_retryable(result):
        raise TransientAgentError(result)
    return result


class CodexProxyRunner(AgentRunner):
    """Runs claude, codex, gemini, copilot, antigravity via Codex CLI pointing at our CLIProxyAPIPlus. gemini/copilot route via proxy (no native CLI)."""

    def __init__(
        self,
        agent_name: str,
        settings: ThegentSettings | None = None,
        model: str = "",
        use_litellm_router: bool | None = None,
    ) -> None:
        if agent_name not in _PROXY_MODEL:
            raise ValueError(f"Unknown proxy agent: {agent_name}")
        self.agent_name = agent_name
        self._settings = settings or ThegentSettings()
        self._model = model or _PROXY_MODEL[agent_name]
        self._use_litellm_router = (
            use_litellm_router
            if use_litellm_router is not None
            else (os.environ.get("THGENT_USE_LITELLM_ROUTER", "0") == "1")
        )

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
        enable_search: bool = True,
        run_id: str | None = None,
        env: dict[str, str] | None = None,
    ) -> RunResult:
        model = agent_model or self._model

        # Route via LiteLLM Router if enabled and not zen
        if self._use_litellm_router and self.agent_name != "zen":
            return self._run_via_litellm_router(
                prompt, cwd, mode, timeout, model, use_stream, live_output, on_stdout, on_stderr, env=env
            )

        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        if self.agent_name == "zen":
            base_url = (self._settings.zen_base_url or "https://api.opencode.ai").rstrip("/")
            api_key = (
                self._settings.zen_api_key or os.environ.get("OPENCODE_API_KEY") or os.environ.get("ZEN_API_KEY") or ""
            ).strip()
            if not api_key:
                return RunResult(
                    exit_code=1,
                    stdout="",
                    stderr=(
                        "Zen API key missing. Set THGENT_ZEN_API_KEY (or OPENCODE_API_KEY / ZEN_API_KEY) "
                        "to use provider=zen."
                    ),
                    timed_out=False,
                )
            full_env["OPENAI_BASE_URL"] = base_url
            full_env["OPENAI_API_KEY"] = api_key
        else:
            try:
                base_url = ensure_proxy_running(self._settings)
            except (FileNotFoundError, RuntimeError) as e:
                return RunResult(
                    exit_code=1,
                    stdout="",
                    stderr=str(e),
                    timed_out=False,
                )
            full_env["OPENAI_BASE_URL"] = base_url.rstrip("/")
            full_env["OPENAI_API_KEY"] = "sk-dummy"

        codex_cmd = _resolve_codex()
        cmd = [codex_cmd, "exec", "-", "--skip-git-repo-check"]
        if not _is_triggered_by_agent_process():
            cmd.append("--dangerously-bypass-approvals-and-sandbox")
        # codex no longer supports a top-level --search flag; leave search disabled by default
        # if enable_search:
        #     cmd.append("--search")
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
            return _run_with_retry(
                cmd,
                prompt,
                cwd,
                timeout,
                full_env,
                max_idle_seconds=self._settings.max_idle_seconds,
                max_wall_time=self._settings.max_wall_time,
                live_output=live_output,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
            )
        except TransientAgentError as e:
            return e.result
        except FileNotFoundError:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=("codex CLI not found. Install: npm i -g @openai/codex\nOr add codex to PATH."),
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                exit_code=124,
                stdout="",
                stderr=f"Agent timed out after {timeout}s",
                timed_out=True,
            )

    def _run_via_litellm_router(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        model: str,
        use_stream: bool,
        live_output: bool,
        on_stdout: Callable[[str], None] | None,
        on_stderr: Callable[[str], None] | None,
        env: dict[str, str] | None = None,
    ) -> RunResult:
        """Run via LiteLLM Router for Codex CLI compatibility."""
        try:
            from thegent.routing.litellm_router import get_enhanced_router

            router = get_enhanced_router()

            # Use model as-is; it should match a model alias in our catalog
            # which is what LiteLLM model_list uses for model_name.
            model_to_use = model

            result = router.route(prompt, model=model_to_use, stream=use_stream, timeout=timeout)

            if not result.success:
                return RunResult(
                    exit_code=1,
                    stdout="",
                    stderr=result.error or "Routing failed",
                    timed_out=False,
                )

            # Handle response
            if use_stream:
                # For Codex, we need to collect the stream into a single response
                # or handle it as Codex expects. Since we're emulating Codex,
                # we'll collect it for now unless we implement full SSE.
                stdout_collector = []
                for chunk in result.response:
                    content = ""
                    if hasattr(chunk, "choices") and chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            content = delta.content
                    elif isinstance(chunk, dict):
                        # Handle dict response (from some LiteLLM adapters)
                        choices = chunk.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")

                    if content:
                        stdout_collector.append(content)
                        if on_stdout:
                            on_stdout(content)

                return RunResult(
                    exit_code=0,
                    stdout="".join(stdout_collector),
                    stderr="",
                    timed_out=False,
                )
            content = ""
            if hasattr(result.response, "choices") and result.response.choices:
                content = result.response.choices[0].message.content
            elif isinstance(result.response, dict):
                choices = result.response.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    content = message.get("content", "")

            return RunResult(
                exit_code=0,
                stdout=content or "",
                stderr="",
                timed_out=False,
            )

        except Exception as e:
            logger.error("LiteLLM Router execution failed: %s", e, exc_info=True)
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=f"LiteLLM Router execution failed: {e}",
                timed_out=False,
            )

    def run_with_metadata(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        *,
        metadata: TaskMetadata | None = None,
        use_stream: bool = True,
        live_output: bool = False,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
        enable_search: bool = True,
        run_id: str | None = None,
    ) -> RunResult:
        """Run agent using resolved routing from TaskMetadata.

        This method consumes resolved_provider and resolved_model_alias
        from the routing classification.

        Args:
            prompt: User prompt
            cwd: Working directory
            mode: Execution mode (read/write/full)
            timeout: Timeout in seconds
            metadata: TaskMetadata with resolved routing

        Returns:
            RunResult from execution
        """
        # Determine provider and model from metadata
        provider = metadata.resolved_provider if metadata else self.agent_name
        model = metadata.resolved_model_alias if metadata else self._model

        # Determine execution path
        exec_path = get_execution_path(provider)

        if exec_path == ExecutionPath.NATIVE_CLI:
            return self._execute_native_cli(prompt, cwd, mode, timeout, model)
        if exec_path == ExecutionPath.LITELLM_API:
            return self._execute_litellm_api(prompt, cwd, mode, timeout, provider, model)
        # CLIProxyAPIPlus path (default)
        return self.run(prompt, cwd, mode, timeout, agent_model=model, use_stream=use_stream)

    def _execute_native_cli(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        model: str,
    ) -> RunResult:
        """Execute via native codex CLI (for codex provider)."""
        # Current implementation uses codex CLI already
        return self.run(prompt, cwd, mode, timeout, agent_model=model)

    def _execute_litellm_api(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        provider: str,
        model: str,
    ) -> RunResult:
        """Execute via LiteLLM direct API (for API key providers).

        Uses litellm.completion() to call providers directly without
        going through the CLIProxyAPIPlus proxy. Supports providers
        like minimax, glm, nim, kilo that have API keys.

        Args:
            prompt: User prompt to send to the model
            cwd: Working directory (not used for API calls, kept for signature compatibility)
            mode: Execution mode (not used for API calls, kept for signature compatibility)
            timeout: Timeout in seconds for the API call
            provider: Provider name (e.g., "minimax", "glm")
            model: Model name/alias (e.g., "minimax-m2.5")

        Returns:
            RunResult with the model response or error
        """
        try:
            from litellm import completion
        except ImportError as e:
            logger.error(f"litellm not installed: {e}")
            return RunResult(
                exit_code=1,
                stdout="",
                stderr="litellm package not installed. Install with: pip install litellm",
                timed_out=False,
            )

        # Build model string in LiteLLM format: "provider/model"
        model_string = f"{provider}/{model}"

        # Get API key environment variable name for this provider
        api_key_env = self._get_api_key_env(provider)
        api_key = os.environ.get(api_key_env)

        if not api_key:
            logger.error(f"API key not found for provider {provider} (env: {api_key_env})")
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=f"API key not found. Set {api_key_env} environment variable.",
                timed_out=False,
            )

        logger.info(f"Calling LiteLLM API: {model_string}")

        try:
            response = completion(
                model=model_string,
                messages=[{"role": "user", "content": prompt}],
                api_key=api_key,
                timeout=timeout,
            )

            # Extract response content from LiteLLM response
            # LiteLLM returns a ModelResponse with choices containing message content
            content = response.choices[0].message.content

            logger.info(f"LiteLLM API call successful: {model_string}")
            return RunResult(
                exit_code=0,
                stdout=content or "",
                stderr="",
                timed_out=False,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"LiteLLM API call failed: {error_msg}")

            # Check for timeout-related errors
            is_timeout = "timeout" in error_msg.lower() or "timed out" in error_msg.lower()

            return RunResult(
                exit_code=1,
                stdout="",
                stderr=f"LiteLLM API error: {error_msg}",
                timed_out=is_timeout,
            )

    @staticmethod
    def _get_api_key_env(provider: str) -> str:
        """Get environment variable name for provider API key.

        Args:
            provider: Provider name (e.g., "minimax", "glm")

        Returns:
            Environment variable name for the API key
        """
        mapping = {
            "minimax": "MINIMAX_API_KEY",
            "nim": "NVIDIA_API_KEY",
            "glm": "ZHIPU_API_KEY",
            "kilo": "KILO_API_KEY",
        }
        return mapping.get(provider, f"{provider.upper()}_API_KEY")
