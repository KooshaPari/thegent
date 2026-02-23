# Merged Fragmented Markdown

## Source: changes/research-tui-compositor/design.md

# TUI Compositor — Technical Design

**Date**: 2026-02-18
**Status**: Design Document
**Version**: 1.0

---

## Architecture Overview

### Layered Design

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Application (Textual)                             │
│  - CompositApp (main Textual.App)                          │
│  - Menubar, Statusbar, Dialogs                             │
│  - Key bindings and event routing                          │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Compositor (Pane Management)                      │
│  - PaneManager (split, merge, focus, layout)               │
│  - LayoutSerializer (save/restore)                         │
│  - SessionState (persistent state machine)                 │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Terminal Backend (PTY)                            │
│  - TerminalPane (wraps Textual.TerminalWidget)             │
│  - PTYAllocator (PTY allocation)                            │
│  - ProcessManager (process execution and cleanup)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. CompositApp (Textual.App)

**Responsibility**: Main application container, event dispatch, UI orchestration

**File**: `thegent/src/thegent/ui/compositor/app.py`

```python
from textual.app import ComposeResult, App
from textual.widgets import Header, Footer, Container
from textual.containers import Container

class CompositApp(App):
    """Main compositor application"""

    TITLE = "Thegent Compositor"
    BINDINGS = [
        ("ctrl+n", "new_pane", "New Pane"),
        ("ctrl+v", "split_vertical", "Split Vert"),
        ("ctrl+h", "split_horizontal", "Split Horiz"),
        ("ctrl+x", "close_pane", "Close"),
        ("ctrl+l", "focus_next", "Next Pane"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.pane_manager = PaneManager(self)
        self.session_state = SessionState()

    def compose(self) -> ComposeResult:
        """Compose application widgets"""
        yield Header()
        yield Container(id="main-pane-container")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize on app mount"""
        # Load prior session or create new
        layout = self.session_state.load_session()
        if layout:
            self.pane_manager.restore_layout(layout)
        else:
            self.pane_manager.create_default_layout()

    def action_new_pane(self) -> None:
        """Create new terminal pane"""
        self.pane_manager.create_pane()

    def action_split_vertical(self) -> None:
        """Split current pane vertically"""
        self.pane_manager.split_pane("vertical")

    def action_split_horizontal(self) -> None:
        """Split current pane horizontally"""
        self.pane_manager.split_pane("horizontal")

    def action_close_pane(self) -> None:
        """Close current pane"""
        self.pane_manager.close_pane()

    def action_focus_next(self) -> None:
        """Focus next pane"""
        self.pane_manager.focus_next()
```

### 2. PaneManager

**Responsibility**: Pane lifecycle, splitting, merging, layout management, focus handling

**File**: `thegent/src/thegent/ui/compositor/pane_manager.py`

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import uuid

