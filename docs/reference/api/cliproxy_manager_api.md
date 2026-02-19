# cliproxy_manager API Reference

> **Source**: `src/thegent/agents/cliproxy_manager.py`

CLIProxyAPIPlus lifecycle: config generation and proxy process management.

Unified login flow: open URL + prompt for API key for all providers. Preflight check for
existing credentials. Setup uses the same flow.
Provider/model definitions from internal JSON (no factory config dependency).

---

## ensure_proxy_running

Ensure CLIProxyAPIPlus is running. Start if not reachable.
Returns base_url (e.g. http://127.0.0.1:8317/v1).
Supports adapter (Responses API) if THGENT_CLIPROXY_ADAPTER=1.

Uses shared MCP server (system-wide) if available.

```python
ensure_proxy_running(settings)
```

---

## fetch_provider_metrics

Fetch per-provider metrics from CLIProxyAPIPlus GET /v1/metrics/providers.

```python
fetch_provider_metrics(settings)
```

---

## kill_proxy

Kill proxy process listening on cliproxy_port. Returns True if a process was killed.
Uses lsof to find PIDs by port; works regardless of how proxy was started.

```python
kill_proxy(settings)
```

---

## proxy_service_install

Install proxy as launchd service (macOS). Runs at login, restarts on crash.

```python
proxy_service_install(settings)
```

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

Run login for provider. Returns exit code.
Prefers OAuth via CLIProxy for providers that support it.
Falls back to API-key flow for providers without OAuth (minimax, nim).
Preflight: skips OAuth flow if already configured (unless force=True).

```python
run_login(settings, provider, prompt_func, force)
```

---

## run_login_unified

Unified login: open URL + prompt for API key. Preflight check for existing credentials.
Returns 0 on success, 1 on skip/cancel, 2 on error.

```python
run_login_unified(settings, provider, prompt_func, skip_if_configured)
```

---

## start_proxy_managed

Start proxy and return (proc, base_url) for lifecycle management.
Caller must terminate proc on shutdown. Skips if proxy already reachable (proc=None).

```python
start_proxy_managed(settings)
```

---

