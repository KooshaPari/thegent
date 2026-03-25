"""Thegent CLI models/agents/providers domain (extracted from god package).

This package encapsulates all model/agent/provider-related commands and infrastructure:
- Model catalog and contract introspection
- Agent/droid discovery and metrics
- Provider configuration and routing
- Skill prompt management

@trace WL-124: CLI god package decomposition - MODELS domain
"""

from thegent.cli.commands.models.facade import (
    list_agents_cmd,
    list_droids_cmd,
    list_models_cmd,
    speed_index_cmd,
    quality_index_cmd,
    metrics_cmd,
    cost_values_cmd,
    resolve_model_route_cmd,
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
