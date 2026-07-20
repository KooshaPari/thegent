"""thegent CLI module.

This module provides the command-line interface for thegent.

AUDIT-N+19 Phase 4: re-export the canonical ``dag_run_cmd``,
``dag_recover_cmd``, ``dag_sync_cmd``, ``dag_reconcile_cmd``,
``dag_checkpoint_cmd``, ``dag_rollback_cmd``, ``dag_probe_cmd``,
``cockpit_cmd``, ``feedback_cmd``, ``session_contract_health_*_impl``,
and the ``_serialize_health_*`` serializer family. The canonical homes
live in dedicated modules so monkeypatch sites resolve cleanly.
"""

from __future__ import annotations

from thegent.cli import run_cmd, bg_cmd
from thegent.cli.commands import impl
from thegent.cli.commands.dag_run_cmd_impl import dag_run_cmd  # noqa: F401
from thegent.cli.commands.dag_recover_cmd_impl import dag_recover_cmd  # noqa: F401
from thegent.cli.commands.plan_cmds import (  # noqa: F401
    dag_checkpoint_cmd,
    dag_probe_cmd,
    dag_reconcile_cmd,
    dag_rollback_cmd,
    dag_sync_cmd,
)
from thegent.cli.commands.session_health_report_impl import (  # noqa: F401
    _serialize_health_report_csv,
    _serialize_health_report_jsonl,
    _serialize_health_report_md,
    session_contract_health_report_impl,
)
from thegent.cli.commands.session_health_trend_impl import (  # noqa: F401
    _serialize_health_trend_csv,
    _serialize_health_trend_jsonl,
    _serialize_health_trend_md,
    session_contract_health_trend_impl,
)
from thegent.cli.commands.infra_cmds import cockpit_cmd  # noqa: F401
from thegent.cli.commands.session_cmds import feedback_cmd  # noqa: F401


__all__ = [
    "run_cmd",
    "bg_cmd",
    "impl",
    "dag_run_cmd",
    "dag_recover_cmd",
    "dag_sync_cmd",
    "dag_reconcile_cmd",
    "dag_checkpoint_cmd",
    "dag_rollback_cmd",
    "dag_probe_cmd",
    "session_contract_health_report_impl",
    "session_contract_health_trend_impl",
    "_serialize_health_report_md",
    "_serialize_health_report_csv",
    "_serialize_health_report_jsonl",
    "_serialize_health_trend_md",
    "_serialize_health_trend_csv",
    "_serialize_health_trend_jsonl",
    "cockpit_cmd",
    "feedback_cmd",
]
