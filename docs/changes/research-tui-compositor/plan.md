# Plan: research-tui-compositor

## Objective

Build a terminal user interface compositor for Thegent that renders structured agent orchestration state, supports composable panels, and exposes an interactive control surface for operators.

## Approach

1. Survey existing TUI frameworks (Textual, blessed, urwid) for composability and terminal compatibility
2. Define the compositor's panel contract and event model for agent state updates
3. Prototype the layout engine with resizable panes and scrollback buffers
4. Implement agent session visualization (task queues, status, logs) as reference panels
5. Validate on macOS Terminal, iTerm2, and common Linux terminals
