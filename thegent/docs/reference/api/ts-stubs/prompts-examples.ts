// Auto-generated usage examples for prompts
// Source: generate-api-docs.py

import { PromptOrchestrator, decompose, route_subtasks } from "./prompts";

// Create a PromptOrchestrator instance
const promptorchestrator = new PromptOrchestrator(undefined as unknown as ThegentSettings);
promptorchestrator.decompose("example_goal");
promptorchestrator.route_subtasks(undefined as unknown as Array<Record<(str, Any)>>);

// Call decompose
decompose(undefined as unknown as any, "example_goal");
// Call route_subtasks
route_subtasks(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
