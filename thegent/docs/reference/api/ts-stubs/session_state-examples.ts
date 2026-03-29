// Auto-generated usage examples for session_state
// Source: generate-api-docs.py

import { SessionState, delete, list_sessions, load, save } from "./session_state";

// Create a SessionState instance
const sessionstate = new SessionState("example_session_id", undefined as unknown as any);
sessionstate.delete();
sessionstate.list_sessions();
sessionstate.load();
sessionstate.save(undefined as unknown as Record<string, unknown>);

// Call delete
delete(undefined as unknown as any);
// Call list_sessions
list_sessions(undefined as unknown as any);
// Call load
load(undefined as unknown as any);
// Call save
save(undefined as unknown as any, undefined as unknown as Record<string, unknown>);
