"""Shared helpers for dex CLI command assembly and parsing."""

from __future__ import annotations

import logging
import shutil
from collections.abc import Mapping
from pathlib import Path

_LOG = logging.getLogger(__name__)


def canonical_model(model_alias: str, alias_map: Mapping[str, str]) -> str:
    """Normalize a model alias to its canonical identifier."""
    return alias_map.get(model_alias.lower(), model_alias)


def resolve_codex_cli_path() -> str | None:
    """Find the codex binary using PATH first, then ~/.local/bin fallback."""
    codex_path = shutil.which("codex")
    if codex_path:
        return codex_path
    local = Path.home() / ".local" / "bin" / "codex"
    if local.exists():
        return str(local)
    return None


def build_codex_exec_command(
    codex_path: str,
    model: str,
    prompt: str,
    *,
    cd: Path | None = None,
    add_dir: list[str] | None = None,
    sandbox: str | None = None,
    full_auto: bool = False,
    dangerously_bypass: bool = True,
    bypass_approved: bool = False,
    bypass_flag: str,
) -> list[str]:
    """Build the codex exec command preserving dex flag semantics."""
    cmd = [codex_path, "exec", "--skip-git-repo-check"]
    if dangerously_bypass and bypass_approved:
        cmd.append(bypass_flag)
    cmd.extend(["--model", model])
    if cd:
        cmd.extend(["-C", str(cd.resolve())])
    if add_dir:
        for directory in add_dir:
            cmd.extend(["--add-dir", directory])
    if sandbox:
        cmd.extend(["--sandbox", sandbox])
    if full_auto:
        cmd.append("--full-auto")
    cmd.append(prompt)
    return cmd


def add_filtered_interactive_args(cmd: list[str], extra_args: list[str] | None, bypass_flag: str) -> None:
    """Append interactive args while filtering duplicate/legacy bypass flags and model overrides."""
    if not extra_args:
        return
    for arg in extra_args:
        if arg not in (bypass_flag, "--yolo") and not arg.startswith("--model"):
            cmd.append(arg)


def extract_dex_command_args(argv: list[str]) -> list[str]:
    """Extract arguments after the dex command token from argv."""
    if not isinstance(argv, list):
        _LOG.warning(
            "dex_command_parse_failed",
            extra={"failure_type": "invalid_argv_container", "argv_type": type(argv).__name__},
        )
        raise TypeError(f"argv must be a list[str], got {type(argv).__name__}")

    for index, arg in enumerate(argv):
        if not isinstance(arg, str):
            _LOG.warning(
                "dex_command_parse_failed",
                extra={"failure_type": "invalid_argv_entry", "argv_index": index, "entry_type": type(arg).__name__},
            )
            raise TypeError(f"argv[{index}] must be str, got {type(arg).__name__}")
        if "dex" in arg and (arg.endswith("dex") or arg == "dex" or "/dex" in arg):
            return argv[index + 1 :] if index + 1 < len(argv) else []
    return []