class SplitDirection(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

@dataclass
class PaneNode:
    """Represents a pane or split in the layout tree"""
    id: str
    pane: Optional['TerminalPane'] = None
    left: Optional['PaneNode'] = None
    right: Optional['PaneNode'] = None
    direction: Optional[SplitDirection] = None

    def is_leaf(self) -> bool:
        """Check if this is a leaf (terminal pane)"""
        return self.pane is not None

class PaneManager:
    """Manages pane layout and lifecycle"""

    def __init__(self, app: CompositApp):
        self.app = app
        self.root: Optional[PaneNode] = None
        self.focus_pane: Optional[TerminalPane] = None

    def create_pane(self, working_dir: str = ".") -> TerminalPane:
        """Create new terminal pane"""
        pane_id = str(uuid.uuid4())[:8]
        pane = TerminalPane(pane_id, working_dir)

        if self.root is None:
            self.root = PaneNode(id=pane_id, pane=pane)
        else:
            self.focus_pane.split(pane, SplitDirection.VERTICAL)

        self.focus_pane = pane
        return pane

    def split_pane(
        self,
        direction: str,
        working_dir: str = "."
    ) -> TerminalPane:
        """Split current pane in given direction"""
        if self.focus_pane is None:
            return self.create_pane(working_dir)

        new_pane = TerminalPane(str(uuid.uuid4())[:8], working_dir)
        self.focus_pane.split(new_pane, SplitDirection(direction))
        self.focus_pane = new_pane
        return new_pane

    def close_pane(self) -> None:
        """Close current pane"""
        if self.focus_pane:
            self.focus_pane.close()
            # TODO: Rebalance layout, move focus

    def focus_next(self) -> None:
        """Focus next pane in rotation"""
        # Traverse tree in-order, find next after current
        panes = self._collect_panes(self.root)
        if not panes:
            return

        current_idx = panes.index(self.focus_pane)
        next_idx = (current_idx + 1) % len(panes)
        self.focus_pane = panes[next_idx]
        self.focus_pane.focus()

    def restore_layout(self, layout_data: dict) -> None:
        """Restore pane layout from serialized data"""
        self.root = self._deserialize_tree(layout_data)

    def save_layout(self) -> dict:
        """Serialize current layout to dict"""
        return self._serialize_tree(self.root)

    def _collect_panes(self, node: Optional[PaneNode]) -> list[TerminalPane]:
        """Collect all panes in in-order traversal"""
        if node is None:
            return []

        if node.is_leaf():
            return [node.pane]

        result = []
        result.extend(self._collect_panes(node.left))
        result.extend(self._collect_panes(node.right))
        return result

    def _serialize_tree(self, node: Optional[PaneNode]) -> dict:
        """Serialize pane tree to dict"""
        if node is None:
            return {}

        if node.is_leaf():
            return {
                "type": "pane",
                "id": node.id,
                "working_dir": node.pane.working_dir,
            }

        return {
            "type": "split",
            "direction": node.direction.value,
            "left": self._serialize_tree(node.left),
            "right": self._serialize_tree(node.right),
        }

    def _deserialize_tree(self, data: dict) -> Optional[PaneNode]:
        """Deserialize pane tree from dict"""
        if not data:
            return None

        if data["type"] == "pane":
            pane = TerminalPane(data["id"], data["working_dir"])
            return PaneNode(id=data["id"], pane=pane)

        # Recursively deserialize children
        left = self._deserialize_tree(data.get("left", {}))
        right = self._deserialize_tree(data.get("right", {}))

        return PaneNode(
            id=str(uuid.uuid4())[:8],
            left=left,
            right=right,
            direction=SplitDirection(data["direction"]),
        )
```

### 3. TerminalPane

**Responsibility**: PTY allocation, terminal widget, process execution

**File**: `thegent/src/thegent/ui/compositor/terminal_pane.py`

```python
from textual.widgets import Static
import pty
import os
import subprocess
from dataclasses import dataclass

class TerminalPane(Static):
    """Terminal pane widget wrapping PTY"""

    def __init__(self, pane_id: str, working_dir: str = "."):
        super().__init__()
        self.pane_id = pane_id
        self.working_dir = working_dir
        self.pty_fd: Optional[int] = None
        self.process_pid: Optional[int] = None

    def render(self) -> str:
        """Render terminal pane content"""
        # TODO: Read from PTY, render output
        return f"[Pane {self.pane_id}]\n{self.working_dir}"

    def spawn_shell(self, shell: str = "/bin/bash") -> None:
        """Spawn shell in PTY"""
        pid, self.pty_fd = pty.openpty()

        fork_pid = os.fork()
        if fork_pid == 0:
            # Child process
            os.close(pid)
            os.setsid()
            os.dup2(self.pty_fd, 0)  # stdin
            os.dup2(self.pty_fd, 1)  # stdout
            os.dup2(self.pty_fd, 2)  # stderr
            os.chdir(self.working_dir)
            os.execvp(shell, [shell])
        else:
            # Parent process
            os.close(self.pty_fd)
            self.process_pid = fork_pid

    def write_input(self, data: bytes) -> None:
        """Write input to PTY"""
        if self.pty_fd:
            os.write(self.pty_fd, data)

    def close(self) -> None:
        """Close terminal pane and cleanup"""
        if self.process_pid:
            os.kill(self.process_pid, 15)  # SIGTERM
            os.waitpid(self.process_pid, 0)
        if self.pty_fd:
            os.close(self.pty_fd)
```

### 4. SessionState

**Responsibility**: Session lifecycle, persistence, restoration

**File**: `thegent/src/thegent/ui/compositor/session_state.py`

```python
import yaml
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SessionMetadata:
    """Session metadata"""
    id: str
    name: str
    created_at: str
    updated_at: str
    working_dir: str

class SessionState:
    """Manages session state and persistence"""

    SESSION_DIR = Path.home() / ".config" / "thegent" / "sessions"
    LAYOUTS_DIR = Path.home() / ".config" / "thegent" / "layouts"

    def __init__(self):
        self.SESSION_DIR.mkdir(parents=True, exist_ok=True)
        self.LAYOUTS_DIR.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[SessionMetadata] = None

    def load_session(self, session_id: Optional[str] = None) -> Optional[dict]:
        """Load session state from disk"""
        if session_id is None:
            session_id = self._get_last_session_id()

        if not session_id:
            return None

        session_file = self.SESSION_DIR / f"{session_id}.yaml"
        if not session_file.exists():
            return None

        with open(session_file) as f:
            return yaml.safe_load(f)

    def save_session(self, session_id: str, layout: dict) -> None:
        """Save session state to disk"""
        session_data = {
            "id": session_id,
            "layout": layout,
            "updated_at": datetime.now().isoformat(),
        }

        session_file = self.SESSION_DIR / f"{session_id}.yaml"
        with open(session_file, "w") as f:
            yaml.dump(session_data, f)

    def save_layout(self, layout_name: str, layout: dict) -> None:
        """Save layout template"""
        layout_file = self.LAYOUTS_DIR / f"{layout_name}.yaml"
        with open(layout_file, "w") as f:
            yaml.dump(layout, f)

    def list_layouts(self) -> list[str]:
        """List available layout templates"""
        return [f.stem for f in self.LAYOUTS_DIR.glob("*.yaml")]

    def _get_last_session_id(self) -> Optional[str]:
        """Get ID of most recent session"""
        sessions = sorted(self.SESSION_DIR.glob("*.yaml"))
        if not sessions:
            return None
        return sessions[-1].stem
```

### 5. Menubar & Statusbar

**Responsibility**: User interface and status display

**File**: `thegent/src/thegent/ui/compositor/widgets.py`

```python
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive

class CompositHeader(Header):
    """Header with menus"""

    def __init__(self):
        super().__init__()
        self.show_header_and_footer = True

class CompositFooter(Footer):
    """Footer with statusbar"""

    session_name = reactive("Untitled")
    agent_status = reactive("idle")
    pane_count = reactive(1)

    def render(self) -> str:
        """Render statusbar"""
        return (
            f"Session: {self.session_name} | "
            f"Agent: {self.agent_status} | "
            f"Panes: {self.pane_count}"
        )
```

---

## Keyboard Shortcut Map

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+N` | `new_pane` | Create new pane |
| `Ctrl+H` | `split_horizontal` | Split current pane horizontally |
| `Ctrl+V` | `split_vertical` | Split current pane vertically |
| `Ctrl+X` | `close_pane` | Close current pane |
| `Ctrl+L` | `focus_next` | Focus next pane (rotate) |
| `Ctrl+S` | `save_layout` | Save current layout |
| `Ctrl+R` | `restore_layout` | Restore saved layout |
| `Ctrl+Q` | `quit` | Quit application |

---

## Data Model: Session & Layout

### Session YAML Format

```yaml
id: "session-20260218-143022"
name: "Development"
created_at: "2026-02-18T14:30:22Z"
updated_at: "2026-02-18T14:35:45Z"
working_dir: "/Users/kush/projects/thegent"
layout:
  type: "split"
  direction: "vertical"
  left:
    type: "pane"
    id: "pane-1"
    working_dir: "/Users/kush/projects/thegent"
  right:
    type: "split"
    direction: "horizontal"
    left:
      type: "pane"
      id: "pane-2"
      working_dir: "/Users/kush/projects/thegent"
    right:
      type: "pane"
      id: "pane-3"
      working_dir: "/Users/kush/projects/thegent"
```

### Layout Template Format

```yaml
name: "Three-Pane Layout"
description: "Vertical split with two right panes"
template:
  type: "split"
  direction: "vertical"
  left:
    type: "pane"
    working_dir: "."
  right:
    type: "split"
    direction: "horizontal"
    # ... nested structure
```

---

## Concurrency & Async Model

### Event Loop Integration

```python
# Integrate with Textual's event loop
async def on_terminal_output(self, pane_id: str, data: bytes):
    """Handle terminal output from PTY"""
    pane = self.pane_manager.get_pane(pane_id)
    if pane:
        pane.append_output(data)
        self.refresh()

async def on_resize(self):
    """Handle terminal resize"""
    # Update all panes with new dimensions
    self.pane_manager.resize_all_panes()
```

---

## Testing Strategy

### Unit Tests

- **PaneManager**: Tree structure, split/merge operations
- **SessionState**: Serialization/deserialization
- **LayoutSerializer**: YAML round-trip

### Integration Tests

- **CompositApp**: Full app initialization
- **TerminalPane**: PTY allocation and cleanup
- **Layout persistence**: Save/restore cycle

### E2E Tests

- User workflows (split, focus, close, save)
- Session recovery after restart

---

## Performance Targets

| Operation | Target | Strategy |
|-----------|--------|----------|
| App startup | <500ms | Lazy load layouts, defer async tasks |
| Pane creation | <100ms | Pre-allocate PTY descriptors |
| Layout switch | <50ms | In-memory layout tree, no disk I/O |
| Idle memory | <100MB | Limit output buffer per pane |
| Idle CPU | <2% | No active polling; event-driven |

---

## References

- **Textual Docs**: https://textual.textualize.io/
- **PTY Programming**: https://man7.org/linux/man-pages/man7/pty.7.html
- **tmux Source**: https://github.com/tmux/tmux
- **Zellij Layout Docs**: https://zellij.dev/documentation/layouts

---

## Source: changes/research-tui-compositor/proposal.md

# TUI Compositor Implementation Proposal

**Date**: 2026-02-18
**Source**: [CONVERSATION_DUMP_2026-02-16_EXPANDED.md](../../research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md) § 2
**Status**: Proposed
**Priority**: P1

---

## Executive Summary

Implement a **TUI Compositor** (terminal user interface compositor and multiplexer) to serve as the primary dashboard and control plane for the **Sitback Agent** and broader **thegent** system. The compositor will provide GUI-like experience (menus, statusbars, dialogs) with terminal pane splitting, process management, and real-time monitoring.

**Key Goals**:
- Unified control plane for agent orchestration and monitoring
- GUI-like experience (menubar, statusbar, keyboard shortcuts) in terminal
- Real-time process and session tracking
- Session persistence and layout management

---

## Problem Statement

**Current State**:
- Multiple disconnected UIs: shell prompt, separate tmux sessions, log files
- Sitback and other agents lack a unified dashboard
- No centralized view of running agents, tasks, and system state
- Users must manually manage terminal panes and sessions

**Desired State**:
- Single unified TUI dashboard
- Menubar navigation (File, Edit, View, Tools, Help)
- Statusbar showing session/agent status in real-time
- Pane splitting and layout management
- Session persistence across restarts

---

## Requirements

### Functional Requirements

| FR-ID | Description | Priority |
|-------|-------------|----------|
| **FR-TUI-001** | Menubar with File/Edit/View/Tools/Help menus | P0 |
| **FR-TUI-002** | Statusbar displaying current session, agent, status | P0 |
| **FR-TUI-003** | Horizontal and vertical pane splitting | P0 |
| **FR-TUI-004** | Terminal pane widget supporting shell interaction | P1 |
| **FR-TUI-005** | Floating window support (dialogs, alerts) | P1 |
| **FR-TUI-006** | Layout save/restore (via YAML or JSON) | P1 |
| **FR-TUI-007** | Session persistence across application restarts | P1 |
| **FR-TUI-008** | Keyboard shortcuts (Ctrl+C, Ctrl+N, Ctrl+V, etc.) | P0 |
| **FR-TUI-009** | Real-time process monitoring (CPU, memory) | P2 |
| **FR-TUI-010** | Integration with thegent work stream (do-next, claim, complete) | P2 |
| **FR-TUI-011** | Web export via `textual serve` (optional) | P3 |
| **FR-TUI-012** | Theme customization (light/dark) | P2 |

### Non-Functional Requirements

| NFR-ID | Requirement | Target |
|--------|-------------|--------|
| **NFR-TUI-001** | App startup latency | <500ms |
| **NFR-TUI-002** | Pane creation latency | <100ms |
| **NFR-TUI-003** | Layout switch latency | <50ms |
| **NFR-TUI-004** | Memory footprint | <100MB idle |
| **NFR-TUI-005** | CPU usage (idle) | <2% |
| **NFR-TUI-006** | Responsiveness to user input | <50ms |

---

## Technology Selection

### Framework: **Textual** (Python)

**Rationale**:
- Written in Python (matches thegent stack)
- CSS-like styling for maintainable UI code
- Rich widget library (menus, buttons, inputs, trees, etc.)
- `textual serve` for web export (future enhancement)
- Strong documentation and active community
- Easy integration with Python async code

**Alternatives Considered**:
- **Ratatui (Rust)**: More performant but requires Rust integration
- **Bubble Tea (Go)**: Not Python; would require separate service
- **Zellij (Rust)**: Compositor, but less control over UI

### Compositor Strategy: **Embedded Terminal Panes**

**Approach**:
- Use Textual's `TerminalWidget` (or equivalent) to embed PTY-based terminal panes
- Build custom layout manager on top
- Implement session state machine

**Alternative**: Use Zellij as backend compositor + custom Textual plugin (more complex)

---

## High-Level Architecture

### Layered Model

```
┌──────────────────────────────────────────────────┐
│  GUI-like Menu Layer (Textual)                   │
│  - Menubar (File, Edit, View, Tools, Help)      │
│  - Statusbar (session info, agent status)       │
│  - Dialogs (confirmations, inputs)              │
│  - Keyboard shortcuts (Ctrl+C, Ctrl+V, etc.)    │
└──────────────────────────────────────────────────┘
                        │
┌──────────────────────────────────────────────────┐
│  TUI Compositor Layer                            │
│  - Pane management (split, merge, focus)        │
│  - Floating window support                       │
│  - Layout management (save/restore)             │
│  - Session persistence                           │
└──────────────────────────────────────────────────┘
                        │
┌──────────────────────────────────────────────────┐
│  Terminal Emulator / PTY Layer                   │
│  - PTY allocation                                │
│  - Process execution                             │
│  - Output rendering                              │
└──────────────────────────────────────────────────┘
```

### Component Breakdown

| Component | Purpose | Technology | Status |
|-----------|---------|-----------|--------|
| **App** | Main Textual application | Textual | To design |
| **Menubar** | Top-level menu navigation | Textual Menu | To design |
| **Statusbar** | Real-time status display | Textual Footer | To design |
| **PaneManager** | Split/merge/layout logic | Custom Python | To implement |
| **TerminalPane** | PTY-based terminal widget | Textual TerminalWidget | To implement |
| **Session** | Persistent session state | YAML/JSON | To design |
| **Keyboard** | Shortcut handling | Textual key bindings | To implement |

---

## Design Decisions

### D1: Framework Choice
**Decision**: Use **Textual** for TUI framework
**Rationale**: Python stack alignment, CSS styling, rich widgets, active community
**Alternatives Rejected**: Ratatui (requires Rust), Bubble Tea (Go-only)
**Tradeoff**: Textual may be slightly slower than Rust alternatives, but alignment with thegent stack outweighs performance cost

### D2: Terminal Pane Implementation
**Decision**: Use **Textual TerminalWidget** for embedded terminals
**Rationale**: Native Textual support, PTY integration, no external process needed
**Alternatives Rejected**: Zellij as compositor (more complex), tmux subprocess (harder to integrate)
**Tradeoff**: Embedded approach requires more development, but offers better integration

### D3: Layout Persistence
**Decision**: Save layouts to **YAML files** in `~/.config/thegent/layouts/`
**Rationale**: Human-readable, version-control friendly, easy to template
**Alternatives Rejected**: JSON (more verbose), binary (not human-readable)
**Tradeoff**: YAML is slightly slower to parse, but benefits outweigh

### D4: Session Model
**Decision**: Use **hierarchical session tree** (workspace → pane group → pane)
**Rationale**: Matches tmux/Zellij concepts, supports complex layouts
**Alternatives Rejected**: Flat session list (less flexible)
**Tradeoff**: More complex state management, but more powerful

---

## Acceptance Criteria

- [ ] **AC-1**: App starts in <500ms
- [ ] **AC-2**: Menubar with File/Edit/View/Tools/Help menus fully functional
- [ ] **AC-3**: Statusbar displays session name, agent status, real-time clock
- [ ] **AC-4**: Can split panes horizontally and vertically; focus switching works
- [ ] **AC-5**: Terminal panes execute shell commands and display output
- [ ] **AC-6**: Keyboard shortcuts work (Ctrl+N=new pane, Ctrl+V=vsplit, Ctrl+X=close)
- [ ] **AC-7**: Layouts can be saved to and restored from YAML
- [ ] **AC-8**: Session state persists across app restart
- [ ] **AC-9**: All linters pass (ruff, type checking); no new lint suppressions
- [ ] **AC-10**: Test coverage ≥80% for compositor core logic

---

## Related Documents

- **Architecture**: [../design.md](./design.md)
- **Implementation Tasks**: [../tasks.md](./tasks.md)
- **Research**: [../../research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md](../../research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md) § 2
- **Related Work**: [../../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md](../../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md)
- **Tech Stacks**: [../../reference/TECHNOLOGY_STACK_AND_FRAMEWORKS.md](../../reference/TECHNOLOGY_STACK_AND_FRAMEWORKS.md)

---

## See Also

- Textual Documentation: https://textual.textualize.io/
- Zellij Compositor: https://zellij.dev/
- tmux Reference: https://man7.org/linux/man-pages/man1/tmux.1.html

---

## Source: changes/research-tui-compositor/tasks.md

---
task_id: research-tui-compositor
status: in_progress
---

# TUI Compositor — Implementation Tasks

**Date**: 2026-02-18
**Status**: Task Breakdown
**Version**: 1.0

---

## Phase 1: Foundation (Week 1)

### Goal
Basic Textual app with menubar, statusbar, and single terminal pane.

### Tasks

#### P1.1: Project Setup & Dependencies
**Depends on**: None
**Effort**: 1-2 hours

- [ ] Create new module: `thegent/src/thegent/ui/compositor/`
- [ ] Create `__init__.py`, `app.py`, `pane_manager.py`, `session_state.py`
- [ ] Add Textual to `pyproject.toml` dependencies
- [ ] Create test directory: `tests/ui/compositor/`
- [ ] Set up pytest fixtures for testing

**Acceptance Criteria**:
- All files created and importable
- `pytest` finds test directory
- No import errors

**Checklist**:
- [ ] `pyproject.toml` updated
- [ ] Module structure created
- [ ] Tests discoverable
- [ ] Linters pass (ruff, type checking)

---

#### P1.2: CompositApp Skeleton
**Depends on**: P1.1
**Effort**: 2-3 hours

- [ ] Implement `CompositApp` class (Textual.App)
- [ ] Add `Header`, `Footer` widgets
- [ ] Implement basic key bindings
- [ ] Add logging and debug output

**Code**:
```python
# thegent/src/thegent/ui/compositor/app.py
class CompositApp(App):
    TITLE = "Thegent Compositor"
    BINDINGS = [
        ("ctrl+n", "new_pane", "New Pane"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(id="main-pane-container")
        yield Footer()
```

**Acceptance Criteria**:
- App starts without errors
- Header/Footer render correctly
- Quit binding works (Ctrl+Q)

**Checklist**:
- [ ] CompositApp renders
- [ ] Header displays "Thegent Compositor"
- [ ] Ctrl+Q quits cleanly
- [ ] Unit tests written

---

#### P1.3: TerminalPane Widget
**Depends on**: P1.1
**Effort**: 3-4 hours

- [ ] Implement `TerminalPane` class
- [ ] Add PTY allocation and shell spawning
- [ ] Implement input/output handling
- [ ] Add cleanup on pane close

**Code**:
```python
# thegent/src/thegent/ui/compositor/terminal_pane.py
class TerminalPane(Static):
    def __init__(self, pane_id: str, working_dir: str = "."):
        super().__init__()
        self.pane_id = pane_id
        self.working_dir = working_dir

    def spawn_shell(self, shell: str = "/bin/bash") -> None:
        # Allocate PTY, fork shell
        pass
```

**Acceptance Criteria**:
- PTY allocation succeeds
- Shell spawns and renders in pane
- Input echoes to terminal
- Pane closes cleanly

**Checklist**:
- [ ] PTY allocated
- [ ] Shell runs in pane
- [ ] Input/output working
- [ ] Cleanup implemented
- [ ] Unit tests written

---

#### P1.4: Basic Integration & Single-Pane Demo
**Depends on**: P1.2, P1.3
**Effort**: 2-3 hours

- [ ] Connect `CompositApp` to `TerminalPane`
- [ ] Implement `action_new_pane()` to create and display pane
- [ ] Test startup with single pane
- [ ] Add logging and debug output

**Acceptance Criteria**:
- App starts with one terminal pane
- Pane is interactive (can type, execute commands)
- Pane renders output correctly

**Checklist**:
- [ ] CompositApp displays TerminalPane
- [ ] Terminal is interactive
- [ ] Commands execute in pane
- [ ] App is stable (no crashes)

---

### Phase 1 Testing

**Test Coverage Target**: 80%

- [ ] Unit tests for `TerminalPane` (PTY operations)
- [ ] Unit tests for `CompositApp` (app initialization)
- [ ] Integration test (app start + interactive pane)
- [ ] Run `pytest` with coverage report

---

### Phase 1 Deliverables

1. **Working single-pane app**
   - App starts in <500ms
   - Terminal pane is interactive
   - Ctrl+Q quits cleanly
   - All tests passing

2. **Documentation**
   - `design.md` (completed)
   - `README.md` for compositor module
   - Developer setup guide

3. **Code Quality**
   - No lint errors (ruff pass)
   - Type annotations complete
   - Test coverage ≥80%

---

## Phase 2: Compositor Integration (Week 2)

### Goal
Implement pane splitting, merging, layout management, and session persistence.

### Tasks

#### P2.1: PaneManager Foundation
**Depends on**: P1.4
**Effort**: 3-4 hours

- [ ] Implement `PaneNode` data structure
- [ ] Implement `PaneManager` tree operations
- [ ] Add split/merge logic for horizontal and vertical splits
- [ ] Implement pane focus tracking

**Code**:
```python
# thegent/src/thegent/ui/compositor/pane_manager.py
class PaneManager:
    def split_pane(self, direction: str) -> TerminalPane:
        # Split current pane, create new pane
        pass

    def close_pane(self) -> None:
        # Close current pane, rebalance layout
        pass

    def focus_next(self) -> None:
        # Rotate focus to next pane
        pass
```

**Acceptance Criteria**:
- Split operations create correct tree structure
- Close operations remove panes and rebalance
- Focus rotation works correctly

**Checklist**:
- [ ] Tree structure correct
- [ ] Split operations tested
- [ ] Close operations tested
- [ ] Focus rotation tested
- [ ] Unit tests written (80%+ coverage)

---

#### P2.2: UI Integration for Pane Operations
**Depends on**: P2.1, P1.4
**Effort**: 2-3 hours

- [ ] Integrate `PaneManager` into `CompositApp`
- [ ] Implement `action_split_horizontal()`, `action_split_vertical()`
- [ ] Implement `action_close_pane()`, `action_focus_next()`
- [ ] Update statusbar to show pane count

**Acceptance Criteria**:
- All split/merge/close/focus actions work
- Statusbar updates correctly
- Layout renders properly after operations

**Checklist**:
- [ ] Ctrl+H/V split correctly
- [ ] Ctrl+X closes pane
- [ ] Ctrl+L focuses next pane
- [ ] Statusbar reflects pane count
- [ ] Integration tests written

---

#### P2.3: Layout Serialization
**Depends on**: P2.1
**Effort**: 2-3 hours

- [ ] Implement `PaneManager.save_layout()` (tree → dict)
- [ ] Implement `PaneManager.restore_layout()` (dict → tree)
- [ ] Test round-trip serialization
- [ ] Test YAML compatibility

**Code**:
```python
# thegent/src/thegent/ui/compositor/pane_manager.py
def save_layout(self) -> dict:
    return self._serialize_tree(self.root)

def restore_layout(self, layout_data: dict) -> None:
    self.root = self._deserialize_tree(layout_data)
```

**Acceptance Criteria**:
- Tree serialization produces valid dict
- Deserialization reconstructs identical tree
- YAML round-trip preserves structure

**Checklist**:
- [ ] Serialization implemented
- [ ] Deserialization implemented
- [ ] Round-trip tests written
- [ ] YAML tests written

---

#### P2.4: Session Persistence
**Depends on**: P2.3
**Effort**: 2-3 hours

- [ ] Implement `SessionState` class
- [ ] Add `save_session()` to persist state to disk
- [ ] Add `load_session()` to restore from disk
- [ ] Integrate into `CompositApp.on_mount()`

**Acceptance Criteria**:
- Sessions save to YAML successfully
- Sessions load from disk correctly
- App restores previous layout on restart

**Checklist**:
- [ ] SessionState class implemented
- [ ] Session dir created (`~/.config/thegent/sessions/`)
- [ ] Save/load round-trip tested
- [ ] Integration test (restart app)
- [ ] Unit tests written

---

#### P2.5: Layout Management UI
**Depends on**: P2.4
**Effort**: 2-3 hours

- [ ] Add `action_save_layout(name)` to save custom layouts
- [ ] Add `action_restore_layout(name)` to load layouts
- [ ] Implement layout selection menu
- [ ] Add Ctrl+S/Ctrl+R shortcuts

**Acceptance Criteria**:
- Named layouts can be saved and restored
- Layout menu displays available layouts
- Shortcuts work correctly

**Checklist**:
- [ ] Save layout action implemented
- [ ] Restore layout action implemented
- [ ] Layout menu implemented
- [ ] Shortcuts work (Ctrl+S, Ctrl+R)
- [ ] Integration tests written

---

### Phase 2 Testing

**Test Coverage Target**: 80%

- [ ] Unit tests for `PaneManager` (tree operations, serialization)
- [ ] Unit tests for `SessionState` (persistence)
- [ ] Integration tests (UI actions → layout changes)
- [ ] E2E test (session restart + recovery)
- [ ] Run `pytest` with coverage report

---

### Phase 2 Deliverables

1. **Functional multi-pane compositor**
   - Pane splitting works (H/V)
   - Pane merging works
   - Layout switching works
   - Session persistence works

2. **Performance benchmarks**
   - Pane creation: <100ms
   - Layout switch: <50ms
   - Session load: <200ms

3. **Documentation**
   - Layout YAML schema documented
   - Session file format documented
   - User guide for layout management

---

## Phase 3: Advanced Features (Week 3)

### Goal
Add floating windows, plugin system, themes, and optional web export.

### Tasks

#### P3.1: Floating Windows & Dialogs
**Depends on**: P2.5
**Effort**: 3-4 hours

- [ ] Implement `FloatingWindow` widget
- [ ] Add confirmation dialogs (close pane, quit, unsaved)
- [ ] Add input dialogs (new pane working dir, layout name)
- [ ] Add info/error message popups

**Acceptance Criteria**:
- Dialogs render correctly
- Dialog actions work (confirm/cancel)
- Input dialogs capture text

**Checklist**:
- [ ] FloatingWindow implemented
- [ ] Confirmation dialogs working
- [ ] Input dialogs working
- [ ] Message popups working

---

#### P3.2: Theme Support
**Depends on**: P1.2
**Effort**: 2-3 hours

- [ ] Add theme configuration (light/dark)
- [ ] Implement CSS styling for themes
- [ ] Add theme switching via menu
- [ ] Store theme preference in session

**Acceptance Criteria**:
- Light and dark themes display correctly
- Theme switching works
- Theme preference persists

**Checklist**:
- [ ] CSS styles created
- [ ] Light/dark themes working
- [ ] Theme switching implemented
- [ ] Preference persistence working

---

#### P3.3: Real-Time Process Monitoring (Optional)
**Depends on**: P1.3
**Effort**: 2-3 hours

- [ ] Add CPU/memory usage tracking per pane
- [ ] Display process info in statusbar
- [ ] Add process tree view (optional)

**Acceptance Criteria**:
- Process stats display in statusbar
- Stats update in real-time
- No significant performance impact

**Checklist**:
- [ ] Process monitoring implemented
- [ ] Statusbar displays stats
- [ ] Performance acceptable

---

#### P3.4: Web Export (Optional)
**Depends on**: P3.1
**Effort**: 2-3 hours

- [ ] Set up `textual serve` integration
- [ ] Export app to web version
- [ ] Test web version functionality

**Acceptance Criteria**:
- `textual serve` exports app successfully
- Web version is functional

**Checklist**:
- [ ] Web export working
- [ ] Web UI functional

---

### Phase 3 Testing

**Test Coverage Target**: 75%

- [ ] Unit tests for floating windows
- [ ] Integration tests for theme switching
- [ ] E2E tests for dialogs

---

### Phase 3 Deliverables

1. **Feature-complete compositor**
   - All advanced features working
   - Theme support
   - Optional web export

2. **Performance benchmarks**
   - Memory usage: <100MB idle
   - CPU usage: <2% idle

3. **Documentation**
   - User manual
   - Plugin development guide
   - Theme customization guide

---

## Quality Gates

### Code Quality

- [ ] All files pass `ruff check`
- [ ] All files pass type checking (`pyright` or `mypy`)
- [ ] No new lint suppressions without justification
- [ ] Test coverage ≥80% for compositor core

### Testing

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] E2E tests for key workflows
- [ ] Manual testing (interactive pane, splits, persistence)

