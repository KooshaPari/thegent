// Auto-generated usage examples for headless_manager
// Source: generate-api-docs.py

import { HeadlessLSPManager, HeadlessLSPServer, ensure_server, is_running, list_servers, start, stop, stop_all, stop_server } from "./headless_manager";

// Create a HeadlessLSPManager instance
const headlesslspmanager = new HeadlessLSPManager(undefined as unknown as any);
headlesslspmanager.ensure_server("example_language", undefined as unknown as any);
headlesslspmanager.list_servers();
headlesslspmanager.stop_all();
headlesslspmanager.stop_server("example_language");

// Create a HeadlessLSPServer instance
const headlesslspserver = new HeadlessLSPServer("example_language", undefined as unknown as Record<(str, Any)>);
headlesslspserver.is_running();
headlesslspserver.start();
headlesslspserver.stop();

// Call ensure_server
ensure_server(undefined as unknown as any, "example_language", undefined as unknown as any);
// Call is_running
is_running(undefined as unknown as any);
// Call list_servers
list_servers(undefined as unknown as any);
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
// Call stop_all
stop_all(undefined as unknown as any);
// Call stop_server
stop_server(undefined as unknown as any, "example_language");
