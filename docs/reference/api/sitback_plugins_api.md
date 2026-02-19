# sitback_plugins API Reference

> **Source**: `src/thegent/sitback_plugins.py`

Sitback plugin API: dashboard widgets and startup steps.

Plugins are discovered from ~/.claude/sitback-plugins/ (JSON or Python).
Each plugin can register:
- dashboard_widgets: dict[str, callable] -> name -> fn() -> dict (title, content, border_style)
- startup_steps: list[str] -> extra lines for startup prompt
- harness_status: callable -> dict | None (for sharecli/FUSE; returns None if unavailable)

---

## SitbackPluginRegistry

Registry for sitback plugins: widgets, startup steps, harness status.

### Methods

#### SitbackPluginRegistry.__init__

```python
__init__(self)
```

#### SitbackPluginRegistry.get_harness_status

Return harness status if provider available, else None.

```python
get_harness_status(self)
```

#### SitbackPluginRegistry.get_startup_steps

Return registered startup steps.

```python
get_startup_steps(self)
```

#### SitbackPluginRegistry.get_widgets

Run all widgets, return {name: result}. Skips failures.

```python
get_widgets(self)
```

#### SitbackPluginRegistry.register_harness_status

Register harness status provider (e.g. sharecli). Returns None if unavailable.

```python
register_harness_status(self, fn)
```

#### SitbackPluginRegistry.register_startup_step

Register an extra startup step (appended to startup prompt).

```python
register_startup_step(self, step)
```

#### SitbackPluginRegistry.register_widget

Register a dashboard widget. fn() returns {title, content, border_style}.

```python
register_widget(self, name, fn)
```

---

## get_harness_status

Return harness status if provider available, else None.

```python
get_harness_status(self)
```

---

## get_registry

Get or create the global plugin registry.

---

## get_startup_steps

Return registered startup steps.

```python
get_startup_steps(self)
```

---

## get_widgets

Run all widgets, return {name: result}. Skips failures.

```python
get_widgets(self)
```

---

## register_harness_status

Register harness status provider (e.g. sharecli). Returns None if unavailable.

```python
register_harness_status(self, fn)
```

---

## register_startup_step

Register an extra startup step (appended to startup prompt).

```python
register_startup_step(self, step)
```

---

## register_widget

Register a dashboard widget. fn() returns {title, content, border_style}.

```python
register_widget(self, name, fn)
```

---

