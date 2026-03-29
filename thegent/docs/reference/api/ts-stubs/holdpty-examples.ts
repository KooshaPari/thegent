// Auto-generated usage examples for holdpty
// Source: generate-api-docs.py

import { PTYHolder, start, stop, wrap_with_holdpty } from "./holdpty";

// Create a PTYHolder instance
const ptyholder = new PTYHolder("example_socket_path", undefined as unknown as Array<string>, undefined as unknown as any, undefined as unknown as any);
ptyholder.start();
ptyholder.stop();

// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
// Call wrap_with_holdpty
wrap_with_holdpty(undefined as unknown as Array<string>, "example_session_id", "example_socket_path");
