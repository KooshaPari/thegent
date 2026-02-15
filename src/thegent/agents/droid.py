"""Droid runner - invokes Factory droid exec, OpenAI Codex CLI, or custom CLI backends."""

import os
import re
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from thegent.agents.base import AgentRunner, RunResult


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _resolve_cmd(cmd: str, candidates: list[Path] | None = None) -> str:
    """Resolve command: use as-is if absolute path exists, else try common locations."""
    expanded = str(Path(cmd).expanduser()) if "~" in cmd or "/" in cmd else cmd
    if os.path.isabs(expanded) and Path(expanded).exists():
        return expanded
    if cmd != expanded and Path(expanded).exists():
        return str(Path(expanded).resolve())
    if candidates:
        for c in candidates:
            if c.exists():
                return str(c)
    return cmd


def _resolve_droid_cmd(cmd: str) -> str:
    """Resolve droid command."""
    return _resolve_cmd(
        cmd,
        candidates=[
            Path.home() / ".local" / "bin" / "droid",
            Path.home() / ".factory" / "bin" / "droid",
        ],
    )


def _resolve_codex_cmd(cmd: str) -> str:
    """Resolve Codex CLI command."""
    return _resolve_cmd(
        cmd,
        candidates=[
            Path.home() / ".local" / "bin" / "codex",
            Path.home() / ".codex" / "bin" / "codex",
        ],
    )


class DroidRunner(AgentRunner):
    """Runs droids via Factory droid exec."""

    def __init__(
        self,
        droid_name: str,
        droids_dir: Path,
        droid_cmd: str = "droid",
        model: str = "custom:MiniMax-M2.5",
    ) -> None:
        self.droid_name = droid_name
        self.droids_dir = droids_dir.expanduser().resolve()
        self._droid_cmd = _resolve_droid_cmd(droid_cmd)
        self._model = model

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
    ) -> RunResult:
        """Run droid via droid exec."""
        droid_path = self.droids_dir / f"{self.droid_name}.md"
        if not droid_path.exists():
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=f"Droid not found: {droid_path}",
                timed_out=False,
            )

        droid_content = droid_path.read_text()
        combined = f"{droid_content.rstrip()}\n\n---\nUser request: {prompt}"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(combined)
            tmp_path = f.name

        try:
            cmd = [self._droid_cmd, "exec", "-f", tmp_path, "--model", self._model]
            if cwd:
                cmd.extend(["--cwd", str(cwd)])
            if use_stream:
                cmd.extend(["--output-format", "stream-json"])
            if mode == "write":
                cmd.extend(["--auto", "low"])
            elif mode == "full":
                cmd.extend(["--auto", "high"])

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5,
                cwd=str(cwd) if cwd else None,
                stdin=subprocess.DEVNULL,
            )
            return RunResult(
                exit_code=proc.returncode,
                stdout=_strip_ansi(proc.stdout),
                stderr=_strip_ansi(proc.stderr),
                timed_out=proc.returncode == 124,
            )
        except FileNotFoundError:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=(
                    "droid CLI not found. Install: curl -fsSL https://app.factory.ai/cli | sh\n"
                    "Then add ~/.local/bin to PATH, or set THGENT_DROID_CMD=/path/to/droid"
                ),
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                exit_code=124,
                stdout="",
                stderr=f"Droid timed out after {timeout}s",
                timed_out=True,
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class CodexRunner(AgentRunner):
    """Runs droids via OpenAI Codex CLI (codex exec)."""

    def __init__(
        self,
        droid_name: str,
        droids_dir: Path,
        codex_cmd: str = "codex",
        model: str = "gpt-5.3-codex-spark-xhigh",
    ) -> None:
        self.droid_name = droid_name
        self.droids_dir = droids_dir.expanduser().resolve()
        self._codex_cmd = _resolve_codex_cmd(codex_cmd)
        self._model = model

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
    ) -> RunResult:
        """Run droid via codex exec."""
        droid_path = self.droids_dir / f"{self.droid_name}.md"
        if not droid_path.exists():
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=f"Droid not found: {droid_path}",
                timed_out=False,
            )

        droid_content = droid_path.read_text()
        combined = f"{droid_content.rstrip()}\n\n---\nUser request: {prompt}"

        cmd = [
            self._codex_cmd,
            "exec",
            "-",
            "--model",
            self._model,
        ]
        if cwd:
            cmd.extend(["--cd", str(cwd)])
        if use_stream:
            cmd.extend(["--json"])
        if mode == "write":
            cmd.extend(["--sandbox", "workspace-write"])
        elif mode == "full":
            cmd.extend(["--full-auto"])

        try:
            proc = subprocess.run(
                cmd,
                input=combined,
                capture_output=True,
                text=True,
                timeout=timeout + 5,
                cwd=str(cwd) if cwd else None,
            )
            return RunResult(
                exit_code=proc.returncode,
                stdout=_strip_ansi(proc.stdout),
                stderr=_strip_ansi(proc.stderr),
                timed_out=proc.returncode == 124,
            )
        except FileNotFoundError:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=(
                    "Codex CLI not found. Install: npm i -g @openai/codex or brew install --cask codex\n"
                    "Then add to PATH, or set THGENT_DROID_CODEX_CMD=/path/to/codex"
                ),
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                exit_code=124,
                stdout="",
                stderr=f"Codex timed out after {timeout}s",
                timed_out=True,
            )


