# plugin_lifecycle API Reference

> **Source**: `src/thegent/governance/plugin_lifecycle.py`

WP-10008: Plugin lifecycle and conformance checks.

Manages the registration and conformance validation of system plugins.

---

## PluginLifecycleManager

Manages the state and conformance of system plugins.

### Methods

#### PluginLifecycleManager.__init__

```python
__init__(self)
```

#### PluginLifecycleManager.get_plugin_status

Return the current status of a plugin.

```python
get_plugin_status(self, plugin_id)
```

#### PluginLifecycleManager.register_plugin

Register a new plugin for validation.

```python
register_plugin(self, plugin_id, metadata)
```

#### PluginLifecycleManager.run_conformance

WP-10008: Run conformance tests on a plugin.

```python
run_conformance(self, plugin_id)
```

---

## PluginStatus

**Inherits from**: `StrEnum`

---

## get_plugin_status

Return the current status of a plugin.

```python
get_plugin_status(self, plugin_id)
```

---

## register_plugin

Register a new plugin for validation.

```python
register_plugin(self, plugin_id, metadata)
```

---

## run_conformance

WP-10008: Run conformance tests on a plugin.

```python
run_conformance(self, plugin_id)
```

---

