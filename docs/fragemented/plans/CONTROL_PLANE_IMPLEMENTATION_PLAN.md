# Control Plane — Implementation Plan

> **Status**: Implementation Plan
> **Date**: 2026-02-18
> **Design**: [CONTROL_PLANE_DESIGN.md](./CONTROL_PLANE_DESIGN.md)
> **Scope**: Phased implementation, cross-platform (Win/Linux/macOS/WSL)

---

## Executive Summary

This plan breaks down the control plane implementation into **6 phases** with concrete tasks, file touchpoints, acceptance criteria, and dependencies. Each phase is shippable; later phases build on earlier ones.

**Cross-platform**: Unix socket primary on Linux/macOS/WSL; HTTP primary on Windows; platform-aware discovery.

---

## Phase Overview

| Phase | Name | Est. Effort | Depends On | Gate |
|-------|------|-------------|------------|------|
| **1** | ConfigProvider abstraction | 2–3 days | None | All CLI paths use provider |
| **2** | Control plane serve | 3–4 days | Phase 1 | `thegent control-plane serve` works |
| **3** | CLI integration + fallback | 2–3 days | Phase 1, 2 | `run`/`bg` use CP when configured |
| **4** | Tenant catalog | 2–3 days | Phase 2 | Per-tenant config resolution |
| **5** | process-compose + MCP | 1–2 days | Phase 2, 3 | CP as service; MCP tool |
| **6** | Observability + hardening | 2 days | Phase 2–5 | Metrics, OTel, circuit breaker |

---

## Phase 1: ConfigProvider Abstraction

**Goal**: Introduce `ConfigProvider` protocol; `EnvConfigProvider` wraps `ThegentSettings`. No behavior change yet.

### 1.1 Create ConfigProvider Module

**File**: `src/thegent/config_provider.py` (new)

```python
# Protocol + EnvConfigProvider
from typing import Any, Protocol

class ConfigProvider(Protocol):
    def resolve(
        self,
        tenant_id: str | None = None,
        session_id: str | None = None,
        request_overrides: dict[str, Any] | None = None,
        keys: list[str] | None = None,
    ) -> dict[str, Any]: ...

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None: ...

class EnvConfigProvider:
    """Reads from ThegentSettings; merges request_overrides."""
    def resolve(self, tenant_id=None, session_id=None, request_overrides=None, keys=None) -> dict[str, Any]: ...
    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None: ...
```

**Tasks**:
- [ ] Define `ConfigProvider` protocol
- [ ] Implement `EnvConfigProvider` using `ThegentSettings()`
- [ ] Add `_ALL_CONFIG_KEYS` from `ThegentSettings.model_fields`
- [ ] Unit tests: `resolve` merges overrides correctly; `get_tenant_config` returns None (env has no tenants)

### 1.2 Add Config Provider Factory

**File**: `src/thegent/config_provider.py`

```python
def get_config_provider() -> ConfigProvider:
    """Returns EnvConfigProvider if no CP URL; else ControlPlaneConfigProvider (Phase 2)."""
    url = os.environ.get("THGENT_CONTROL_PLANE_URL")
    if not url:
        return EnvConfigProvider()
    return ControlPlaneConfigProvider(url)  # Phase 2
```

**Tasks**:
- [ ] Add `get_config_provider()`; Phase 1 returns only `EnvConfigProvider`
- [ ] Add `THGENT_CONTROL_PLANE_URL` to config docs

### 1.3 Introduce Usage in One Critical Path (Pilot)

**File**: `src/thegent/cli_impl.py`

**Goal**: `run_impl` and `bg_impl` accept optional `config: dict[str, Any]` from provider. If not passed, use `ThegentSettings()` as today (backward compat).

**Tasks**:
- [ ] Add `config_provider: ConfigProvider | None = None` param to `run_impl` / `bg_impl`
- [ ] When `config_provider` is set, call `resolve(tenant_id, request_overrides={timeout, agent, ...})` and merge into effective config
- [ ] CLI: `run_cmd` / `bg_cmd` pass `get_config_provider()` when `THGENT_CONTROL_PLANE_URL` or `thegent control-plane status` indicates CP is available (Phase 3; Phase 1: always pass `EnvConfigProvider()` for pilot)
- [ ] Pilot: `run_cmd` uses `EnvConfigProvider().resolve()` for timeout/agent override; verify no regression

**Acceptance**:
- [ ] `thegent run "Fix bug"` behaves identically; `thegent run -t 1800 "Fix bug"` uses 1800s
- [ ] `EnvConfigProvider.resolve(request_overrides={"default_timeout": 1800})` returns merged config

---

## Phase 2: Control Plane Serve

**Goal**: `thegent control-plane serve` starts a long-running process with config resolve API.

### 2.1 Control Plane Command

**File**: `src/thegent/main.py`

```python
@app.command()
def control_plane_serve(
    socket_path: str | None = typer.Option(None, "--socket"),
    port: int = typer.Option(3848, "--port"),
    ...
):
    """Start the control plane server."""
```

