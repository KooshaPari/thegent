"""Thegent CLI commands — slim re-export shim.

WL-120 Wave-3: All command handler implementations have been extracted to
domain-specific modules. This file is now a pure re-export surface so that
existing callers of ``thegent.cli.commands.cli`` continue to resolve all names
without modification.

Extraction map:
  session_cmds.py   — session_*_cmd, ps_cmd, status_cmd, wait_cmd, etc.
  infra_cmds.py     — interruption_*, concurrency_*, cockpit_cmd, etc.
  plan_cmds.py      — dag_*_cmd, plan_*_cmd, closure_pack_cmd, etc.
  model_cmds.py     — list_models_cmd, setup_cmd, metrics_cmd, etc.
  governance_cmds.py — data_protection_cmd, escalate_*, govern_*, etc.
  run_cmds.py       — run_cmd, bg_cmd, loop_cmd, etc.
  team_cmds.py      — teammates_*, handoff_*, summary_cmd, etc.
  _cli_shared.py    — shared lazy imports, constants, helper functions
"""
# @trace WL-120 Wave-3 (W3-A1 through W3-A5)

from __future__ import annotations

# WL-136 B90-W2-D2: Tooling-surface commands — re-exported from canonical module.
# Canonical definitions live in cli_tooling.py (tooling surface, not core runtime).
from thegent.cli.commands.cli_tooling import (  # noqa: F401
    audit_verify_cmd,
    benchmark_cmd,
    deep_research_cmd,
    drift_monitor_cmd,
    roadmap_cmd,
)

# WL-136 compatibility aliases expected by tooling-routing contract tests.
_tooling_audit_verify_cmd = audit_verify_cmd
_tooling_benchmark_cmd = benchmark_cmd
_tooling_deep_research_cmd = deep_research_cmd
_tooling_drift_monitor_cmd = drift_monitor_cmd
_tooling_roadmap_cmd = roadmap_cmd

__all__ = [
    "audit_verify_cmd",
    "benchmark_cmd",
    "deep_research_cmd",
    "drift_monitor_cmd",
    "roadmap_cmd",
]

# Shared infrastructure: public names (wildcard re-export).
# Exposes: console, ThegentSettings, RunRegistry, get_exit_message,
# dag_ready_impl, dag_run_impl, dag_sync_impl, dag_recover_impl,
# EXIT_TIMEOUT, EXIT_HEALTH_GATE_FAILED, list_agent_names, resolve_agent, etc.
from thegent.cli.commands._cli_shared import *  # noqa: F401, F403 -- WL-120 shim re-export

# WL-120 Wave-X: private helper re-exports now come from _cli_shared.__all__,
# so explicit private import lists are no longer needed in this shim.

# WL-124: Domain submodule re-exports — all command names available at this namespace.
from thegent.cli.commands.run_cmds import *  # noqa: F401, F403 -- WL-124 re-export
from thegent.cli.commands.session_cmds import *  # noqa: F401, F403 -- WL-124 re-export
from thegent.cli.commands.governance_cmds import *  # noqa: F401, F403 -- WL-124 re-export
from thegent.cli.commands.plan_cmds import *  # noqa: F401, F403 -- WL-124 re-export
from thegent.cli.commands.model_cmds import *  # noqa: F401, F403 -- WL-124 re-export
from thegent.cli.commands.infra_cmds import *  # noqa: F401, F403 -- WL-124 re-export
from thegent.cli.commands.team_cmds import *  # noqa: F401, F403 -- WL-124 re-export
