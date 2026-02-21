// Auto-generated usage examples for control_vectors
// Source: generate-api-docs.py

import { ControlVectorManager, analyze_and_inject, prepare_environment } from "./control_vectors";

// Create a ControlVectorManager instance
const controlvectormanager = new ControlVectorManager("example_agent_id");
controlvectormanager.analyze_and_inject("example_prompt", undefined as unknown as Record<(str, Any)>);
controlvectormanager.prepare_environment("example_workspace_path");

// Call analyze_and_inject
analyze_and_inject(undefined as unknown as any, "example_prompt", undefined as unknown as Record<(str, Any)>);
// Call prepare_environment
prepare_environment(undefined as unknown as any, "example_workspace_path");
