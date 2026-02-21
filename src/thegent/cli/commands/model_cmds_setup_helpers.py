"""Setup-flow helpers for model_cmds."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

_SETUP_SKIP = frozenset({"iflow-cookie", "kiro-google", "kiro-aws", "kiro-aws-authcode", "kiro-import"})


def set_env_line(lines: list[str], *, key: str, value: str) -> None:
    """Upsert a KEY=VALUE line in an env-file line list."""
    for idx, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[idx] = f"{key}={value}"
            return
    lines.append(f"{key}={value}")


def build_provider_list(
    *,
    provider_login_config: dict[str, Any],
    login_flags: dict[str, Any],
    agents: str | None,
    console: Any,
) -> list[str]:
    """Build target setup providers, optionally filtered by --agents."""
    providers = sorted(set(provider_login_config) | set(login_flags) - _SETUP_SKIP)
    if not agents:
        return providers

    agent_set = {item.strip().lower() for item in agents.split(",") if item.strip()}
    filtered = [provider for provider in providers if provider in agent_set]
    if not filtered:
        console.print(
            f"[yellow]No matching providers for --agents '{agents}'. Use names like claude, codex, cursor, nim, kilo.[/yellow]"
        )
    return filtered


def configure_providers(
    *,
    providers: list[str],
    overrides: dict[str, str | None],
    wizard: bool,
    settings: Any,
    provider_login_config: dict[str, Any],
    ensure_config: Callable[[Any], Any],
    inject_api_key: Callable[[dict[str, Any], str, str, dict[str, Any]], None],
    run_login: Callable[..., int],
    yaml_load: Callable[[Any], Any],
    yaml_dump: Callable[..., str],
    prompt_key: Callable[[str], str],
    console: Any,
) -> bool:
    """Apply CLI key overrides and optional interactive provider logins."""
    any_configured = False

    for provider in providers:
        display_name = provider_login_config.get(provider, {}).get("display_name", provider.replace("-", " ").title())
        override_value = overrides.get(provider)

        if override_value:
            if provider not in provider_login_config:
                continue
            config_path = ensure_config(settings)
            raw = yaml_load(config_path) if config_path.exists() else {}
            config = dict(raw) if isinstance(raw, dict) else {}
            cfg = provider_login_config[provider]
            inject_api_key(config, provider, str(override_value), cfg)
            config_path.write_text(yaml_dump(config, default_flow_style=False, sort_keys=False) or "")
            any_configured = True
            continue

        if wizard:
            console.print(f"\n[bold cyan]Setting up {display_name}...[/bold cyan]")
            try:
                rc = run_login(settings, provider, prompt_func=prompt_key, force=False)
                if rc == 0:
                    any_configured = True
            except (ValueError, FileNotFoundError) as exc:
                console.print(f"[dim]  {exc}[/dim]")

    return any_configured