**Tasks**:
- [ ] Add `control-plane` Typer group with `serve` subcommand
- [ ] `control-plane serve` invokes `control_plane_serve_impl()`

### 2.2 Control Plane Server Implementation

**File**: `src/thegent/control_plane/server.py` (new)

```python
# FastAPI or Starlette app
# POST /v1/config/resolve
# GET /health
```

**Tasks**:
- [ ] Create `control_plane/` package: `__init__.py`, `server.py`
- [ ] Implement `POST /v1/config/resolve` — accepts `tenant_id`, `session_id`, `overrides`, `keys`; returns merged config (Phase 2: global only, no tenant catalog)
- [ ] Implement `GET /health` — returns `{"status":"ok","version":"..."}`
- [ ] Load base config from `ThegentSettings()` at startup
- [ ] Config schema validation (JSON Schema) for response

### 2.3 Transport: Cross-Platform

**File**: `src/thegent/control_plane/server.py`

| Platform | Primary | Fallback |
|----------|---------|----------|
| Linux, macOS, WSL | Unix socket | HTTP |
| Windows | HTTP | Named pipe (optional) |

**Tasks**:
- [ ] Use `platform.system()` to choose transport
- [ ] Unix: bind `~/.thegent/control-plane.sock` or `$XDG_RUNTIME_DIR/thegent/cp.sock`
- [ ] Windows: bind `http://127.0.0.1:{port}` only (no socket)
- [ ] Add `--socket` and `--port` options; default: socket on Unix, port on Windows
- [ ] Use `uvicorn` or `hypercorn` with `uds` for Unix socket

### 2.4 ControlPlaneConfigProvider

**File**: `src/thegent/config_provider.py`

```python
class ControlPlaneConfigProvider:
    def __init__(self, url: str, timeout: float = 2.0): ...
    def resolve(self, ...) -> dict[str, Any]:
        # POST to url/v1/config/resolve
        # On timeout/error: raise or return None (caller falls back)
```

**Tasks**:
- [ ] Implement `ControlPlaneConfigProvider` with `httpx` (sync, timeout 2s)
- [ ] `get_config_provider()` returns it when `THGENT_CONTROL_PLANE_URL` is set
- [ ] Handle connection errors; raise `ControlPlaneUnavailable` for fallback logic

**Acceptance**:
- [ ] `thegent control-plane serve --port 3848` starts; `curl http://127.0.0.1:3848/health` returns 200
- [ ] `curl -X POST http://127.0.0.1:3848/v1/config/resolve -d '{"overrides":{"default_timeout":1800}}'` returns merged config

---

## Phase 3: CLI Integration + Fallback

**Goal**: `run`, `bg`, `plan spawn-next` use ConfigProvider; fallback to env on CP failure.

### 3.1 Config Resolution in CLI

**File**: `src/thegent/cli.py` (run_cmd, bg_cmd)

**Tasks**:
- [ ] Before `run_impl`/`bg_impl`: call `get_config_provider().resolve(tenant_id, request_overrides={...})`
- [ ] Resolve `tenant_id`: `--tenant X` | `cwd` → project config | `default`
- [ ] Pass resolved config to `run_impl`/`bg_impl` (or use provider inside impl)
- [ ] On `ControlPlaneUnavailable`: fall back to `EnvConfigProvider.resolve()`; log warning

### 3.2 Circuit Breaker

**File**: `src/thegent/config_provider.py` or `src/thegent/control_plane/client.py`

**Tasks**:
- [ ] After N consecutive CP failures (e.g. 5), open circuit; use env only
- [ ] After cooldown (e.g. 30s), half-open; try once
- [ ] On success, close circuit
- [ ] Config: `THGENT_CP_CIRCUIT_THRESHOLD`, `THGENT_CP_CIRCUIT_RECOVERY_S`

### 3.3 New Commands

**File**: `src/thegent/main.py`, `cli.py`

| Command | Implementation |
|---------|----------------|
| `thegent control-plane status` | GET /health; print status or "not running" |
| `thegent config show [--tenant X]` | Resolve config for tenant; print as YAML/JSON |

**Tasks**:
- [ ] `control-plane status` — try CP URL; print status
- [ ] `config show` — use `get_config_provider().resolve(tenant_id)`; print

**Acceptance**:
- [ ] With `THGENT_CONTROL_PLANE_URL=http://127.0.0.1:3848` and CP running: `run` uses CP config
- [ ] With CP down: `run` falls back to env; warning printed
- [ ] `thegent config show` prints resolved config

---

## Phase 4: Tenant Catalog

**Goal**: Per-tenant config overrides; file-based catalog.

### 4.1 Tenant Catalog Storage

**File**: `src/thegent/control_plane/catalog.py` (new)

