// Auto-generated usage examples for terminal_pane
// Source: generate-api-docs.py

import { TerminalConfig, TerminalManager, TerminalPane, TerminalSize, add_pane, clear, get_active, get_output, get_pane, list_panes, on_resize, set_active } from "./terminal_pane";

// Create a TerminalConfig instance
const terminalconfig = new TerminalConfig();

// Create a TerminalManager instance
const terminalmanager = new TerminalManager();
terminalmanager.add_pane("example_pane_id", undefined as unknown as TerminalPane);
terminalmanager.get_active();
terminalmanager.get_pane("example_pane_id");
terminalmanager.list_panes();
terminalmanager.set_active("example_pane_id");

// Create a TerminalPane instance
const terminalpane = new TerminalPane();
terminalpane.clear();
terminalpane.get_output();
terminalpane.on_resize(undefined as unknown as Resize);

// Create a TerminalSize instance
const terminalsize = new TerminalSize();

// Call add_pane
add_pane(undefined as unknown as any, "example_pane_id", undefined as unknown as TerminalPane);
// Call clear
clear(undefined as unknown as any);
// Call get_active
get_active(undefined as unknown as any);
// Call get_output
get_output(undefined as unknown as any);
// Call get_pane
get_pane(undefined as unknown as any, "example_pane_id");
// Call list_panes
list_panes(undefined as unknown as any);
// Call on_resize
on_resize(undefined as unknown as any, undefined as unknown as Resize);
// Call set_active
set_active(undefined as unknown as any, "example_pane_id");
