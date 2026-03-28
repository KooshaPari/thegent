# textual_app API Reference

> **Source**: `src/thegent/ui/compositor/textual_app.py`

CompositorApp - Agent-oriented Textual application with sidebar and output pane.

Provides TUIContext, CompositorApp (with sidebar/maximize toggle, output writing,
agent status), and run_tui() for launching the TUI from code or the CLI.

---

## CompositorApp

Agent-oriented TUI application for thegent.

Features:
- Menubar with file/edit/view/tools/help menus
- Output pane for agent output with write/append helpers
- Sidebar with session/agent status info
- Sidebar toggle and output maximize actions
- Keybindings for navigation and layout control
- TUI context (session_id, agent_name, cwd) threading through UI

**Inherits from**: `App`

### Methods

#### CompositorApp.__init__

```python
__init__(self: Any, context: Any)
```

---

#### CompositorApp.action_focus_next

```python
action_focus_next(self: Any)
```

Focus the next pane.

---

#### CompositorApp.action_focus_prev

```python
action_focus_prev(self: Any)
```

Focus the previous pane.

---

#### CompositorApp.action_quit

```python
action_quit(self: Any)
```

Quit the application.

---

#### CompositorApp.action_show_help

```python
action_show_help(self: Any)
```

Show help dialog.

---

#### CompositorApp.action_toggle_maximize

```python
action_toggle_maximize(self: Any)
```

Toggle output pane maximization.

---

#### CompositorApp.action_toggle_sidebar

```python
action_toggle_sidebar(self: Any)
```

Toggle sidebar visibility.

---

#### CompositorApp.append_output

```python
append_output(self: Any, text: str)
```

Append text to output pane.

---

#### CompositorApp.compose

```python
compose(self: Any)
```

Create the UI layout.

---

#### CompositorApp.on_mount

```python
on_mount(self: Any)
```

Initialize the app after mounting.

---

#### CompositorApp.set_agent_status

```python
set_agent_status(self: Any, agent_status: str, agent: str)
```

Update agent status display.

---

#### CompositorApp.update_status

```python
update_status(self: Any)
```

Update status display.

---

#### CompositorApp.update_title

```python
update_title(self: Any)
```

Update window title.

---

#### CompositorApp.write_output

```python
write_output(self: Any, text: str)
```

Write text to output pane.

---

---

## TUIContext

Context passed to all widgets/components.

### Methods

#### TUIContext.__init__

```python
__init__(self: Any, session_id: Any, agent_name: Any, cwd: Any)
```

---

---

## action_focus_next

```python
action_focus_next(self: Any)
```

Focus the next pane.

---

## action_focus_prev

```python
action_focus_prev(self: Any)
```

Focus the previous pane.

---

## action_quit

```python
action_quit(self: Any)
```

Quit the application.

---

## action_show_help

```python
action_show_help(self: Any)
```

Show help dialog.

---

## action_toggle_maximize

```python
action_toggle_maximize(self: Any)
```

Toggle output pane maximization.

---

## action_toggle_sidebar

```python
action_toggle_sidebar(self: Any)
```

Toggle sidebar visibility.

---

## append_output

```python
append_output(self: Any, text: str)
```

Append text to output pane.

---

## compose

```python
compose(self: Any)
```

Create the UI layout.

---

## on_mount

```python
on_mount(self: Any)
```

Initialize the app after mounting.

---

## set_agent_status

```python
set_agent_status(self: Any, agent_status: str, agent: str)
```

Update agent status display.

---

## update_status

```python
update_status(self: Any)
```

Update status display.

---

## update_title

```python
update_title(self: Any)
```

Update window title.

---

## write_output

```python
write_output(self: Any, text: str)
```

Write text to output pane.

---

