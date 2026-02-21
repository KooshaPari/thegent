// Auto-generated usage examples for keepalive
// Source: generate-api-docs.py

import { KeepaliveConfig, TerminalKeepalive, keepalive, start, stop } from "./keepalive";

// Create a KeepaliveConfig instance
const keepaliveconfig = new KeepaliveConfig();

// Create a TerminalKeepalive instance
const terminalkeepalive = new TerminalKeepalive(undefined as unknown as any);
terminalkeepalive.start();
terminalkeepalive.stop();

// Call keepalive
keepalive(0, "example_message");
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
