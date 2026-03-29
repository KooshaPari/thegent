// Auto-generated usage examples for terminal
// Source: generate-api-docs.py

import { TmuxPane, capture_tmux_pane, heliosShield_status, is_claude_code_pane, list_tmux_panes, send_to_tmux_pane } from "./terminal";

// Create a TmuxPane instance
const tmuxpane = new TmuxPane();

// Call capture_tmux_pane
capture_tmux_pane("example_pane_id", 0);
// Call heliosShield_status
heliosShield_status();
// Call is_claude_code_pane
is_claude_code_pane(undefined as unknown as TmuxPane);
// Call list_tmux_panes
list_tmux_panes();
// Call send_to_tmux_pane
send_to_tmux_pane("example_pane_id", "example_text", false);
