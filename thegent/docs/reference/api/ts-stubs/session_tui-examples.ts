// Auto-generated usage examples for session_tui
// Source: generate-api-docs.py

import { SessionTUI, manage_session, render_session_view, render_sessions_list, show, watch } from "./session_tui";

// Create a SessionTUI instance
const sessiontui = new SessionTUI(undefined as unknown as any);
sessiontui.manage_session("example_session_id", "example_action");
sessiontui.render_session_view("example_session_id");
sessiontui.render_sessions_list();
sessiontui.show(undefined as unknown as any);
sessiontui.watch(undefined as unknown as any, 0);

// Call manage_session
manage_session(undefined as unknown as any, "example_session_id", "example_action");
// Call render_session_view
render_session_view(undefined as unknown as any, "example_session_id");
// Call render_sessions_list
render_sessions_list(undefined as unknown as any);
// Call show
show(undefined as unknown as any, undefined as unknown as any);
// Call watch
watch(undefined as unknown as any, undefined as unknown as any, 0);
