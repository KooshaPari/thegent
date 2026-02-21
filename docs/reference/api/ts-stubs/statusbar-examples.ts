// Auto-generated usage examples for statusbar
// Source: generate-api-docs.py

import { StatusItem, StatusbarWidget, add_item, clear_items, compose, on_mount, remove_item, set_status, watch_agent_name, watch_agent_status, watch_cwd, watch_session_id } from "./statusbar";

// Create a StatusItem instance
const statusitem = new StatusItem("example_label", "example_value", false, "example_color");

// Create a StatusbarWidget instance
const statusbarwidget = new StatusbarWidget();
statusbarwidget.add_item(undefined as unknown as StatusItem);
statusbarwidget.clear_items();
statusbarwidget.compose();
statusbarwidget.on_mount();
statusbarwidget.remove_item("example_label");
statusbarwidget.set_status("example_status", "example_message");
statusbarwidget.watch_agent_name(undefined as unknown as any);
statusbarwidget.watch_agent_status("example_value");
statusbarwidget.watch_cwd("example_value");
statusbarwidget.watch_session_id(undefined as unknown as any);

// Call add_item
add_item(undefined as unknown as any, undefined as unknown as StatusItem);
// Call clear_items
clear_items(undefined as unknown as any);
// Call compose
compose(undefined as unknown as any);
// Call on_mount
on_mount(undefined as unknown as any);
// Call remove_item
remove_item(undefined as unknown as any, "example_label");
// Call set_status
set_status(undefined as unknown as any, "example_status", "example_message");
// Call watch_agent_name
watch_agent_name(undefined as unknown as any, undefined as unknown as any);
// Call watch_agent_status
watch_agent_status(undefined as unknown as any, "example_value");
// Call watch_cwd
watch_cwd(undefined as unknown as any, "example_value");
// Call watch_session_id
watch_session_id(undefined as unknown as any, undefined as unknown as any);
