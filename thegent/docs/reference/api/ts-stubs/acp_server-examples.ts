// Auto-generated usage examples for acp_server
// Source: generate-api-docs.py

import { ACPServerAdapter, AgentSession, SessionEndpoints, add_message, attach, build_starlette_app, cli, get_or_resolve_backend, inspect, main, run_http, send, stop } from "./acp_server";

// Create a ACPServerAdapter instance
const acpserveradapter = new ACPServerAdapter(undefined as unknown as any);
acpserveradapter.build_starlette_app();
acpserveradapter.run_http("example_host", 0);

// Create a AgentSession instance
const agentsession = new AgentSession("example_session_id", undefined as unknown as AgentRunner, undefined as unknown as any);
agentsession.add_message("example_role", "example_content");
agentsession.stop();

// Create a SessionEndpoints instance
const sessionendpoints = new SessionEndpoints(undefined as unknown as any);
sessionendpoints.attach("example_session_name");
sessionendpoints.get_or_resolve_backend();
sessionendpoints.inspect("example_session_id", 0);
sessionendpoints.send("example_session_id", "example_text");

// Call add_message
add_message(undefined as unknown as any, "example_role", "example_content");
// Call attach
attach(undefined as unknown as any, "example_session_name");
// Call build_starlette_app
build_starlette_app(undefined as unknown as any);
// Call cli
cli(false, "example_host", 0, "example_log_level");
// Call get_or_resolve_backend
get_or_resolve_backend(undefined as unknown as any);
// Call inspect
inspect(undefined as unknown as any, "example_session_id", 0);
// Call main
main();
// Call run_http
run_http(undefined as unknown as any, "example_host", 0);
// Call send
send(undefined as unknown as any, "example_session_id", "example_text");
// Call stop
stop(undefined as unknown as any);
