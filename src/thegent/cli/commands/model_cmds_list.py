"""Thegent CLI model/agent commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import json
from thegent.utils.json_utils import json_loads, json_dumps
import re
import os
import shutil
import sys
from pathlib import Path
from typing import Any, cast

import typer

from rich.table import Table

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _bootstrap_metric_contracts,
    _get_run_subprocess_optimized,
    _normalize_output_format,
    _resolve_cwd,
    _resolve_droids_dir,
    console,
    list_agent_names,
    list_droid_names,
    resolve_agent,
)
from thegent.cli.commands.model_cmds_agents_helpers import render_agents_table, render_droids_table
from thegent.cli.commands.model_cmds_catalog_helpers import (
    emit_by_model_view,
    emit_contract_view,
    provider_sequence,
    run_provider_listings,
)
from thegent.cli.commands.model_cmds_metrics_helpers import (
    build_index_data,
    collect_metrics_rows,
    emit_cost_values_output,
    emit_index_output,
    emit_metrics_output,
    flatten_cost_values,
)
from thegent.cli.commands.model_cmds_route_helpers import build_available_routes, build_resolved_route
from thegent.cli.commands.model_cmds_setup_helpers import (
    build_provider_list,
    configure_providers,
    set_env_line,
)


from thegent.cli.commands.model_cmds_catalog_helpers import (
    emit_by_model_view,
    emit_contract_view,
    provider_sequence,
    run_provider_listings,
)
from thegent.cli.commands.model_cmds_metrics_helpers import (
    build_index_data,
    collect_metrics_rows,
    emit_cost_values_output,
    emit_index_output,
    emit_metrics_output,
    flatten_cost_values,
)
from thegent.cli.commands.model_cmds_route_helpers import build_available_routes, build_resolved_route


def _assert_str(value: str | None) -> str:
    """Assert yaml.dump returned str (always true when stream=None)."""
    assert value is not None, "yaml.dump returned None unexpectedly"
    return value


_CLIPROXYCTL_SCHEMA_VERSION = "cliproxyctl.machine.v1"
_HELIOS_CLIPROXYCTL_REPO = "github.com/kooshapari/cliproxyapi-plusplus"
_HELIOS_CLIPROXYCTL_PACKAGE = f"{_HELIOS_CLIPROXYCTL_REPO}/v6/cmd/server@latest"
_HELIOS_CLIPROXYCTL_LOCAL_REPO = "cliproxyapi-plusplus"
_HELIOS_CLIPROXYCTL_LOCAL_BINARY = "cli-proxy-api-plus"
_CLIPROXYCTL_NOT_FOUND_MSG = (
    "cliproxyctl not found. Auto-install via go is attempted when possible. "
    "Install Go or set THGENT_CLIPROXYCTL_BINARY=/path/to/cliproxyctl if needed. "
    f"Expected package: `go install {_HELIOS_CLIPROXYCTL_PACKAGE}`"
)


def _resolve_cliproxyctl_binary() -> str:
    """Resolve cliproxyctl binary path from env, PATH, or Go install locations."""
    configured = os.environ.get("THGENT_CLIPROXYCTL_BINARY", "cliproxyctl").strip() or "cliproxyctl"
    if "/" in configured or "~" in configured:
        return str(Path(configured).expanduser())
    found = shutil.which(configured)
    if found:
        return found

    go_paths = []
    go_bin = _resolve_go_env("GOBIN")
    if go_bin:
        go_paths.append(Path(go_bin))
    gopath = _resolve_go_env("GOPATH")
    if gopath:
        go_paths.append(Path(gopath) / "bin")
    go_paths.append(Path(os.path.expanduser("~/go/bin")))

    # Common Go install locations if PATH is not yet wired.
    go_fallback_candidates = ("cliproxyctl", "cli-proxy-api", "cli-proxy-api-plus", "server")
    for base in go_paths:
        if not base:
            continue
        for name in go_fallback_candidates:
            candidate = base / name
            if candidate.exists():
                return str(candidate)
    return configured


def _resolve_cliproxyctl_local_paths() -> list[Path]:
    """Return likely local checkout paths for cliproxyctl."""
    configured = os.environ.get("THGENT_CLIPROXYCTL_REPO_PATH", "").strip()
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured).expanduser())

    script_dir = Path(__file__).resolve().parent
    for ancestor in script_dir.parents:
        if ancestor.name == "repos":
            candidates.append(ancestor / _HELIOS_CLIPROXYCTL_LOCAL_REPO)
            break
    candidates.extend(
        (
            Path.cwd(),
            Path.cwd().parent,
            Path.cwd() / _HELIOS_CLIPROXYCTL_LOCAL_REPO,
            Path.home() / "CodeProjects" / "Phenotype" / "repos" / _HELIOS_CLIPROXYCTL_LOCAL_REPO,
        )
    )
    return [path.expanduser() for path in candidates if str(path).strip()]


def _build_cliproxyctl_from_local_repo() -> str:
    """Build cliproxyctl from a local source checkout and return output binary path."""
    run_subprocess_optimized = _get_run_subprocess_optimized()
    seen: set[Path] = set()
    for repo_path in _resolve_cliproxyctl_local_paths():
        repo_path = repo_path.expanduser()
        cmd_dir = repo_path / "cmd" / "server"
        if not cmd_dir.is_dir():
            continue
        if repo_path in seen:
            continue
        seen.add(repo_path)
        binary_path = repo_path / _HELIOS_CLIPROXYCTL_LOCAL_BINARY
        proc = run_subprocess_optimized(
            [shutil.which("go") or "go", "build", "-o", str(binary_path), "./cmd/server"],
            check=False,
            capture_output=True,
            text=True,
            cwd=repo_path,
        )
        if proc.returncode != 0:
            stderr_text = _coerce_subprocess_output(getattr(proc, "stderr", ""))
            stdout_text = _coerce_subprocess_output(getattr(proc, "stdout", ""))
            detail = stderr_text.strip() or stdout_text.strip() or "go build failed"
            raise RuntimeError(f"Auto-install cliproxyctl failed from local checkout {repo_path}: {detail}")
        if binary_path.exists():
            return str(binary_path)
    raise FileNotFoundError("Could not find local cliproxyctl source tree to build")


def _resolve_go_env(name: str) -> str:
    """Return `go env <name>` output if available."""
    run_subprocess_optimized = _get_run_subprocess_optimized()
    proc = run_subprocess_optimized(["go", "env", name], check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        return ""
    return _coerce_subprocess_output(getattr(proc, "stdout", "")).strip()


def _install_cliproxyctl() -> str:
    """Install cliproxyctl with go install and return discovered binary path."""
    configured = os.environ.get("THGENT_CLIPROXYCTL_BINARY", "").strip()
    if configured and ("/" in configured or "~" in configured):
        return configured

    go_bin = shutil.which("go")
    if not go_bin:
        raise FileNotFoundError("go not found. Install Go or set THGENT_CLIPROXYCTL_BINARY=/path/to/cliproxyctl")

    try:
        run_subprocess_optimized = _get_run_subprocess_optimized()
        proc = run_subprocess_optimized(
            [go_bin, "install", _HELIOS_CLIPROXYCTL_PACKAGE],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise RuntimeError(f"Auto-install cliproxyctl failed to run go install: {exc}") from exc

    if proc.returncode != 0:
        stderr_text = _coerce_subprocess_output(getattr(proc, "stderr", ""))
        stdout_text = _coerce_subprocess_output(getattr(proc, "stdout", ""))
        detail = stderr_text.strip() or stdout_text.strip() or "go install failed"
        # Older/renamed upstream module metadata can block package installs.
        # Keep automation active by building from a local checkout when available.
        return _build_cliproxyctl_from_local_repo()

    go_paths = []
    for path in (os.environ.get("GOBIN", "").strip(), _resolve_go_env("GOPATH"), os.path.expanduser("~/go")):
        if path:
            go_paths.append(Path(path) / "bin")
    if not go_paths:
        go_paths.append(Path(os.path.expanduser("~/go/bin")))

    for base in go_paths:
        for name in ("cliproxyctl", "cli-proxy-api", "cli-proxy-api-plus", "server"):
            candidate = base / name
            if base and candidate.exists():
                path = str(candidate)
                os.environ["THGENT_CLIPROXYCTL_BINARY"] = path
                return path
    maybe = _resolve_cliproxyctl_binary()
    if _binary_exists(maybe):
        return maybe
    raise RuntimeError(
        "Auto-installed cliproxyctl but could not locate binary. "
        "Set THGENT_CLIPROXYCTL_BINARY to the installed location."
    )


def _binary_exists(binary: str) -> bool:
    return Path(binary).exists() or shutil.which(binary) is not None


def _coerce_subprocess_output(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return "" if value is None else str(value)


def _parse_cliproxyctl_envelope(stdout_text: str, *, expected_command: str) -> dict[str, Any]:
    """Parse and validate cliproxyctl machine JSON envelope."""
    try:
        payload = json.loads(stdout_text)
    except json.JSONDecodeError as exc:  # pragma: no cover - explicit error branch in tests
        raise ValueError(f"Invalid cliproxyctl JSON envelope: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Invalid cliproxyctl JSON envelope: expected top-level object")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, str):
        raise ValueError("Invalid cliproxyctl JSON envelope: missing schema_version")
    if schema_version != _CLIPROXYCTL_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported cliproxyctl schema_version: "
            f"{schema_version} (expected {_CLIPROXYCTL_SCHEMA_VERSION})"
        )
    command = payload.get("command")
    if not isinstance(command, str):
        raise ValueError("Invalid cliproxyctl JSON envelope: missing command")
    if command != expected_command:
        raise ValueError(f"cliproxyctl command mismatch: expected '{expected_command}', got '{command}'")
    ok = payload.get("ok")
    if not isinstance(ok, bool):
        raise ValueError("Invalid cliproxyctl JSON envelope: missing boolean 'ok'")
    return payload


def _run_cliproxyctl_machine_command(command: str, *, args: list[str] | None = None) -> dict[str, Any]:
    """Run cliproxyctl command with --json and enforce envelope validation."""
    binary = _resolve_cliproxyctl_binary()
    if not _binary_exists(binary):
        console.print("[yellow]cliproxyctl not found. Attempting auto-install via Go...[/yellow]")
        binary = _install_cliproxyctl()
    if not _binary_exists(binary):
        raise FileNotFoundError(_CLIPROXYCTL_NOT_FOUND_MSG)
    argv = [binary, command, *(args or []), "--json"]
    run_subprocess_optimized = _get_run_subprocess_optimized()
    proc = run_subprocess_optimized(argv, check=False, capture_output=True, text=True)
    stdout_text = _coerce_subprocess_output(getattr(proc, "stdout", ""))
    stderr_text = _coerce_subprocess_output(getattr(proc, "stderr", ""))
    envelope = _parse_cliproxyctl_envelope(stdout_text, expected_command=command)
    if proc.returncode != 0:
        error = envelope.get("error")
        error_message = ""
        if isinstance(error, dict):
            code = error.get("code")
            message = error.get("message")
            error_message = f"{code}: {message}" if code or message else str(error)
        if not error_message:
            error_message = stderr_text.strip() or envelope.get("message", "")
        raise RuntimeError(f"cliproxyctl {command} failed with exit code {proc.returncode}: {error_message}".strip())
    if not envelope["ok"]:
        error = envelope.get("error")
        detail = error if isinstance(error, str) else json.dumps(error) if error is not None else ""
        message = str(envelope.get("message", "")).strip()
        combined = ": ".join([part for part in [message, detail] if part]).strip()
        raise RuntimeError(f"cliproxyctl {command} reported failure{': ' + combined if combined else ''}")
    return envelope


# Copilot: only gpt-5-mini and haiku (no gemini-3.1-pro).
_COPILOT_ALLOWED_MODELS: tuple[str, ...] = (
    "claude-haiku-4.5",
    "gpt-5-mini",
)


def _models_table(title: str) -> Table:
    t = Table(title=title)
    t.add_column("Model ID", style="cyan")
    t.add_column("Display Name", style="dim")
    return t



def list_agents_cmd() -> None:
    """List available agents."""
    agents = list_agent_names()
    render_agents_table(agents, resolve_agent=resolve_agent, console=console)


def list_droids_cmd(cd: Path | None = None) -> None:
    """List available droids."""
    settings = ThegentSettings()
    resolved_cd = _resolve_cwd(cd)
    droids_dir = _resolve_droids_dir(resolved_cd, settings)
    droids = list_droid_names(droids_dir)
    if not droids:
        console.print("[yellow]No droids found.[/yellow]")
        return
    render_droids_table(droids, console=console)


def list_models_cmd(
    provider: str | None = None,
    by_model: bool = False,
    refresh: bool = False,
    include_contract: bool = False,
) -> None:
    """List available models (scraped from CLIs/config)."""
    if include_contract:
        emit_contract_view(provider=provider, refresh=refresh, console=console)
        return

    if by_model:
        emit_by_model_view(refresh=refresh, console=console)
        return
    providers = provider_sequence(provider)
    run_provider_listings(
        providers,
        handlers={
            "minimax": _list_minimax_models,
            "glm": _list_glm_models,
            "cursor": _list_cursor_api_models,
            "gemini": _list_gemini_models,
            "copilot": _list_copilot_models,
            "interactive_agent": _list_claude_models,
            "claude": _list_claude_models,
            "headless_agent": _list_codex_models,
            "codex": _list_codex_models,
            "antigravity": _list_antigravity_models,
            "kiro": _list_kiro_models,
        },
    )


def speed_index_cmd(
    format: str | None = None,
    no_cache: bool = False,
) -> None:
    """Show speed index (0-1, higher=faster) for all model-provider pairs.

    Uses CLIProxyAPIPlus metrics (tps_1m, latency_p50_ms, success_rate) when reachable;
    falls back to Route.latency_ms.
    """
    from thegent.models.speed_values import (
        get_model_provider_speed_indices,
        invalidate_speed_index_cache,
    )

    if no_cache:
        invalidate_speed_index_cache()
    indices = get_model_provider_speed_indices(use_cache=not no_cache)
    data = build_index_data(indices)

    fmt = _normalize_output_format(format)
    emit_index_output(
        data=data,
        fmt=fmt,
        title="Model-Provider Speed Index (0-1, higher=faster)",
        value_label="Speed Index",
        console=console,
    )


def quality_index_cmd(
    format: str | None = None,
    no_cache: bool = False,
) -> None:
    """Show quality index (0-1) for all models.

    Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available;
    falls back to Route.accuracy_score.
    """
    from thegent.models.quality_values import (
        get_model_provider_quality_indices,
        invalidate_quality_index_cache,
    )

    if no_cache:
        invalidate_quality_index_cache()
    indices = get_model_provider_quality_indices(use_cache=not no_cache)
    data = build_index_data(indices)

    fmt = _normalize_output_format(format)
    emit_index_output(
        data=data,
        fmt=fmt,
        title="Model-Provider Quality Index (0-1, higher=better)",
        value_label="Quality Index",
        console=console,
    )


def metrics_cmd(
    format: str | None = None,
    no_cache: bool = False,
    limit: int = 50,
) -> None:
    """Show cost, speed, and quality indices for all model-provider pairs (unified view)."""
    from thegent.models.cost_values import get_model_provider_costs
    from thegent.models.quality_values import (
        get_model_provider_quality_indices,
        invalidate_quality_index_cache,
    )
    from thegent.models.speed_values import (
        get_model_provider_speed_indices,
        invalidate_speed_index_cache,
    )

    if no_cache:
        invalidate_speed_index_cache()
        invalidate_quality_index_cache()
    costs = get_model_provider_costs()
    speed = get_model_provider_speed_indices(use_cache=not no_cache)
    quality = get_model_provider_quality_indices(use_cache=not no_cache)

    rows = collect_metrics_rows(costs=costs, speed=speed, quality=quality, limit=limit)

    fmt = _normalize_output_format(format)
    emit_metrics_output(rows=rows, limit=limit, fmt=fmt, console=console)


def cost_values_cmd(format: str | None = None) -> None:
    """Show cost values ($/1k tokens) for all model-provider pairs.

    Uses CLIProxyAPIPlus metrics when reachable; falls back to static values.
    """
    from thegent.models.cost_values import get_model_provider_costs

    costs = get_model_provider_costs()
    data = flatten_cost_values(costs)

    fmt = _normalize_output_format(format)
    emit_cost_values_output(data=data, fmt=fmt, console=console)


def resolve_model_route_cmd(
    model: str,
    provider: str | None = None,
    policy: str = "prefer_direct",
    quality_floor: float = 0.0,
    lane: str | None = None,
) -> None:
    """Resolve a model to a preferred route and emit contract-style output."""
    from thegent.models import (
        ModelCatalog,
        normalize_model_id,
        normalize_route_policy,
        resolve_route_contract,
    )
    from thegent.models.quality_values import get_model_provider_quality_indices
    from thegent.models.speed_values import get_model_provider_speed_indices

    try:
        policy_value = normalize_route_policy(policy)
    except ValueError:
        console.print(
            "[red]Invalid routing policy. Use prefer_direct, prefer_proxy, failover, cheapest, cost_quality, pareto.[/red]"
        )
        raise typer.Exit(1)

    normalized = normalize_model_id(model)
    route = resolve_route_contract(
        model,
        provider_hint=provider,
        policy=policy_value,
    )
    speed_map = get_model_provider_speed_indices().get(normalized, {})
    quality_map = get_model_provider_quality_indices().get(normalized, {})
    routes = sorted(
        ModelCatalog.routes_for(model),
        key=lambda r: (r.provider, r.priority, r.model_alias),
    )
    available_routes = build_available_routes(routes=routes, speed_map=speed_map, quality_map=quality_map)

    payload: dict[str, Any] = {
        "model": model,
        "normalized_model": normalized,
        "policy": policy_value,
        "provider_hint": provider,
        "route_found": route is not None,
        "available_routes": available_routes,
    }
    if route is None:
        if available_routes:
            console.print("[yellow]No route matched the provided hint. Showing available routes below.[/yellow]")
        else:
            console.print(f"[red]No route for model '{model}'.[/red]")
        console.print_json(data=payload)
        raise typer.Exit(1)

    resolved = build_resolved_route(route=route, speed_map=speed_map, quality_map=quality_map)
    payload["resolved_route"] = resolved
    console.print_json(data=payload)
