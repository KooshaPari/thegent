"""Starlette server for thegent Control Plane."""

import orjson as json
import logging
import os
import platform
from pathlib import Path
from typing import Any

from thegent.infra.fast_yaml_parser import yaml_load
from opentelemetry import trace
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route

from thegent.config_provider import EnvConfigProvider
from thegent.control_plane.registry_router import registry_routes

_log = logging.getLogger(__name__)

# Tracer for control plane server
tracer = trace.get_tracer("thegent.control_plane.server")

# Basic metrics store
_metrics = {
    "config_resolves_total": 0,
    "sessions_indexed": 0,
    "config_resolve_duration_sum": 0.0,
}


async def metrics(request: Request) -> Response:
    """GET /metrics — Prometheus format (basic)."""
    lines = [
        "# HELP config_resolves_total Total number of config resolutions",
        "# TYPE config_resolves_total counter",
        f"config_resolves_total {_metrics['config_resolves_total']}",
        "# HELP config_resolve_duration_sum Total time spent in config resolution",
        "# TYPE config_resolve_duration_sum counter",
        f"config_resolve_duration_sum {_metrics['config_resolve_duration_sum']}",
        "# HELP thegent_sessions_indexed Total number of sessions in the CP index",
        "# TYPE thegent_sessions_indexed gauge",
        f"thegent_sessions_indexed {_metrics['sessions_indexed']}",
    ]
    return PlainTextResponse("\n".join(lines))


class TenantManager:
    """Manages tenant config files in ~/.thegent/tenants/*.yaml."""

    def __init__(self, tenant_dir: Path | None = None) -> None:
        self.tenant_dir = tenant_dir or (Path.home() / ".thegent" / "tenants")
        self.tenant_dir.mkdir(parents=True, exist_ok=True)

    def get_config(self, tenant_id: str | None) -> dict[str, Any]:
        """Read tenant config from YAML file."""
        if not tenant_id:
            return {}
        p = self.tenant_dir / f"{tenant_id}.yaml"
        if not p.exists():
            return {}
        try:
            return yaml_load(p) or {}
        except Exception:
            return {}