class CustomCliRunner(AgentRunner):
    """Runs droids via a generic custom CLI (e.g. claudemax, claudeglm in ~/.local/bin)."""

    def __init__(
        self,
        droid_name: str,
        droids_dir: Path,
        custom_cmd: str,
        model: str = "",
    ) -> None:
        self.droid_name = droid_name
        self.droids_dir = droids_dir.expanduser().resolve()
        # Resolve path if it looks like a path; otherwise use as-is (for PATH lookup)
        if not custom_cmd:
            self._custom_cmd = ""
        elif "/" in custom_cmd or custom_cmd.startswith("~"):
            self._custom_cmd = str(Path(custom_cmd).expanduser().resolve())
        else:
            self._custom_cmd = custom_cmd
        self._model = model

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
    ) -> RunResult:
        """Run droid via custom CLI. Prompt sent via stdin; expects --model and --cd support."""
        droid_path = self.droids_dir / f"{self.droid_name}.md"
        if not droid_path.exists():
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=f"Droid not found: {droid_path}",
                timed_out=False,
            )

        droid_content = droid_path.read_text()
        combined = f"{droid_content.rstrip()}\n\n---\nUser request: {prompt}"

        cmd = [self._custom_cmd]
        if self._model:
            cmd.extend(["--model", self._model])
        if cwd:
            cmd.extend(["--cd", str(cwd)])

        try:
            proc = subprocess.run(
                cmd,
                input=combined,
                capture_output=True,
                text=True,
                timeout=timeout + 5,
                cwd=str(cwd) if cwd else None,
            )
            return RunResult(
                exit_code=proc.returncode,
                stdout=_strip_ansi(proc.stdout),
                stderr=_strip_ansi(proc.stderr),
                timed_out=proc.returncode == 124,
            )
        except FileNotFoundError:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr=(
                    f"Custom CLI not found: {self._custom_cmd}\n"
                    "Set THGENT_DROID_CUSTOM_CMD to path (e.g. ~/.local/bin/claudemax)"
                ),
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                exit_code=124,
                stdout="",
                stderr=f"Custom CLI timed out after {timeout}s",
                timed_out=True,
            )


def get_droid_runner(
    backend: str,
    droid_name: str,
    droids_dir: Path,
    *,
    droid_cmd: str = "droid",
    droid_model: str = "custom:MiniMax-M2.5",
    codex_cmd: str = "codex",
    codex_model: str = "gpt-5.3-codex-spark-xhigh",
    custom_cmd: str = "",
    custom_model: str = "",
) -> AgentRunner:
    """Factory: return the appropriate droid runner for the given backend."""
    backend_lower = backend.lower().strip()
    if backend_lower == "codex":
        return CodexRunner(
            droid_name,
            droids_dir,
            codex_cmd=codex_cmd,
            model=codex_model,
        )
    if backend_lower == "custom" and custom_cmd:
        return CustomCliRunner(
            droid_name,
            droids_dir,
            custom_cmd=custom_cmd,
            model=custom_model or droid_model,
        )
    return DroidRunner(
        droid_name,
        droids_dir,
        droid_cmd=droid_cmd,
        model=droid_model,
    )
