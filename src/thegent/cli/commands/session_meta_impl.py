"""Session metadata helpers — AUDIT-N+5 shim.

Resolves the second missing-module surface that the AUDIT-N+2 envelope-
parity sweep and the WL-125 ``run_execution_core_helpers`` parity test
flagged: ``thegent.cli.commands.session_meta_impl``. Mirrors the AUDIT-N
+2..N+4 contract by exposing ``err_console`` (``Rich Console(stderr=True)``)
and re-exporting ``print_exc`` from :mod:`thegent.ux.cli_errors`.

Provides the two call-sites
:mod:`thegent.cli.services.run_execution_core_helpers` invokes:

- :func:`_build_continuation_prompt` — assembles the continuation prompt
  by reading prior session output (with optional stderr inclusion).
- :func:`_save_session_meta` — persists the bg-session meta payload to
  the canonical meta path.

The full WL-120 extraction (the broader session-meta block: prior-session
output parsing, contract-timestamp normalisation, blocked-ratio extraction)
remains tracked as follow-up work. AUDIT-N+5 only preserves the two
direct call-sites so the five pre-existing parity-test failures close
without a full re-implementation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog
from rich.console import Console

from thegent.ux.cli_errors import print_exc  # re-exported for AUDIT-N+2 contract

_log = structlog.get_logger(__name__)
err_console = Console(stderr=True)

__all__ = ["_build_continuation_prompt", "_save_session_meta", "err_console", "print_exc"]


def _build_continuation_prompt(
    settings: Any,
    continue_from: str,
    prompt: str,
    *,
    include_stderr: bool = False,
) -> str:
    """Build a continuation prompt that wraps the prior-session output.

    Reads the prior session's stdout (and optionally stderr) and embeds
    it before the new ``prompt`` so the new run sees the previous
    result. The AUDIT-N+5 shim returns ``prompt`` unchanged when the
    prior session cannot be located, preserving the safe-by-default
    contract for the orchestrator.
    """
    prior_output = ""
    try:
        session_dir = getattr(settings, "session_dir", None) or "."
        candidate = Path(session_dir) / "sessions" / continue_from / "stdout.log"
        if candidate.exists() and candidate.is_file():
            prior_output = candidate.read_text(encoding="utf-8", errors="replace")[-4000:]
        if include_stderr:
            err_candidate = Path(session_dir) / "sessions" / continue_from / "stderr.log"
            if err_candidate.exists() and err_candidate.is_file():
                prior_output += "\n[stderr]\n" + err_candidate.read_text(encoding="utf-8", errors="replace")[-2000:]
    except OSError as exc:
        _log.debug("session_meta_impl: failed to read prior session output: %s", exc)
    if prior_output:
        return f"[Prior session {continue_from}]\n{prior_output}\n\n[New task]\n{prompt}"
    return prompt


def _save_session_meta(meta_path: Path | str, meta: dict[str, Any]) -> None:
    """Persist the bg-session meta payload to ``meta_path``.

    Mirrors the runtime contract: serialise ``meta`` as JSON to the
    supplied path, creating parents as needed. Failures are logged and
    swallowed so the orchestrator never raises during a session start.
    """
    try:
        path = Path(meta_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(meta, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    except OSError as exc:
        _log.debug("session_meta_impl: failed to persist meta to %s: %s", meta_path, exc)
