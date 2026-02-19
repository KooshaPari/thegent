# projects API Reference

> **Source**: `src/thegent/discovery/projects.py`

WP-11001: Cross-project discovery and context management.

---

## ContextBridger

WP-11002: Bridges context (files, state) across projects.

### Methods

#### ContextBridger.__init__

```python
__init__(self, registry)
```

#### ContextBridger.get_peer_context

Find files in a peer project matching a pattern.

```python
get_peer_context(self, project_name, file_pattern)
```

---

## ProjectRegistry

Manages a registry of local projects using thegent.

### Methods

#### ProjectRegistry.__init__

```python
__init__(self, global_config_dir)
```

#### ProjectRegistry.list_projects

List all registered projects.

```python
list_projects(self)
```

#### ProjectRegistry.register_project

Register a project path.

```python
register_project(self, path, name)
```

#### ProjectRegistry.update_activity

Update last active timestamp for a project.

```python
update_activity(self, path)
```

---

## get_peer_context

Find files in a peer project matching a pattern.

```python
get_peer_context(self, project_name, file_pattern)
```

---

## list_projects

List all registered projects.

```python
list_projects(self)
```

---

## register_project

Register a project path.

```python
register_project(self, path, name)
```

---

## update_activity

Update last active timestamp for a project.

```python
update_activity(self, path)
```

---

