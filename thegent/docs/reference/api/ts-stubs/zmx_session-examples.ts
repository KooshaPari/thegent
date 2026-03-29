// Auto-generated usage examples for zmx_session
// Source: generate-api-docs.py

import { ZmxSessionConfig, ZmxSessionManager, attach_session, capture_output, create_session, destroy_session, from_env, from_settings, is_available, list_sessions, make_zmx_session_manager, send_input } from "./zmx_session";

// Create a ZmxSessionConfig instance
const zmxsessionconfig = new ZmxSessionConfig();
zmxsessionconfig.from_env();
zmxsessionconfig.from_settings();

// Create a ZmxSessionManager instance
const zmxsessionmanager = new ZmxSessionManager(undefined as unknown as any);
zmxsessionmanager.attach_session("example_session_name");
zmxsessionmanager.capture_output("example_session_name", 0);
zmxsessionmanager.create_session("example_session_id", undefined as unknown as Array<string>);
zmxsessionmanager.destroy_session("example_session_name");
zmxsessionmanager.is_available();
zmxsessionmanager.list_sessions();
zmxsessionmanager.send_input("example_session_name", "example_text");

// Call attach_session
attach_session(undefined as unknown as any, "example_session_name");
// Call capture_output
capture_output(undefined as unknown as any, "example_session_name", 0);
// Call create_session
create_session(undefined as unknown as any, "example_session_id", undefined as unknown as Array<string>);
// Call destroy_session
destroy_session(undefined as unknown as any, "example_session_name");
// Call from_env
from_env(undefined as unknown as any);
// Call from_settings
from_settings(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
// Call list_sessions
list_sessions(undefined as unknown as any);
// Call make_zmx_session_manager
make_zmx_session_manager(undefined as unknown as any);
// Call send_input
send_input(undefined as unknown as any, "example_session_name", "example_text");