class SessionIndexer:
    """Aggregates sessions from RunRegistry across all scopes."""

    def __init__(self, session_dir: Path | None = None) -> None:
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        self.session_dir = session_dir or settings.session_dir
        self.sessions: dict[str, dict[str, Any]] = {}

    def refresh(self) -> int:
        """Poll all run_registry.jsonl files in the session directory."""
        if not self.session_dir.exists():
            return 0

        new_sessions = {}
        # Walk ~/.cache/thegent/sessions/<owner>/run_registry.jsonl
        for registry_path in self.session_dir.glob("**/run_registry.jsonl"):
            try:
                with open(registry_path, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            # We only care about 'run' events (starts) or updates
                            run_id = data.get("run_id")
                            if not run_id:
                                continue

                            # Merge updates for the same run_id
                            if run_id not in new_sessions:
                                new_sessions[run_id] = data
                            else:
                                new_sessions[run_id].update(data)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                _log.warning("Failed to read registry %s: %s", registry_path, e)

        self.sessions = new_sessions
        _metrics["sessions_indexed"] = len(self.sessions)
        return len(self.sessions)

    def list_sessions(
        self, owner: str | None = None, agent: str | None = None, status: str | None = None
    ) -> list[dict[str, Any]]:
        """Filter and return indexed sessions."""
        results = []
        for s in self.sessions.values():
            if owner and s.get("owner") != owner:
                continue
            if agent and s.get("agent") != agent:
                continue
            if status and s.get("status") != status:
                continue
            results.append(s)
        # Sort by started_at descending
        return sorted(results, key=lambda x: x.get("started_at_utc", ""), reverse=True)


_tenant_manager = TenantManager()
_session_indexer = SessionIndexer()


async def health(request: Request) -> JSONResponse:
    """GET /health — liveness."""
    try:
        import thegent

        version = getattr(thegent, "__version__", "0.1.0")
    except ImportError:
        version = "0.1.0"
    return JSONResponse({"status": "ok", "version": version})


async def resolve_config(request: Request) -> JSONResponse:
    """POST /v1/config/resolve — resolve config with overrides."""
    import time

    start = time.perf_counter()
    with tracer.start_as_current_span("config.resolve") as span:
        try:
            req = await request.json()
        except Exception:
            req = {}

        tenant_id = req.get("tenant_id")
        session_id = req.get("session_id")
        overrides = req.get("overrides") or {}
        keys = req.get("keys")

        span.set_attribute("thegent.tenant_id", tenant_id or "default")
        span.set_attribute("thegent.session_id", session_id or "unknown")

        # Phase 4: apply tenant resolution order
        provider = EnvConfigProvider()
        base = provider.resolve(keys=keys)
        tenant_config = _tenant_manager.get_config(tenant_id)

        # Resolution order: overrides > session (todo) > tenant > global
        resolved = {**base, **tenant_config, **overrides}

        # Filter by keys if requested
        if keys:
            resolved = {k: v for k, v in resolved.items() if k in keys}

        # WP-CP-4.2: Validate resolved config against ThegentSettings schema (partial)
        from thegent.config import ThegentSettings

        try:
            # We only validate keys that exist in ThegentSettings
            ThegentSettings.model_validate(resolved, strict=False)
        except Exception as e:
            _log.warning("Resolved config failed validation: %s", e)
            # We proceed anyway but log it, as some keys might be dynamic/experimental

        # Update metrics
        _metrics["config_resolves_total"] += 1
        _metrics["config_resolve_duration_sum"] += time.perf_counter() - start

        # Convert Path objects to strings for JSON serialization
        def _sanitize(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_sanitize(i) for i in obj]
            if hasattr(obj, "__str__") and not isinstance(obj, (int | float | bool | str | None)):
                return str(obj)
            return obj

        res = _sanitize(resolved)
        span.set_attribute("thegent.config.keys", str(list(res.keys())))
        return JSONResponse(res)


async def get_tenant_config(request: Request) -> Response:
    """Fetch raw configuration for a specific tenant."""
    tenant_id = request.path_params.get("tenant_id")
    config = _tenant_manager.get_config(tenant_id)
    if config:
        return JSONResponse(config)
    return JSONResponse({"detail": f"Tenant {tenant_id} not found in catalog"}, status_code=404)


async def list_sessions(request: Request) -> JSONResponse:
    """GET /v1/sessions — list indexed sessions."""
    _session_indexer.refresh()  # Simple poll-on-demand for now
    owner = request.query_params.get("owner")
    agent = request.query_params.get("agent")
    status = request.query_params.get("status")
    sessions = _session_indexer.list_sessions(owner=owner, agent=agent, status=status)
    return JSONResponse({"sessions": sessions, "count": len(sessions)})


def create_app() -> Starlette:
    """Create the Starlette app for the control plane."""
    return Starlette(
        debug=True,
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/metrics", metrics, methods=["GET"]),
            Route("/v1/config/resolve", resolve_config, methods=["POST"]),
            Route("/v1/tenants/{tenant_id}/config", get_tenant_config, methods=["GET"]),
            Route("/v1/sessions", list_sessions, methods=["GET"]),
            *registry_routes,
        ],
    )


app = create_app()


def _default_socket_path() -> Path:
    """Default Unix socket path. Windows: not used."""
    xdg = Path(os.environ.get("XDG_RUNTIME_DIR", "") or "")
    if xdg.exists():
        return xdg / "thegent" / "cp.sock"
    return Path.home() / ".thegent" / "control-plane.sock"


def _default_port() -> int:
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    return settings.control_plane_port


def serve(socket_path: str | None = None, port: int | None = None, host: str = "127.0.0.1") -> None:
    """Run control plane server. Unix: socket or port. Windows: port only."""
    import uvicorn

    is_windows = platform.system() == "Windows"

    # If port is explicitly provided, use it. Otherwise, prefer socket on non-Windows.
    if port:
        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        sock = socket_path or (None if is_windows else str(_default_socket_path()))
        if sock:
            sock_path = Path(sock)
            sock_path.parent.mkdir(parents=True, exist_ok=True)
            if sock_path.exists():
                sock_path.unlink()
            uvicorn.run(app, uds=sock, log_level="info")
        else:
            p = _default_port()
            uvicorn.run(app, host=host, port=p, log_level="info")
