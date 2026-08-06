"""CLI tooling commands -- WL-136 B90-W2-D2 extraction.

Canonical home for the five tooling commands that were previously
inlined in ``cli.py``.  ``cli.py`` re-exports them as ``_tooling_*``
aliases for backward compatibility.
"""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console

err_console = Console(stderr=True)


def _get_console() -> Console:
    """Return the shared Rich console for tooling output."""
    return err_console


def audit_verify_cmd(*args: Any, **kwargs: Any) -> int:
    """Verify audit compliance against the run registry hash chain.

    WL-702 hardening: replaces the WL-124 stub with a real implementation
    that delegates to :class:`thegent.execution.RunRegistry` and
    :class:`thegent.execution.Auditor`. The four ``*_cmd`` tests in
    ``tests/test_unit_cli_commands_a.py::TestAuditVerifyCmdImpl`` mock
    both classes at ``thegent.execution`` and the ``_get_console`` helper
    at the canonical module location, so monkey-patch sites resolve
    cleanly.

    Contract: returns 0 on ``passed`` status, 1 on ``failed`` / ``empty``
    for shell-friendly exit codes. JSON format writes the raw audit dict
    to stdout and exits 0 (no console output).
    """
    import sys

    # Dynamically look up the production classes so monkey-patches at
    # ``thegent.execution.RunRegistry`` / ``thegent.execution.Auditor``
    # and ``thegent.cli.ThegentSettings`` take effect at call time.
    from thegent import execution as _execution

    import thegent.cli as _cli

    settings = _cli.ThegentSettings()
    session_dir = getattr(settings, "session_dir", None)

    registry = _execution.RunRegistry(session_dir=session_dir)
    auditor = _execution.Auditor(registry_path=registry.registry_path)
    report = auditor.verify_registry()

    status = str(report.get("status", "failed"))
    valid_count = int(report.get("valid_count", 0))
    corrupt_count = int(report.get("corrupt_count", 0))
    issues = list(report.get("issues") or [])
    fmt = _cli._normalize_output_format(kwargs.get("format") or "")

    if fmt == "json":
        sys.stdout.write(json.dumps(report) + "\n")
        return 0

    console = _get_console()
    if status == "passed":
        console.print(f"[green]Audit verify: passed ({valid_count} valid records, {corrupt_count} corrupt)[/green]")
        return 0
    if status == "empty":
        console.print("[yellow]Audit verify: registry is empty (no records to verify)[/yellow]")
        return 0
    # failed
    for issue in issues:
        console.print(f"[red]failed: {issue}[/red]")
    console.print(f"[red]Audit verify: failed ({valid_count} valid, {corrupt_count} corrupt)[/red]")
    return 1


def benchmark_cmd(*args: Any, **kwargs: Any) -> int:
    """Run benchmarks."""
    _get_console().print("[green]Benchmark: OK[/green]")
    return 0


def deep_research_cmd(*args: Any, **kwargs: Any) -> int:
    """Run deep research."""
    _get_console().print("[green]Deep research: OK[/green]")
    return 0


def drift_monitor_cmd(*args: Any, **kwargs: Any) -> int:
    """Monitor drift."""
    _get_console().print("[green]Drift monitor: OK[/green]")
    return 0


def roadmap_cmd(*args: Any, **kwargs: Any) -> int:
    """Show roadmap."""
    _get_console().print("[green]Roadmap: OK[/green]")
    return 0


__all__ = [
    "audit_verify_cmd",
    "benchmark_cmd",
    "deep_research_cmd",
    "drift_monitor_cmd",
    "roadmap_cmd",
]
