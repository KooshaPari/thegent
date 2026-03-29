// Auto-generated usage examples for app
// Source: generate-api-docs.py

import { CompositApp, ErrorBoundary, Statusbar, action_close_pane, action_focus_next, action_new_pane, action_quit, action_retry_pane, action_split_horizontal, action_split_vertical, compose, on_mount, on_panel_mounted, on_panel_unmounted, on_unmount, render } from "./app";

// Create a CompositApp instance
const compositapp = new CompositApp(undefined as unknown as SessionState | None);
compositapp.action_close_pane();
compositapp.action_focus_next();
compositapp.action_new_pane();
compositapp.action_quit();
compositapp.action_retry_pane();
compositapp.action_split_horizontal();
compositapp.action_split_vertical();
compositapp.compose();
compositapp.on_mount();
compositapp.on_panel_mounted(undefined as unknown as PanelMounted);
compositapp.on_panel_unmounted(undefined as unknown as PanelUnmounted);
compositapp.on_unmount();

// Create a ErrorBoundary instance
const errorboundary = new ErrorBoundary("example_error_message", "example_error_type", "example_stack_trace", "example_pane_id");
errorboundary.render();

// Create a Statusbar instance
const statusbar = new Statusbar();
statusbar.render();

// Call action_close_pane
action_close_pane(undefined as unknown as any);
// Call action_focus_next
action_focus_next(undefined as unknown as any);
// Call action_new_pane
action_new_pane(undefined as unknown as any);
// Call action_quit
action_quit(undefined as unknown as any);
// Call action_retry_pane
action_retry_pane(undefined as unknown as any);
// Call action_split_horizontal
action_split_horizontal(undefined as unknown as any);
// Call action_split_vertical
action_split_vertical(undefined as unknown as any);
// Call compose
compose(undefined as unknown as any);
// Call on_mount
on_mount(undefined as unknown as any);
// Call on_panel_mounted
on_panel_mounted(undefined as unknown as any, undefined as unknown as PanelMounted);
// Call on_panel_unmounted
on_panel_unmounted(undefined as unknown as any, undefined as unknown as PanelUnmounted);
// Call on_unmount
on_unmount(undefined as unknown as any);
// Call render
render(undefined as unknown as any);
