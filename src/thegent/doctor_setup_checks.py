"""Configuration/isolation/connectivity checks extracted from doctor."""

import time
from pathlib import Path
from typing import Any

import httpx
from thegent.infra.fast_yaml_parser import yaml_load
from rich.console import Console

from thegent.config import ThegentSettings


def _classify_httpx_error(exc: BaseException) -> str:
    if isinstance(exc, httpx.TimeoutException):
        return "timeout"
    if isinstance(exc, httpx.ConnectError):
        return "connection_error"
    if isinstance(exc, httpx.NetworkError):
        return "network_error"
    if isinstance(exc, httpx.HTTPError):
        return "http_error"
    return type(exc).__name__


def check_configuration(*, check_result_cls: type[Any]) -> list[Any]:
    res_list = []
    settings = ThegentSettings()

    from thegent.agents.cliproxy_manager import _OAUTH_AUTH_PREFIXES, _has_oauth_credentials

    oauth_providers = list(_OAUTH_AUTH_PREFIXES.keys())
    oauth_providers.extend(["gemini"])

    configured_providers = []
    for provider in sorted(set(oauth_providers)):
        if _has_oauth_credentials(settings, provider):
            configured_providers.append(provider)

    r = check_result_cls("OAuth Providers", "Configuration")
    if configured_providers:
        r.status = "ok"
        r.message = f"OAuth credentials found for: {', '.join(configured_providers)}"
    else:
        r.status = "fail"
        r.message = "No OAuth providers configured (OAuth is required, API keys are not used)"
        r.fix_hint = "Run: thegent cliproxy login <provider> (e.g., claude, codex, gemini)"
    res_list.append(r)

    r = check_result_cls("CLIProxy Config", "Configuration")
    config_path = settings.cliproxy_config_path.expanduser().resolve()
    if config_path.exists():
        try:
            with open(config_path) as f:
                cfg = yaml_load(f.read())
            if isinstance(cfg, dict):
                r.status = "ok"
                r.message = f"Config found at {config_path}"
                from thegent.agents.cliproxy_manager import _OAUTH_AUTH_PREFIXES, _has_oauth_credentials

                oauth_providers = list(_OAUTH_AUTH_PREFIXES.keys())
                configured_count = sum(1 for p in oauth_providers if _has_oauth_credentials(settings, p))
                if configured_count > 0:
                    r.message += f" ({configured_count} OAuth provider(s) configured)"
                else:
                    r.status = "fail"
                    r.message += " (no OAuth providers configured)"
                    r.fix_hint = "Run: thegent cliproxy login <provider> (e.g., claude, codex, gemini)"
            else:
                r.status = "fail"
                r.message = f"Config at {config_path} is invalid YAML"
        except Exception as e:
            r.status = "fail"
            r.message = f"Failed to read config at {config_path}: {e}"
    else:
        r.status = "fail"
        r.message = f"CLIProxy config not found: {config_path}"
        r.fix_hint = "Run: thegent setup (or create the config file manually)"
    res_list.append(r)

    return res_list


def check_isolation(*, check_result_cls: type[Any]) -> list[Any]:
    res_list = []

    r = check_result_cls("Claude Config Isolation", "Isolation")
    cache_dir = Path.home() / ".cache" / "thegent" / "claude-config"
    if cache_dir.exists() and cache_dir.is_dir():
        r.status = "ok"
        r.message = f"Isolated config directory exists: {cache_dir}"

        missing_links = []
        for item in [".claude.json", "__store.db"]:
            if not (cache_dir / item).exists():
                missing_links.append(item)

        if missing_links:
            r.status = "warn"
            r.message += f" (missing: {', '.join(missing_links)})"
            r.fix_hint = "Run 'clode' once to initialize symlinks."
    else:
        r.status = "warn"
        r.message = f"Isolated config directory not found: {cache_dir}"
        r.fix_hint = "It will be created automatically on first 'clode' run."
    res_list.append(r)

    return res_list


