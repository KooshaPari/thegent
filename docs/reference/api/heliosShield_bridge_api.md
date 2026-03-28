# heliosShield_bridge API Reference

> **Source**: `src/thegent/governance/heliosShield_bridge.py`

WP-16003: heliosShield Coordination Bridge for multi-agent tasks.

---

## SmartMerge

WP-16004: AST-aware conflict resolution using Mergiraf.

### Methods

#### SmartMerge.__init__

```python
__init__(self: Any)
```

---

#### SmartMerge.merge_files

```python
merge_files(self: Any, base: Path, ours: Path, theirs: Path, output: Path)
```

Attempt an AST-aware merge using Mergiraf or standard git merge-file.

---

---

## heliosShieldBridge

Bridges thegent to the native mesh coordination layer (formerly heliosShield).

### Methods

#### heliosShieldBridge.__init__

```python
__init__(self: Any, settings: Any)
```

---

#### heliosShieldBridge.broadcast_intent

```python
broadcast_intent(self: Any, agent_id: str, intent_type: str, target: str)
```

WP-16003: Broadcast operation intent to the mesh.

---

#### heliosShieldBridge.create_shared_task

```python
create_shared_task(self: Any, task_id: str, description: str, depends_on: Any)
```

WP-16003: Create a task in the mesh's global task list.

---

#### heliosShieldBridge.get_session_state

```python
get_session_state(self: Any, session_id: str)
```

WP-16003: Deep inspection of session state from thegent.mesh var/ dirs.

---

#### heliosShieldBridge.is_available

```python
is_available(self: Any)
```

Check if mesh coordination layer is initialized.

---

#### heliosShieldBridge.manager

```python
manager(self: Any)
```

Lazy-loaded MeshManager.

---

---

## broadcast_intent

```python
broadcast_intent(self: Any, agent_id: str, intent_type: str, target: str)
```

WP-16003: Broadcast operation intent to the mesh.

---

## create_shared_task

```python
create_shared_task(self: Any, task_id: str, description: str, depends_on: Any)
```

WP-16003: Create a task in the mesh's global task list.

---

## get_session_state

```python
get_session_state(self: Any, session_id: str)
```

WP-16003: Deep inspection of session state from thegent.mesh var/ dirs.

---

## is_available

```python
is_available(self: Any)
```

Check if mesh coordination layer is initialized.

---

## manager

```python
manager(self: Any)
```

Lazy-loaded MeshManager.

---

## merge_files

```python
merge_files(self: Any, base: Path, ours: Path, theirs: Path, output: Path)
```

Attempt an AST-aware merge using Mergiraf or standard git merge-file.

---

