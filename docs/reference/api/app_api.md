# app API Reference

> **Source**: `src/thegent/compositor/app.py`

Main Textual application for the TUI compositor.

Provides the CompositApp class which manages the overall UI layout including
header, footer, and pane management.

---

## CompositApp

Main TUI Compositor application.

This is a Textual application that provides a multi-pane terminal interface
with support for splitting, merging, and layout management.

**Inherits from**: `Vertical`

### Methods

#### CompositApp.__init__

```python
__init__(self: Any)
```

Initialize the CompositApp.

---

#### CompositApp.action_close_pane

```python
action_close_pane(self: Any)
```

Action: Close the current pane.

---

#### CompositApp.action_focus_next

```python
action_focus_next(self: Any)
```

Action: Focus on the next pane.

---

#### CompositApp.action_new_pane

```python
action_new_pane(self: Any)
```

Action: Create a new pane.

---

#### CompositApp.action_restore_layout

```python
action_restore_layout(self: Any)
```

Action: Restore a saved layout.

---

#### CompositApp.action_save_layout

```python
action_save_layout(self: Any)
```

Action: Save the current layout.

---

#### CompositApp.action_split_horizontal

```python
action_split_horizontal(self: Any)
```

Action: Split the current pane horizontally.

---

#### CompositApp.action_split_vertical

```python
action_split_vertical(self: Any)
```

Action: Split the current pane vertically.

---

#### CompositApp.compose

```python
compose(self: Any)
```

Compose the application layout.

---

#### CompositApp.on_mount

```python
on_mount(self: Any)
```

Called when the app is mounted.

---

#### CompositApp.on_unmount

```python
on_unmount(self: Any)
```

Called when the app is unmounted. Clean up resources.

---

#### CompositApp.save_session_state

```python
save_session_state(self: Any)
```

Save the current session state to disk.

---

#### CompositApp.update_pane_display

```python
update_pane_display(self: Any)
```

Update the pane display after tree changes.

---

#### CompositApp.update_status

```python
update_status(self: Any)
```

Update the status bar.

---

---

## PaneContainer

Container for terminal panes.

**Inherits from**: `Container`

### Methods

#### PaneContainer.__init__

```python
__init__(self: Any, pane_manager: PaneManager)
```

Initialize the pane container.

**Parameters**:

- `pane_manager`: Reference to the pane manager

---

#### PaneContainer.compose

```python
compose(self: Any)
```

Compose the pane container with the root pane.

---

---

## StatusBar

Custom status bar widget.

**Inherits from**: `Static`

### Methods

#### StatusBar.__init__

```python
__init__(self: Any, pane_manager: PaneManager)
```

Initialize the status bar.

**Parameters**:

- `pane_manager`: Reference to the pane manager

---

#### StatusBar.render

```python
render(self: Any)
```

Render the status bar with current information.

---

---

## _CompositRunner

Minimal App shell to host CompositApp widget.

**Inherits from**: `App`

### Methods

#### _CompositRunner.compose

```python
compose(self: Any)
```

---

---

## action_close_pane

```python
action_close_pane(self: Any)
```

Action: Close the current pane.

---

## action_focus_next

```python
action_focus_next(self: Any)
```

Action: Focus on the next pane.

---

## action_new_pane

```python
action_new_pane(self: Any)
```

Action: Create a new pane.

---

## action_restore_layout

```python
action_restore_layout(self: Any)
```

Action: Restore a saved layout.

---

## action_save_layout

```python
action_save_layout(self: Any)
```

Action: Save the current layout.

---

## action_split_horizontal

```python
action_split_horizontal(self: Any)
```

Action: Split the current pane horizontally.

---

## action_split_vertical

```python
action_split_vertical(self: Any)
```

Action: Split the current pane vertically.

---

## compose

```python
compose(self: Any) -> ComposeResult
```

---

## on_mount

```python
on_mount(self: Any)
```

Called when the app is mounted.

---

## on_unmount

```python
on_unmount(self: Any)
```

Called when the app is unmounted. Clean up resources.

---

## render

```python
render(self: Any)
```

Render the status bar with current information.

---

## run

Run the CompositApp.

---

## save_session_state

```python
save_session_state(self: Any)
```

Save the current session state to disk.

---

## update_pane_display

```python
update_pane_display(self: Any)
```

Update the pane display after tree changes.

---

## update_status

```python
update_status(self: Any)
```

Update the status bar.

---

