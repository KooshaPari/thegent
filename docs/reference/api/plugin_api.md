# plugin API Reference

> **Source**: `src/thegent/plugin.py`

Plugin system for thegent.

Allows lazy-loading of extensions, commands, and integrations.

---

## Plugin

Protocol for plugins.

**Inherits from**: `Protocol`

### Methods

#### Plugin.activate

```python
activate(self: Any)
```

Activate the plugin.

---

#### Plugin.deactivate

```python
deactivate(self: Any)
```

Deactivate the plugin.

---

---

## PluginRegistry

Registry for managing plugins.

### Methods

#### PluginRegistry.__init__

```python
__init__(self: Any)
```

---

#### PluginRegistry.activate

```python
activate(self: Any, name: str)
```

Activate a plugin by name.

---

#### PluginRegistry.deactivate

```python
deactivate(self: Any, name: str)
```

Deactivate a plugin by name.

---

#### PluginRegistry.get

```python
get(self: Any, name: str)
```

Get an active plugin by name.

---

#### PluginRegistry.list_active

```python
list_active(self: Any)
```

List all active plugins.

---

#### PluginRegistry.load_plugins_from_dir

```python
load_plugins_from_dir(self: Any, plugins_dir: Path)
```

Load all plugins from a directory.

---

#### PluginRegistry.register

```python
register(self: Any, name: str, loader: PluginLoader)
```

Register a plugin loader.

---

---

## activate

```python
activate(self: Any, name: str)
```

Activate a plugin by name.

---

## activate_plugin

```python
activate_plugin(name: str)
```

Activate a plugin from the global registry.

---

## deactivate

```python
deactivate(self: Any, name: str)
```

Deactivate a plugin by name.

---

## get

```python
get(self: Any, name: str)
```

Get an active plugin by name.

---

## get_registry

Get the global plugin registry.

---

## list_active

```python
list_active(self: Any)
```

List all active plugins.

---

## list_plugins

List active plugins.

---

## load_plugins_from_dir

```python
load_plugins_from_dir(self: Any, plugins_dir: Path)
```

Load all plugins from a directory.

---

## register

```python
register(self: Any, name: str, loader: PluginLoader)
```

Register a plugin loader.

---

## register_plugin

```python
register_plugin(name: str, loader: PluginLoader)
```

Register a plugin with the global registry.

---

