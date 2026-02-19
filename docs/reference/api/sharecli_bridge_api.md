# sharecli_bridge API Reference

> **Source**: `src/thegent/governance/sharecli_bridge.py`

WP-16003: ShareCLI Coordination Bridge for multi-agent tasks.

---

## ShareCLIBridge

Bridges thegent to ShareCLI's Phase 11 task coordination layer.

### Methods

#### ShareCLIBridge.__init__

```python
__init__(self)
```

#### ShareCLIBridge.broadcast_intent

WP-16003: Broadcast operation intent to the mesh.

```python
broadcast_intent(self, agent_id, intent_type, target)
```

#### ShareCLIBridge.create_shared_task

WP-16003: Create a task in ShareCLI's global task list.

```python
create_shared_task(self, task_id, description, depends_on)
```

#### ShareCLIBridge.get_session_state

WP-16003: Deep inspection of session state from ShareCLI var/ dirs.

```python
get_session_state(self, session_id)
```

#### ShareCLIBridge.is_available

Check if ShareCLI coordination layer is initialized.

```python
is_available(self)
```

---

## SmartMerge

WP-16004: AST-aware conflict resolution using Mergiraf.

### Methods

#### SmartMerge.__init__

```python
__init__(self)
```

#### SmartMerge.merge_files

Attempt an AST-aware merge using Mergiraf or standard git merge-file.

```python
merge_files(self, base, ours, theirs, output)
```

---

## broadcast_intent

WP-16003: Broadcast operation intent to the mesh.

```python
broadcast_intent(self, agent_id, intent_type, target)
```

---

## create_shared_task

WP-16003: Create a task in ShareCLI's global task list.

```python
create_shared_task(self, task_id, description, depends_on)
```

---

## get_session_state

WP-16003: Deep inspection of session state from ShareCLI var/ dirs.

```python
get_session_state(self, session_id)
```

---

## is_available

Check if ShareCLI coordination layer is initialized.

```python
is_available(self)
```

---

## merge_files

Attempt an AST-aware merge using Mergiraf or standard git merge-file.

```python
merge_files(self, base, ours, theirs, output)
```

---

