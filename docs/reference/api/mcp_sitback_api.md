# mcp_sitback API Reference

> **Source**: `src/thegent/mcp_sitback.py`

Sitback Agent FastMCP integration: dashboard resource, tool, prompts.

Sitback uses FastMCP as the primary interface (projection over skill + CLI).
Tools and resources are more intuitive: typed, discoverable, URI-addressable.

---

## register_sitback

Register sitback resource, tool, and prompts with the FastMCP server.

```python
register_sitback(mcp)
```

---

## resource_sitback_dashboard

Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.
profile: light, medium (default), full (includes plugin widgets, harness).

```python
resource_sitback_dashboard(profile)
```

---

## thegent_sitback_dashboard

Unified sitback dashboard: sessions, cockpit (circuits, drift, budget), terminals.
profile: light (summary only), medium (panels), full (+ plugins, harness).
Use when THGENT_SITBACK=1 for startup protocol.

```python
thegent_sitback_dashboard(profile)
```

---

## thegent_sitback_spawn_sibling

Instructions to spawn a sibling Sitback session with the same protocol.

```python
thegent_sitback_spawn_sibling(agent)
```

---

## thegent_sitback_startup

Startup protocol for Sitback Agent (when THGENT_SITBACK=1).
Call thegent_sitback_dashboard, present the summary, then say "Sitback ready. Awaiting instructions."

---