### Performance

- [ ] App startup: <500ms
- [ ] Pane creation: <100ms
- [ ] Layout switch: <50ms
- [ ] Idle memory: <100MB
- [ ] Idle CPU: <2%

### Documentation

- [ ] `proposal.md` complete
- [ ] `design.md` complete
- [ ] `tasks.md` complete (this file)
- [ ] README for compositor module
- [ ] User guide

---

## Work Stream Integration

### Work Items

Add to `WORK_STREAM.md`:

```
## ACTIVE

### research-tui-compositor
- Status: IN_PROGRESS
- Priority: P1
- Owner: [agent-id]
- Depends on: -
- Blocking: -
- Progress:
  - [x] Proposal written
  - [x] Design written
  - [ ] Phase 1 (foundation) complete
  - [ ] Phase 2 (compositor) complete
  - [ ] Phase 3 (advanced) complete
  - [ ] Quality gates passed
  - [ ] Merged to main
```

### Related Tasks

- **research-tui-compositor**: This implementation
- **research-sitback-ui**: Use compositor for Sitback dashboard
- **research-unified-system-app**: Integrate compositor into unified app

---

## Success Criteria (Final)

1. ✅ App starts in <500ms
2. ✅ Menubar with File/Edit/View/Tools/Help menus functional
3. ✅ Statusbar displays session name, agent status, real-time clock
4. ✅ Can split panes horizontally and vertically; focus switching works
5. ✅ Terminal panes execute shell commands and display output
6. ✅ Keyboard shortcuts work (Ctrl+N, Ctrl+V, Ctrl+X, Ctrl+L)
7. ✅ Layouts can be saved to and restored from YAML
8. ✅ Session state persists across app restart
9. ✅ All linters pass; no new lint suppressions
10. ✅ Test coverage ≥80% for compositor core logic

---

## References

- **Proposal**: [./proposal.md](./proposal.md)
- **Design**: [./design.md](./design.md)
- **Research**: [../../research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md](../../research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md) § 2
- **Textual Docs**: https://textual.textualize.io/
- **Related Plan**: [../../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md](../../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md)

---