def ensure_mcp_running(*, settings: ThegentSettings, console: Console, timeout: int = 30) -> bool:
    """Ensure MCP server and CLIProxy are running. Returns True if started successfully."""
    mcp_url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
    preflight_failure = None
    try:
        resp = httpx.get(mcp_url, timeout=2.0)
        if resp.status_code == 200:
            return True
        preflight_failure = f"HTTP {resp.status_code}"
    except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError, httpx.HTTPError) as exc:
        preflight_failure = f"{_classify_httpx_error(exc)}: {exc}"

    if preflight_failure:
        console.print(
            f"[yellow]MCP preflight health check failed ({preflight_failure}). Starting automatically...[/yellow]"
        )
    else:
        console.print("[yellow]MCP server not running. Starting automatically...[/yellow]")
    try:
        from thegent.mcp.manage import mcp_up

        success, msg = mcp_up()
        if success:
            retry_failures: dict[str, int] = {}
            for _ in range(timeout * 2):
                time.sleep(0.5)
                try:
                    resp = httpx.get(mcp_url, timeout=1.0)
                    if resp.status_code == 200:
                        if retry_failures:
                            detail = ", ".join(f"{reason}={count}" for reason, count in sorted(retry_failures.items()))
                            console.print(f"[dim]MCP startup retry diagnostics: {detail}[/dim]")
                        console.print("[green]MCP server started successfully.[/green]")
                        return True
                    retry_failures[f"http_{resp.status_code}"] = retry_failures.get(f"http_{resp.status_code}", 0) + 1
                except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError, httpx.HTTPError) as exc:
                    reason = _classify_httpx_error(exc)
                    retry_failures[reason] = retry_failures.get(reason, 0) + 1

            if retry_failures:
                detail = ", ".join(f"{reason}={count}" for reason, count in sorted(retry_failures.items()))
                console.print(f"[dim]MCP startup retry diagnostics: {detail}[/dim]")
            console.print("[red]Timeout waiting for MCP server to start.[/red]")
            return False
        console.print(f"[red]Failed to start MCP server: {msg}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Failed to start MCP server: {e}[/red]")
        return False


def check_connectivity(*, check_result_cls: type[Any], console: Console, auto_start: bool = True) -> list[Any]:
    res_list = []
    settings = ThegentSettings()

    r = check_result_cls("MCP Server", "Connectivity")
    mcp_url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
    try:
        resp = httpx.get(mcp_url, timeout=2.0)
        if resp.status_code == 200:
            r.status = "ok"
            r.message = f"MCP server reachable at {mcp_url}"
        else:
            r.status = "warn"
            r.message = f"MCP server returned {resp.status_code} at {mcp_url}"
            r.details = "Suspicion Level: LOW\nMCP server returned non-200 status."
            if auto_start:
                if ensure_mcp_running(settings=settings, console=console):
                    r.message = "MCP server started"
                    r.status = "ok"
                else:
                    r.fix_hint = "Run: thegent mcp up"
            else:
                r.fix_hint = "Run: thegent serve (or thegent mcp up)"
    except Exception as e:
        r.status = "warn"
        r.message = f"MCP server not reachable: {e}"
        r.details = "Suspicion Level: LOW\nMCP server is not running."
        if auto_start:
            if ensure_mcp_running(settings=settings, console=console):
                r.message = "MCP server started"
                r.status = "ok"
            else:
                r.fix_hint = "Run: thegent mcp up"
        else:
            r.fix_hint = "Run: thegent serve (or thegent mcp up)"
    res_list.append(r)

    r = check_result_cls("CLIProxy", "Connectivity")
    proxy_url = "http://127.0.0.1:8317/v1/models"
    try:
        resp = httpx.get(proxy_url, timeout=2.0)
        if resp.status_code == 200:
            r.status = "ok"
            r.message = "CLIProxy reachable at http://127.0.0.1:8317"
        else:
            r.status = "warn"
            r.message = f"CLIProxy returned {resp.status_code} at {proxy_url}"
            r.details = f"CLIProxy responded with HTTP {resp.status_code}"
            r.fix_hint = "Run: thegent mcp up (starts proxy + MCP)"
    except httpx.TimeoutException as exc:
        r.status = "warn"
        r.message = f"CLIProxy request timed out: {exc}"
        r.details = "CLIProxy transport status: timeout"
        r.fix_hint = "Run: thegent mcp up (starts proxy + MCP)"
    except httpx.ConnectError as exc:
        r.status = "warn"
        r.message = f"CLIProxy connection error: {exc}"
        r.details = "CLIProxy transport status: connection_error"
        r.fix_hint = "Run: thegent mcp up (starts proxy + MCP)"
    except (httpx.NetworkError, httpx.HTTPError) as exc:
        err_type = _classify_httpx_error(exc)
        r.status = "warn"
        r.message = f"CLIProxy transport error ({err_type}): {exc}"
        r.details = f"CLIProxy transport status: {err_type}"
        r.fix_hint = "Run: thegent mcp up (starts proxy + MCP)"
    except OSError as exc:
        r.status = "warn"
        r.message = f"CLIProxy OS error: {exc}"
        r.details = "CLIProxy transport status: os_error"
        r.fix_hint = "Run: thegent mcp up (starts proxy + MCP)"
    res_list.append(r)

    return res_list
