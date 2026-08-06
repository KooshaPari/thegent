"""Model commands module.

WL-124 stable import surface for the model domain.
"""

from __future__ import annotations

from typing import Any

import typer


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


def cliproxy_login_cmd(*args: Any, provider: str = "", **kwargs: Any) -> int:
    """Login to a CLIProxyAPIPlus provider via the canonical machine helper.

    WL-703 hardening: replaces the WL-124 stub (``return 0``) with a real
    dispatcher that delegates to
    :func:`thegent.cli.commands.model_cmds_rules._run_cliproxyctl_machine_command`.
    The canonical home for the rules layer (and its ``console``) lives
    in :mod:`thegent.cli.commands.model_cmds_rules` so monkey-patch sites
    at the canonical surface resolve cleanly under tests.

    Contract: returns 0 on success, raises :class:`typer.Exit` with
    ``exit_code=0`` on a successful delegated login, ``exit_code=1`` on
    user-skip or ``ValueError`` / ``FileNotFoundError`` from the canonical
    helper (the underlying ``run_login`` exit_code is surfaced verbatim
    via the printed message).

    The body is intentionally short: all rule logic lives in
    ``_run_cliproxyctl_machine_command`` so the canonical surface can be
    unit-tested in isolation. ``*args`` / ``**kwargs`` are accepted for
    parity with the surrounding WL-124 stub-vocabulary.
    """
    # Local import — monkey-patches at ``model_cmds_rules`` resolve at
    # call time (parity with WL-702 sweep patch-pattern).
    from thegent.cli.commands.model_cmds_rules import (
        _run_cliproxyctl_machine_command,
        console,
    )

    try:
        result = _run_cliproxyctl_machine_command(provider=provider)
    except ValueError as exc:
        console.print(f"[red]cliproxy login invalid or failed: {exc}[/red]")
        raise typer.Exit(1) from exc
    except FileNotFoundError as exc:
        console.print(f"[red]cliproxy login missing binary: {exc}[/red]")
        raise typer.Exit(1) from exc

    exit_code_raw = result.get("exit_code", 0)
    exit_code = int(exit_code_raw) if exit_code_raw is not None else 0
    if exit_code == 0:
        console.print(f"[green]{result.get('message', 'cliproxy login ok')}[/green]")
        raise typer.Exit(0)
    console.print(f"[red]{result.get('message', 'cliproxy login failed')}[/red]")
    raise typer.Exit(exit_code or 1)


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
