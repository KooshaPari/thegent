// Auto-generated usage examples for zmx_backend
// Source: generate-api-docs.py

import { SessionBackend, ZmxBackend, ZmxSession, attach, available, capture, create, kill, list, name, resolve_session_backend } from "./zmx_backend";

// Create a SessionBackend instance
const sessionbackend = new SessionBackend();
sessionbackend.attach("example_session_name");
sessionbackend.available();
sessionbackend.capture("example_session_name", 0);
sessionbackend.create("example_session_name", undefined as unknown as Array<string>);
sessionbackend.kill("example_session_name");
sessionbackend.list();
sessionbackend.name();

// Create a ZmxBackend instance
const zmxbackend = new ZmxBackend("example_zmx_bin");
zmxbackend.attach("example_session_name");
zmxbackend.available();
zmxbackend.capture("example_session_name", 0);
zmxbackend.create("example_session_name", undefined as unknown as Array<string>);
zmxbackend.kill("example_session_name");
zmxbackend.list();
zmxbackend.name();

// Create a ZmxSession instance
const zmxsession = new ZmxSession();

// Call attach
attach(undefined as unknown as any, "example_session_name");
// Call available
available(undefined as unknown as any);
// Call capture
capture(undefined as unknown as any, "example_session_name", 0);
// Call create
create(undefined as unknown as any, "example_session_name", undefined as unknown as Array<string>);
// Call kill
kill(undefined as unknown as any, "example_session_name");
// Call list
list(undefined as unknown as any);
// Call name
name(undefined as unknown as any);
// Call resolve_session_backend
resolve_session_backend(undefined as unknown as any);
