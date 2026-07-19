"""Observability / escalation hand-off shim — AUDIT-N+5.

Resolves the ``ModuleNotFoundError: No module named
'thegent.cli.commands.observability_impl'`` surfaced by the AUDIT-N+2
envelope-parity sweep and the WL-125 ``run_execution_core_helpers``
parity test. Mirrors the AUDIT-N+2..N+4 contract by exposing
``err_console`` (``Rich Console(stderr=True)``) and re-exporting
``print_exc`` from :mod:`thegent.ux.cli_errors`, then provides the
single call site :mod:`thegent.cli.services.run_execution_core_helpers`
invokes (``escalate_add_impl``).

The full WL-120 extraction (the original 1,125-line observability /
health / escalation / governance / review / compliance block) is
tracked as follow-up work in WORKLOG.md. AUDIT-N+5 only preserves the
import surface and the one ``escalate_add_impl`` call site so the
five pre-existing parity-test failures close without a full
re-implementation.
"""

from __future__ import annotations

from typing import Any

import structlog
from rich.console import Console

from thegent.ux.cli_errors import print_exc

# AUDIT-N+2 envelope-parity contract: every swept module exposes a
# stderr ``Console`` and re-exports ``cli_errors.print_exc``.
err_console = Console(stderr=True)

_log = structlog.get_logger(__name__)

# In-memory record of every escalation request the shim receives.
# Real WL-120 implementation will route through
# :class:`thegent.execution.EscalationQueue`.
_escalation_log: list[dict[str, Any]] = []


def escalate_add_impl(
    *,
    run_id: str,
    reason: str,
    sla_minutes: int,
    owner: str | None,
    agent: str | None,
    lane: str,
    priority: int | None = None,
) -> None:
    """AUDIT-N+5 hand-off shim for ``escalate_add_impl``.

    Accepts the canonical kwargs used by
    :mod:`thegent.cli.services.run_execution_core_helpers`
    (policy-deny + HITL-pause paths). Records to ``_escalation_log``
    and emits a ``structlog`` warning so operators see a structured
    trace until the real ``EscalationQueue`` lands.
    """
    payload: dict[str, Any] = {
        "run_id": run_id,
        "reason": reason,
        "sla_minutes": sla_minutes,
        "owner": owner,
        "agent": agent,
        "lane": lane,
    }
    if priority is not None:
        payload["priority"] = priority
    _escalation_log.append(payload)
    _log.warning(
        "escalation.recorded",
        run_id=run_id,
        lane=lane,
        agent=agent,
        owner=owner,
        sla_minutes=sla_minutes,
        priority=priority,
    )


__all__ = ["err_console", "print_exc", "escalate_add_impl"]
