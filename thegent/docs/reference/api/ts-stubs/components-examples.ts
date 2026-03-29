// Auto-generated usage examples for components
// Source: generate-api-docs.py

import { FooterStatusBar, HeaderWidget, MetricsPanel, OutputWidget, ProgressIndicator, SidebarWidget, StatusWidget, add_agent, clear, compose, get_line_count, render, start_timer, stop_timer, update_agent_status, update_metric, update_metrics, update_pane_info, update_progress, update_session_info, update_status, watch_elapsed_time, watch_model, watch_status, watch_tokens_used, write } from "./components";

// Create a FooterStatusBar instance
const footerstatusbar = new FooterStatusBar();
footerstatusbar.render();
footerstatusbar.update_pane_info(0, "example_focus_id");

// Create a HeaderWidget instance
const headerwidget = new HeaderWidget("example_title", "example_version");
headerwidget.render();

// Create a MetricsPanel instance
const metricspanel = new MetricsPanel();
metricspanel.compose();
metricspanel.update_metric("example_key", "example_value");
metricspanel.update_metrics(undefined as unknown as Record<(str, str)>);

// Create a OutputWidget instance
const outputwidget = new OutputWidget("example_title");
outputwidget.clear();
outputwidget.compose();
outputwidget.get_line_count();
outputwidget.write("example_text", "example_style", false);

// Create a ProgressIndicator instance
const progressindicator = new ProgressIndicator();
progressindicator.render();
progressindicator.update_progress(0, 0, undefined as unknown as any);

// Create a SidebarWidget instance
const sidebarwidget = new SidebarWidget();
sidebarwidget.add_agent("example_agent_id", "example_name", "example_status");
sidebarwidget.compose();
sidebarwidget.update_agent_status("example_agent_id", "example_status");
sidebarwidget.update_session_info("example_session_id", "example_start_time", "example_uptime");

// Create a StatusWidget instance
const statuswidget = new StatusWidget();
statuswidget.compose();
statuswidget.start_timer();
statuswidget.stop_timer();
statuswidget.update_status("example_status", undefined as unknown as any, undefined as unknown as any);
statuswidget.watch_elapsed_time(0);
statuswidget.watch_model("example_model");
statuswidget.watch_status("example_status");
statuswidget.watch_tokens_used(0);

// Call add_agent
add_agent(undefined as unknown as any, "example_agent_id", "example_name", "example_status");
// Call clear
clear(undefined as unknown as any);
// Call compose
compose(undefined as unknown as any);
// Call get_line_count
get_line_count(undefined as unknown as any);
// Call render
render(undefined as unknown as any);
// Call start_timer
start_timer(undefined as unknown as any);
// Call stop_timer
stop_timer(undefined as unknown as any);
// Call update_agent_status
update_agent_status(undefined as unknown as any, "example_agent_id", "example_status");
// Call update_metric
update_metric(undefined as unknown as any, "example_key", "example_value");
// Call update_metrics
update_metrics(undefined as unknown as any, undefined as unknown as Record<(str, str)>);
// Call update_pane_info
update_pane_info(undefined as unknown as any, 0, "example_focus_id");
// Call update_progress
update_progress(undefined as unknown as any, 0, 0, undefined as unknown as any);
// Call update_session_info
update_session_info(undefined as unknown as any, "example_session_id", "example_start_time", "example_uptime");
// Call update_status
update_status(undefined as unknown as any, "example_status", undefined as unknown as any, undefined as unknown as any);
// Call watch_elapsed_time
watch_elapsed_time(undefined as unknown as any, 0);
// Call watch_model
watch_model(undefined as unknown as any, "example_model");
// Call watch_status
watch_status(undefined as unknown as any, "example_status");
// Call watch_tokens_used
watch_tokens_used(undefined as unknown as any, 0);
// Call write
write(undefined as unknown as any, "example_text", "example_style", false);
