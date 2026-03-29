// Auto-generated usage examples for sandboxing
// Source: generate-api-docs.py

import { AutonomyEnforcer, SandboxProvider, classify_operation, wrap_command } from "./sandboxing";

// Create a AutonomyEnforcer instance
const autonomyenforcer = new AutonomyEnforcer();
autonomyenforcer.classify_operation("example_command", "example_target");

// Create a SandboxProvider instance
const sandboxprovider = new SandboxProvider();
sandboxprovider.wrap_command(undefined as unknown as Array<string>, 0);

// Call classify_operation
classify_operation(undefined as unknown as any, "example_command", "example_target");
// Call wrap_command
wrap_command(undefined as unknown as any, undefined as unknown as Array<string>, 0);
