"""Thegent CLI model/agent commands facade - re-exports from submodules."""

# @trace WL-124
from __future__ import annotations

# List and metrics commands
from thegent.cli.commands.model_cmds_list import (
    list_agents_cmd,
    list_droids_cmd,
    list_models_cmd,
    speed_index_cmd,
    quality_index_cmd,
    metrics_cmd,
    cost_values_cmd,
    resolve_model_route_cmd,
)

# Catalog and config commands
from thegent.cli.commands.model_cmds_config import (
    list_model_contract_schema_cmd,
    cliproxy_login_cmd,
    setup_cmd,
    rules_sync_cmd,
)

__all__ = [
    "list_agents_cmd",
    "list_droids_cmd",
    "list_models_cmd",
    "speed_index_cmd",
    "quality_index_cmd",
    "metrics_cmd",
    "cost_values_cmd",
    "resolve_model_route_cmd",
    "list_model_contract_schema_cmd",
    "cliproxy_login_cmd",
    "setup_cmd",
    "rules_sync_cmd",
]
