# pane_manager API Reference

> **Source**: `src/thegent/compositor/pane_manager.py`

Pane management for the TUI compositor.

Handles pane tree structure, splitting, merging, and layout operations.

---

## PaneManager

Manages a tree of terminal panes with split/merge operations.

### Methods

#### PaneManager.__init__

```python
__init__(self: Any, initial_dir: str)
```

Initialize the pane manager with a root pane.

**Parameters**:

- `initial_dir`: Initial working directory for the root pane

---

#### PaneManager.close_pane

```python
close_pane(self: Any, pane_id: Any)
```

Close a pane and rebalance the tree.

**Parameters**:

- `pane_id`: ID of pane to close (default: focused pane)

**Returns**: True if pane was closed, False if it's the only pane

---

#### PaneManager.focus_next

```python
focus_next(self: Any)
```

Rotate focus to the next pane.

---

#### PaneManager.get_all_panes

```python
get_all_panes(self: Any)
```

Get all panes in the tree.

---

#### PaneManager.get_focused_pane

```python
get_focused_pane(self: Any)
```

Get the currently focused pane node.

---

#### PaneManager.get_pane_by_id

```python
get_pane_by_id(self: Any, pane_id: str)
```

Get a pane node by its ID.

---

#### PaneManager.get_pane_count

```python
get_pane_count(self: Any)
```

Get the number of terminal panes.

---

#### PaneManager.restore_layout

```python
restore_layout(self: Any, layout_data: dict)
```

Restore a pane tree from a serialized layout.

**Parameters**:

- `layout_data`: Serialized layout data

**Returns**: True if restoration was successful

---

#### PaneManager.save_layout

```python
save_layout(self: Any)
```

Serialize the pane tree to a dictionary.

---

#### PaneManager.split_pane

```python
split_pane(self: Any, direction: str, pane_id: Any)
```

Split a pane in the specified direction.

**Parameters**:

- `direction`: 'H' for horizontal split, 'V' for vertical split
- `pane_id`: ID of pane to split (default: focused pane)

**Returns**: The new pane node, or None if split failed

---

---

## PaneNode

A node in the pane tree structure.

### Methods

#### PaneNode.is_branch

```python
is_branch(self: Any)
```

Check if this node is a branch (has children).

---

#### PaneNode.is_leaf

```python
is_leaf(self: Any)
```

Check if this node is a leaf (contains a pane).

---

---

## close_pane

```python
close_pane(self: Any, pane_id: Any)
```

Close a pane and rebalance the tree.

**Parameters**:

- `pane_id`: ID of pane to close (default: focused pane)

**Returns**: True if pane was closed, False if it's the only pane

---

## focus_next

```python
focus_next(self: Any)
```

Rotate focus to the next pane.

---

## get_all_panes

```python
get_all_panes(self: Any)
```

Get all panes in the tree.

---

## get_focused_pane

```python
get_focused_pane(self: Any)
```

Get the currently focused pane node.

---

## get_pane_by_id

```python
get_pane_by_id(self: Any, pane_id: str)
```

Get a pane node by its ID.

---

## get_pane_count

```python
get_pane_count(self: Any)
```

Get the number of terminal panes.

---

## is_branch

```python
is_branch(self: Any)
```

Check if this node is a branch (has children).

---

## is_leaf

```python
is_leaf(self: Any)
```

Check if this node is a leaf (contains a pane).

---

## restore_layout

```python
restore_layout(self: Any, layout_data: dict)
```

Restore a pane tree from a serialized layout.

**Parameters**:

- `layout_data`: Serialized layout data

**Returns**: True if restoration was successful

---

## save_layout

```python
save_layout(self: Any)
```

Serialize the pane tree to a dictionary.

---

## split_pane

```python
split_pane(self: Any, direction: str, pane_id: Any)
```

Split a pane in the specified direction.

**Parameters**:

- `direction`: 'H' for horizontal split, 'V' for vertical split
- `pane_id`: ID of pane to split (default: focused pane)

**Returns**: The new pane node, or None if split failed

---

