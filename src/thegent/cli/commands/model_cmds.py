"""Model commands module.

WL-124 stable import surface for the model domain.
"""

from __future__ import annotations

from typing import Any


def _models_table(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: models table helper."""
    return {}


def list_agents_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """List agents. Thin shim over list_agents_impl."""
    from .impl import list_agents_impl

    return list_agents_impl(*args, **kwargs)


def list_droids_cmd(*args: Any, **kwargs: Any) -> int:
    """List droids. Stub returning 0."""
    return 0


def list_models_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """List models. Thin shim over list_models_impl."""
    from .impl import list_models_impl

    return list_models_impl(*args, **kwargs)


def speed_index_cmd(*args: Any, **kwargs: Any) -> int:
    """Show speed index. Stub returning 0."""
    return 0


def quality_index_cmd(*args: Any, **kwargs: Any) -> int:
    """Show quality index. Stub returning 0."""
    return 0


def metrics_cmd(*args: Any, **kwargs: Any) -> int:
    """Show metrics. Stub returning 0."""
    return 0


def cost_values_cmd(*args: Any, **kwargs: Any) -> int:
    """Show cost values. Stub returning 0."""
    return 0


def resolve_model_route_cmd(*args: Any, **kwargs: Any) -> int:
    """Resolve a model route. Stub returning 0."""
    return 0


def list_model_contract_schema_cmd(*args: Any, **kwargs: Any) -> int:
    """Show the model contract schema. Stub returning 0."""
    return 0


def _list_minimax_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list MiniMax models."""
    return {}


def _list_glm_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list GLM models."""
    return {}


def _list_cursor_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list Cursor models."""
    return {}


def _list_cursor_api_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list Cursor API models."""
    return {}


def _list_gemini_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list Gemini models."""
    return {}


def _list_copilot_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list Copilot models."""
    return {}


def _list_copilot_models_fallback(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: fallback Copilot models list."""
    return {}


def _list_claude_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list Claude models."""
    return {}


def _list_codex_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list Codex models."""
    return {}


def _list_codex_models_fallback(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: fallback Codex models list."""
    return {}


def _list_antigravity_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list Antigravity models."""
    return {}


def _list_kiro_models(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """WL-124 stable import surface: list Kiro models."""
    return {}


def cliproxy_login_cmd(*args: Any, **kwargs: Any) -> int:
    """CLI Proxy login. Stub returning 0."""
    return 0


def setup_cmd(*args: Any, **kwargs: Any) -> int:
    """Setup. Stub returning 0."""
    return 0


def rules_sync_cmd(*args: Any, **kwargs: Any) -> int:
    """Sync rules. Stub returning 0."""
    return 0


# Backwards-compatible alias for the original model_cmds_list helper.
def model_cmds_list() -> list[str]:
    """Return list of model commands (legacy helper)."""
    return ["list", "info", "set"]


__all__ = [
    "_models_table",
    "list_agents_cmd",
    "list_droids_cmd",
    "list_models_cmd",
    "speed_index_cmd",
    "quality_index_cmd",
    "metrics_cmd",
    "cost_values_cmd",
    "resolve_model_route_cmd",
    "list_model_contract_schema_cmd",
    "_list_minimax_models",
    "_list_glm_models",
    "_list_cursor_models",
    "_list_cursor_api_models",
    "_list_gemini_models",
    "_list_copilot_models",
    "_list_copilot_models_fallback",
    "_list_claude_models",
    "_list_codex_models",
    "_list_codex_models_fallback",
    "_list_antigravity_models",
    "_list_kiro_models",
    "cliproxy_login_cmd",
    "setup_cmd",
    "rules_sync_cmd",
    "model_cmds_list",
]
