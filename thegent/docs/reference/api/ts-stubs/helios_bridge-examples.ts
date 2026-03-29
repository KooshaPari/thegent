// Auto-generated usage examples for helios_bridge
// Source: generate-api-docs.py

import { HeliosShieldBridge, connect, send_command, test_connection } from "./helios_bridge";

// Create a HeliosShieldBridge instance
const heliosshieldbridge = new HeliosShieldBridge();
heliosshieldbridge.connect();
heliosshieldbridge.send_command("example_command");
heliosshieldbridge.test_connection();

// Call connect
connect(undefined as unknown as any);
// Call send_command
send_command(undefined as unknown as any, "example_command");
// Call test_connection
test_connection(undefined as unknown as any);
