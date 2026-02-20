# cliproxy_manager API Reference

> **Source**: `src/thegent/agents/cliproxy_manager.py`

CLIProxyAPIPlus lifecycle: config generation and proxy process management.

Unified login flow: open URL + prompt for API key for all providers. Preflight check for
existing credentials. Setup uses the same flow.
Provider/model definitions from internal JSON (no factory config dependency).

---

## ensure_proxy_running

```python
ensure_proxy_running(settings: ThegentSettings)
```

Ensure CLIProxyAPIPlus is running. Start if not reachable.

Returns base_url (e.g. http://127.0.0.1:8317/v1).
Supports adapter (Responses API) if THGENT_CLIPROXY_ADAPTER=1.

Uses shared MCP server (system-wide) if available.

---

## fetch_provider_metrics

```python
fetch_provider_metrics(settings: Any)
```

Fetch per-provider metrics from CLIProxyAPIPlus GET /v1/metrics/providers.

---

## kill_proxy

```python
kill_proxy(settings: ThegentSettings)
```

Kill proxy process listening on cliproxy_port. Returns True if a process was killed.

Uses lsof to find PIDs by port; works regardless of how proxy was started.

---

## proxy_service_install

```python
proxy_service_install(settings: ThegentSettings)
```

Install proxy as launchd service (macOS). Runs at login, restarts on crash.

---

## proxy_service_start

Start proxy launchd service.

---

## proxy_service_stop

Stop proxy launchd service.

---

## proxy_service_uninstall

Remove proxy launchd service.

---

## run_login

```python
run_login(settings: ThegentSettings, provider: str, prompt_func: Any, force: bool)
```

Run login for provider. Returns exit code.

Prefers OAuth via CLIProxy for providers that support it.
Falls back to API-key flow for providers without OAuth (minimax, nim).
Preflight: skips OAuth flow if already configured (unless force=True).
DX-015: Checks for factory keys before opening browser or prompting.

---

## run_login_unified

```python
run_login_unified(settings: ThegentSettings, provider: str, prompt_func: Any, skip_if_configured: bool)
```

Unified login: open URL + prompt for API key. Preflight check for existing credentials.

Returns 0 on success, 1 on skip/cancel, 2 on error.

---

## start_proxy_managed

```python
start_proxy_managed(settings: ThegentSettings)
```

Start proxy and return (proc, base_url) for lifecycle management.

Caller must terminate proc on shutdown. Skips if proxy already reachable (proc=None).
Uses adapter (Responses API + WebSocket /v1/responses) when THGENT_CLIPROXY_ADAPTER=1.

---

