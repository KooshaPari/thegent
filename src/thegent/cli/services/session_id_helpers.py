"""Session identifier helpers extracted from CLI impl (WL-125).

WL-125 closure: ``new_session_id`` is the AUDIT-N+12-compatible
``<agent>-<scope>-<8-char hex uuid>`` formatter so
``thegent.cli.commands.impl._new_session_id`` (which delegates here) and
``thegent.cli.commands.session_impl._new_session_id`` (the canonical home)
both return the audit-pin format. ``run_session_helpers.new_session_id``
exposes its own timestamp-based formatter independently.
"""

from __future__ import annotations

import uuid


def new_session_id(agent: str | None, owner: str) -> str:
    """Compose ``<agent>-<scope>-<8-char hex uuid>`` matching AUDIT-N+12 format.

    The scope is derived from ``owner`` via ``:`` / ``/`` / whitespace ->
    ``-`` substitution (matches :func:`scope_key` in
    :mod:`thegent.cli.services.session_owner_helpers`). Empty owner resolves
    to ``"anon"`` so callers always get a deterministic, scope-tagged id.
    """
    if not owner:
        scope = "anon"
    else:
        # Mirror the legacy scope_key derivation so old format contracts
        # remain green (e.g. owner="alice:proj" -> scope="alice-proj").
        out: list[str] = []
        for ch in owner:
            if ch.isalnum() or ch in "._-":
                out.append(ch)
            else:
                out.append("-")
        scope = "".join(out) or "anon"
    short = uuid.uuid4().hex[:8]
    agent_tag = agent or "any"
    return f"{agent_tag}-{scope}-{short}"
