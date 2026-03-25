"""Thegent CLI model/agent commands — backwards-compat wrapper for extracted models subpackage.

This file provides backwards compatibility for code that imports from the old
location. All implementations have been moved to the models/ subpackage.

@trace WL-124: CLI god package decomposition - MODELS domain
"""

from thegent.cli.commands.models import *  # noqa: F401, F403 -- WL-124 re-export

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
