// Auto-generated usage examples for pane_manager
// Source: generate-api-docs.py

import { PaneManager, PaneNode, close_pane, create_root_pane, focus_next, restore_layout, save_layout, split_pane } from "./pane_manager";

// Create a PaneManager instance
const panemanager = new PaneManager();
panemanager.close_pane();
panemanager.create_root_pane("example_pane_id");
panemanager.focus_next();
panemanager.restore_layout(undefined as unknown as Record<string, unknown>);
panemanager.save_layout();
panemanager.split_pane("example_direction");

// Create a PaneNode instance
const panenode = new PaneNode();

// Call close_pane
close_pane(undefined as unknown as any);
// Call create_root_pane
create_root_pane(undefined as unknown as any, "example_pane_id");
// Call focus_next
focus_next(undefined as unknown as any);
// Call restore_layout
restore_layout(undefined as unknown as any, undefined as unknown as Record<string, unknown>);
// Call save_layout
save_layout(undefined as unknown as any);
// Call split_pane
split_pane(undefined as unknown as any, "example_direction");
