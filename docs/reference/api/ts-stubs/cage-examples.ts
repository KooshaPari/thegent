// Auto-generated usage examples for cage
// Source: generate-api-docs.py

import { AgentCage, cleanup, run_command, setup } from "./cage";

// Create a AgentCage instance
const agentcage = new AgentCage("example_cage_id", "example_base_dir");
agentcage.cleanup();
agentcage.run_command(undefined as unknown as Array<string>);
agentcage.setup(undefined as unknown as Array<string>);

// Call cleanup
cleanup(undefined as unknown as any);
// Call run_command
run_command(undefined as unknown as any, undefined as unknown as Array<string>);
// Call setup
setup(undefined as unknown as any, undefined as unknown as Array<string>);