**Tasks**:
- [ ] Load tenants from `~/.thegent/tenants/*.yaml` (or `%LOCALAPPDATA%\thegent\tenants\` on Windows)
- [ ] Schema: `Tenant(id, name, config: TenantConfig, ...)`
- [ ] `TenantConfig` = subset of ThegentSettings (timeout, concurrency, etc.)
- [ ] Config resolution order: request → session → tenant → global

### 4.2 Config Resolution in CP

**File**: `src/thegent/control_plane/server.py`

**Tasks**:
- [ ] `POST /v1/config/resolve` uses tenant catalog when `tenant_id` provided
- [ ] Merge: global → tenant → session → overrides
- [ ] Validate tenant config with JSON Schema before returning

### 4.3 Tenant Discovery from CWD

**File**: `src/thegent/cli_impl.py` or `config_provider.py`

**Tasks**:
- [ ] `_resolve_tenant_from_cwd(cwd: Path) -> str`: read `.thegent/tenant` or `pyproject.toml` thegent.tenant; default `"default"`
- [ ] Pass tenant_id to `resolve` in run/bg paths

**Acceptance**:
- [ ] Create `~/.thegent/tenants/acme.yaml` with `default_timeout: 1800`
- [ ] `thegent run --tenant acme "Fix bug"` uses 1800s
- [ ] `thegent config show --tenant acme` shows acme overrides

---

## Phase 5: process-compose + MCP

**Goal**: CP as third service; MCP tool for config resolve.

### 5.1 process-compose

**File**: `process-compose.yaml` or equivalent

**Tasks**:
- [ ] Add `control-plane` service: `thegent control-plane serve`
- [ ] Health check: `curl -s http://127.0.0.1:3848/health`
- [ ] Optional: depends_on mcp

### 5.2 MCP Tool

**File**: `src/thegent/mcp_server.py`

**Tasks**:
- [ ] Add `thegent_config_resolve` tool: params `tenant_id`, `keys`; returns resolved config
- [ ] Uses `get_config_provider().resolve()`

**Acceptance**:
- [ ] `mcp_up` starts mcp + proxy + control-plane
- [ ] MCP tool `thegent_config_resolve` returns config

---

## Phase 6: Observability + Hardening

**Goal**: Metrics, OTel traces, audit logging.

### 6.1 Metrics

**File**: `src/thegent/control_plane/server.py`

**Tasks**:
- [ ] `thegent_cp_config_resolves_total` (counter)
- [ ] `thegent_cp_config_resolve_duration_seconds` (histogram)
- [ ] `thegent_cp_fallback_total` (counter, in CLI)

### 6.2 OTel Spans

**File**: `src/thegent/config_provider.py`, `control_plane/server.py`

**Tasks**:
- [ ] Span `config.resolve` with attributes: tenant_id, source (cp|env)
- [ ] Span `tenant.catalog.get` when tenant lookup

### 6.3 Audit Logging

**File**: `src/thegent/control_plane/server.py`

**Tasks**:
- [ ] Log config mutations (Phase 4+ when mutation API exists)
- [ ] Structured JSON logs with tenant_id, request_id

**Acceptance**:
- [ ] Metrics exposed when `THGENT_OTEL_CONSOLE=1` or Prometheus endpoint
- [ ] Traces visible in OTel collector

---

## File Touchpoints Summary

| File | Phases |
|------|--------|
| `src/thegent/config_provider.py` (new) | 1, 2, 3, 6 |
| `src/thegent/control_plane/` (new) | 2, 4, 5, 6 |
| `src/thegent/cli_impl.py` | 1, 3, 4 |
| `src/thegent/cli.py` | 1, 3, 4 |
| `src/thegent/main.py` | 2, 3, 5 |
| `src/thegent/mcp_server.py` | 5 |
| `src/thegent/config.py` | 1 (optional: extend) |
| `process-compose.yaml` | 5 |
| `tests/` | 1, 2, 3, 4 |

---

## Dependencies

- **Phase 1**: None
- **Phase 2**: Phase 1 (ConfigProvider protocol)
- **Phase 3**: Phase 1, 2 (CP + provider)
- **Phase 4**: Phase 2 (CP server)
- **Phase 5**: Phase 2, 3
- **Phase 6**: Phase 2–5

---

## Testing Strategy

| Phase | Unit | Integration |
|-------|------|-------------|
| 1 | EnvConfigProvider.resolve, get_tenant_config | run_cmd with provider |
| 2 | CP resolve endpoint, health | `control-plane serve` + curl |
| 3 | Fallback logic, circuit breaker | run with CP up/down |
| 4 | Tenant catalog load, merge order | config show --tenant |
| 5 | MCP tool | mcp_up + tool call |
| 6 | Metrics, spans | OTel export |

---

## Rollout Plan

1. **Phase 1**: Merge; no user-visible change. Feature flag: `THGENT_USE_CONFIG_PROVIDER=1` (default off for pilot) or always use EnvConfigProvider.
2. **Phase 2**: Ship `control-plane serve`; opt-in.
3. **Phase 3**: `THGENT_CONTROL_PLANE_URL` opt-in; fallback to env.
4. **Phase 4–6**: Incremental; document in CONTROL_PLANE_QUICK_START.md.

---

## References

- [CONTROL_PLANE_DESIGN.md](./CONTROL_PLANE_DESIGN.md) — Full design
- [00-MASTER-INDEX.md](./00-MASTER-INDEX.md) — Plan index
