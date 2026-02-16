"""Direct agent invocation - cursor, claude, copilot, codex, gemini via their CLIs."""

import os
import re
import shutil
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from thegent.agents.base import AgentRunner, RunResult
from thegent.agents.resilience import TransientAgentError, is_retryable, with_retry

PROCESS_TIMEOUT_SECS = 3600

_NOISY_STDERR_PATTERNS = (
    r"\(node:\d+\) \[DEP0040\].*punycode",
    r"Session cleanup disabled:",
    r"Hook registry initialized with \d+ hook entries",
    r'Error executing tool run_shell_command: Tool "run_shell_command" not found',
    r"Use `node --trace-deprecation",
    r"^Loaded cached credentials\.$",
    r"^\[OK\] ",
    r"^\[INFO\] ",
    r"^Total usage est:",
    r"^Total duration ",
    r"^Total code changes:",
    r"^Usage by model:",
    r"^Copilot CLI available",
    r"^Commit:",
)


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _filter_noisy_stderr(text: str) -> str:
    if not text:
        return text
    lines = []
    for line in text.splitlines():
        if any(re.search(p, line) for p in _NOISY_STDERR_PATTERNS):
            continue
        lines.append(line)
    return "\n".join(lines).rstrip()


def _resolve_cli(cmd: str, name: str) -> str:
    """Resolve CLI path: env override, absolute path, which, or ~/.local/bin."""
    # cursor-agent: THGENT_CURSOR_AGENT_CMD (underscore, shell-friendly)
    env_key = "THGENT_CURSOR_AGENT_CMD" if name == "cursor-agent" else f"THGENT_{name.upper().replace('-', '_')}_CMD"
    env_val = os.environ.get(env_key)
    if env_val:
        expanded = str(Path(env_val).expanduser())
        if Path(expanded).exists():
            return expanded
        return env_val
    if "/" in cmd or "~" in cmd:
        expanded = str(Path(cmd).expanduser())
        if Path(expanded).exists():
            return expanded
    found = shutil.which(cmd)
    if found:
        return found
    # cursor-agent: fallback to cursor if cursor-agent not on PATH (Cursor IDE CLI)
    if name == "cursor-agent":
        fallback = shutil.which("cursor")
        if fallback:
            return fallback
    local = Path.home() / ".local" / "bin" / name
    if local.exists():
        return str(local)
    if name == "cursor-agent":
        local_cursor = Path.home() / ".local" / "bin" / "cursor"
        if local_cursor.exists():
            return str(local_cursor)
    return cmd


# Agent name -> (cli_cmd, uses_stdin, stream_arg)
_AGENT_CLI: dict[str, tuple[str, bool, str]] = {
    "cursor-agent": ("cursor-agent", False, "--print"),
    "claude": ("claude", True, "--output-format stream-json"),
    "copilot": ("copilot", False, "--stream on"),
    "codex": ("codex", True, "--json"),
    "gemini": ("gemini", False, "--output-format stream-json"),
}


