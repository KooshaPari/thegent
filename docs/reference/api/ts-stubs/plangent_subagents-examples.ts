// Auto-generated usage examples for plangent_subagents
// Source: generate-api-docs.py

import { PlangentSubagents, execute, register_subagent } from "./plangent_subagents";

// Create a PlangentSubagents instance
const plangentsubagents = new PlangentSubagents();
plangentsubagents.execute("example_subagent_name", undefined as unknown as Record<(str, Any)>);
plangentsubagents.register_subagent("example_name", undefined as unknown as any);

// Call execute
execute(undefined as unknown as any, "example_subagent_name", undefined as unknown as Record<(str, Any)>);
// Call register_subagent
register_subagent(undefined as unknown as any, "example_name", undefined as unknown as any);
