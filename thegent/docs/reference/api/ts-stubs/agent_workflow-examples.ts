// Auto-generated usage examples for agent_workflow
// Source: generate-api-docs.py

import { AgentWorkflow, create_docgen_workflow, execute, register_step } from "./agent_workflow";

// Create a AgentWorkflow instance
const agentworkflow = new AgentWorkflow();
agentworkflow.create_docgen_workflow();
agentworkflow.execute(undefined as unknown as Record<(str, Any)>);
agentworkflow.register_step("example_name", undefined as unknown as callable, undefined as unknown as any);

// Call create_docgen_workflow
create_docgen_workflow(undefined as unknown as any);
// Call execute
execute(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call register_step
register_step(undefined as unknown as any, "example_name", undefined as unknown as callable, undefined as unknown as any);