class DirectAgentRunner(AgentRunner):
    """Invokes cursor, claude, copilot, codex, gemini directly via their CLIs."""

    def __init__(
        self,
        agent_name: str,
        cli_cmd: str | None = None,
        default_model: str = "",
    ) -> None:
        self.agent_name = agent_name
        spec = _AGENT_CLI.get(agent_name)
        if not spec:
            raise ValueError(f"Unknown direct agent: {agent_name}")
        self._cli_name, self._uses_stdin, self._stream_arg = spec
        self._cli_cmd = _resolve_cli(cli_cmd or self._cli_name, self._cli_name)
        self._default_model = default_model

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
        model = agent_model or self._default_model

        # WP-Y6: OTel GenAI Instrumentation
        from thegent.observability.otel_instrumentation import instrument_genai_call

        system_map = {
            "claude": "anthropic",
            "gemini": "google",
            "codex": "openai",
            "copilot": "github",
            "cursor-agent": "cursor",
        }

        with instrument_genai_call(
            agent_name=self.agent_name,
            model=model,
            system=system_map.get(self.agent_name),
        ) as span:
            cmd = self._build_cmd(cwd, use_stream, model, mode)
            stdin_input = prompt if self._uses_stdin else None
            if not self._uses_stdin:
                if self.agent_name == "gemini":
                    cmd.extend(["-p", prompt])
                elif self.agent_name == "copilot":
                    cmd.extend(["-p", prompt])  # copilot requires -p for non-interactive
                else:
                    cmd.append(prompt)

            try:
                if live_output:
                    result = self._run_live(cmd, cwd, timeout, stdin_input, on_stdout, on_stderr)
                else:
                    result = self._run_capture(cmd, cwd, timeout, stdin_input)

                span.set_attribute("exit_code", result.exit_code)
                return result
            except FileNotFoundError:
                env_hint = (
                    "THGENT_CURSOR_AGENT_CMD"
                    if self._cli_name == "cursor-agent"
                    else f"THGENT_{self._cli_name.upper().replace('-', '_')}_CMD"
                )
                res = RunResult(
                    exit_code=1,
                    stdout="",
                    stderr=(
                        f"{self._cli_name} not found. Install and add to PATH, or set {env_hint}=/path/to/{self._cli_name}"
                    ),
                    timed_out=False,
                )
                span.set_attribute("exit_code", 1)
                cast("Any", span).record_exception(FileNotFoundError(res.stderr))
                return res
            except subprocess.TimeoutExpired:
                res = RunResult(
                    exit_code=124,
                    stdout="",
                    stderr=f"Agent timed out after {timeout}s",
                    timed_out=True,
                )
                span.set_attribute("exit_code", 124)
                span.set_attribute("timed_out", True)
                return res

    def _build_cmd(
        self,
        cwd: Path | None,
        use_stream: bool,
        model: str,
        mode: str,
    ) -> list[str]:
        cmd = [self._cli_cmd]

        if self.agent_name == "codex":
            cmd.extend(["exec", "-", "--skip-git-repo-check"])
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
            return cmd

        if self.agent_name == "cursor-agent":
            cmd.extend(["--print"])
            if mode != "read-only":
                cmd.append("--trust")
            if cwd:
                cmd.extend(["--workspace", str(cwd)])
            if model:
                cmd.extend(["--model", model])
            return cmd

        if self.agent_name == "claude":
            cmd.extend(["--print"])
            if mode != "read-only":
                cmd.append("--dangerously-skip-permissions")
            if cwd:
                cmd.extend(["--add-dir", str(cwd)])
            if use_stream:
                cmd.extend(self._stream_arg.split())
                cmd.append("--verbose")  # required with --print + stream-json
            if model:
                cmd.extend(["--model", model])
            return cmd

        if self.agent_name == "copilot":
            if cwd:
                cmd.extend(["--add-dir", str(cwd)])
            if mode != "read-only":
                cmd.append("--allow-all-tools")
            if use_stream:
                cmd.extend(self._stream_arg.split())
            if model:
                cmd.extend(["--model", model])
            return cmd

        if self.agent_name == "gemini":
            if cwd:
                cmd.extend(["--include-directories", str(cwd)])
            if use_stream:
                cmd.extend(["-o", "stream-json"])
            if model:
                cmd.extend(["-m", model])
            return cmd

        return cmd

    def _run_capture(
        self,
        cmd: list[str],
        cwd: Path | None,
        timeout: int,
        stdin_input: str | None,
    ) -> RunResult:
        try:
            return self._run_capture_attempt(cmd, cwd, timeout, stdin_input)
        except TransientAgentError as e:
            return e.result

    @with_retry(max_attempts=4, min_wait=2.0, max_wait=60.0)
    def _run_capture_attempt(
        self,
        cmd: list[str],
        cwd: Path | None,
        timeout: int,
        stdin_input: str | None,
    ) -> RunResult:
        kwargs: dict = {
            "capture_output": True,
            "text": True,
            "timeout": min(timeout + 10, PROCESS_TIMEOUT_SECS + 10),
            "cwd": str(cwd) if cwd else None,
        }
        if stdin_input is not None:
            kwargs["input"] = stdin_input
        else:
            kwargs["stdin"] = subprocess.DEVNULL
        proc = subprocess.run(cmd, check=False, **cast("Any", kwargs))
        result = RunResult(
            exit_code=proc.returncode,
            stdout=_strip_ansi(proc.stdout),
            stderr=_filter_noisy_stderr(_strip_ansi(proc.stderr)),
            timed_out=proc.returncode == 124,
        )
        if result.exit_code != 0 and is_retryable(result):
            raise TransientAgentError(result)
        return result

    def _run_live(
        self,
        cmd: list[str],
        cwd: Path | None,
        timeout: int,
        stdin_input: str | None,
        on_stdout: Callable[[str], None] | None,
        on_stderr: Callable[[str], None] | None,
    ) -> RunResult:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE if stdin_input else subprocess.DEVNULL,
            text=True,
            bufsize=1,
            cwd=str(cwd) if cwd else None,
        )
        if stdin_input and proc.stdin:
            proc.stdin.write(stdin_input)
            proc.stdin.close()
        out_lines: list[str] = []
        err_lines: list[str] = []

        def _drain(stream, collector: list[str], cb: Callable[[str], None] | None) -> None:
            for line in stream:
                clean = _strip_ansi(line)
                collector.append(clean)
                if cb:
                    cb(clean.rstrip("\n"))

        t_out = threading.Thread(target=_drain, args=(proc.stdout, out_lines, on_stdout), daemon=True)
        t_err = threading.Thread(target=_drain, args=(proc.stderr, err_lines, on_stderr), daemon=True)
        t_out.start()
        t_err.start()
        try:
            rc = proc.wait(timeout=PROCESS_TIMEOUT_SECS + 10)
        except subprocess.TimeoutExpired:
            proc.kill()
            rc = 124
        t_out.join(timeout=1)
        t_err.join(timeout=1)
        return RunResult(
            exit_code=rc,
            stdout="".join(out_lines),
            stderr=_filter_noisy_stderr("".join(err_lines)),
            timed_out=rc == 124,
        )
