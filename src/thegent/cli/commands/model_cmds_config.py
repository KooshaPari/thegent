"""Thegent CLI model/agent commands domain - re-export facade (WL-124).

Main entry point for model listing, setup, and configuration commands.
Implementation split across model_cmds_rules.py and model_cmds_setup.py.
"""

from thegent.cli.commands.model_cmds_rules import (
    _list_antigravity_models,
    _list_claude_models,
    _list_codex_models,
    _list_codex_models_fallback,
    _list_copilot_models,
    _list_copilot_models_fallback,
    _list_cursor_api_models,
    _list_cursor_models,
    _list_gemini_models,
    _list_glm_models,
    _list_kiro_models,
    _list_minimax_models,
    cliproxy_login_cmd,
    list_model_contract_schema_cmd,
)
from thegent.cli.commands.model_cmds_setup import (
    rules_sync_cmd,
    setup_cmd,
)

__all__ = [
    "_list_antigravity_models",
    "_list_claude_models",
    "_list_codex_models",
    "_list_codex_models_fallback",
    "_list_copilot_models",
    "_list_copilot_models_fallback",
    "_list_cursor_api_models",
    "_list_cursor_models",
    "_list_gemini_models",
    "_list_glm_models",
    "_list_kiro_models",
    "_list_minimax_models",
    "cliproxy_login_cmd",
    "list_model_contract_schema_cmd",
    "rules_sync_cmd",
    "setup_cmd",
]
