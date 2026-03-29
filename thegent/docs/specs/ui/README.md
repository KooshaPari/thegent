# UI & TUI Domain Technical Specification

## Overview

Terminal and graphical user interfaces.

## Components

### TUI (Terminal UI)

| Component | Purpose | Files |
|-----------|---------|-------|
| Compositor | Layout | `tui/compositor.py` |
| Pane manager | Windows | `tui/pane_manager.py` |
| Session | State | `tui/session.py` |
| Themes | Styling | `tui/themes.py` |

### Widgets

| Widget | Purpose |
|--------|---------|
| Table | Data display |
| Timeline | History |
| StatusBar | Info |
| MenuBar | Navigation |
| TerminalPane | PTY |

### UI (Graphical)

| Component | Purpose |
|-----------|---------|
| Compositor | Layout |
| Components | Reusable |
| Textual | App framework |

## Performance

| Metric | Target |
|--------|--------|
| Render | <16ms (60fps) |
| Input | <10ms |
| Resize | <50ms |
