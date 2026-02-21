// Auto-generated usage examples for workflow
// Source: generate-api-docs.py

import { CrewStage, WorkflowEngine, add_stage, execute, execute_stage, resolve_stage_dependencies } from "./workflow";

// Create a CrewStage instance
const crewstage = new CrewStage();

// Create a WorkflowEngine instance
const workflowengine = new WorkflowEngine();
workflowengine.add_stage(undefined as unknown as CrewStage);
workflowengine.execute();
workflowengine.execute_stage(undefined as unknown as CrewStage);
workflowengine.resolve_stage_dependencies();

// Call add_stage
add_stage(undefined as unknown as any, undefined as unknown as CrewStage);
// Call execute
execute(undefined as unknown as any);
// Call execute_stage
execute_stage(undefined as unknown as any, undefined as unknown as CrewStage);
// Call resolve_stage_dependencies
resolve_stage_dependencies(undefined as unknown as any);
