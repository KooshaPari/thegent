// Auto-generated usage examples for task_router
// Source: generate-api-docs.py

import { ConstraintValidator, TaskClassifier, TaskRouter, classify, detect_role, find_active_terminal_for_path, get_fallback_chain, route, route_by_capability, route_dag_tasks, shape_task, should_delegate_to_reviewer, validate } from "./task_router";

// Create a ConstraintValidator instance
const constraintvalidator = new ConstraintValidator(undefined as unknown as ThegentSettings);
constraintvalidator.validate(undefined as unknown as TaskMetadata, undefined as unknown as RunRegistry | None, undefined as unknown as any);

// Create a TaskClassifier instance
const taskclassifier = new TaskClassifier(undefined as unknown as ThegentSettings);
taskclassifier.classify("example_prompt", undefined as unknown as any);
taskclassifier.detect_role("example_prompt", undefined as unknown as any);

// Create a TaskRouter instance
const taskrouter = new TaskRouter(undefined as unknown as ThegentSettings);
taskrouter.classify("example_prompt");
taskrouter.find_active_terminal_for_path("example_path");
taskrouter.get_fallback_chain(undefined as unknown as TaskCategory);
taskrouter.route("example_prompt", undefined as unknown as RunRegistry | None, undefined as unknown as any);
taskrouter.route_by_capability("example_task_type");
taskrouter.route_dag_tasks(undefined as unknown as any);
taskrouter.shape_task("example_prompt", undefined as unknown as TaskCategory);
taskrouter.should_delegate_to_reviewer(0);
taskrouter.validate(undefined as unknown as TaskMetadata, undefined as unknown as RunRegistry | None, undefined as unknown as any);

// Call classify
classify(undefined as unknown as any, "example_prompt");
// Call detect_role
detect_role(undefined as unknown as any, "example_prompt", undefined as unknown as any);
// Call find_active_terminal_for_path
find_active_terminal_for_path(undefined as unknown as any, "example_path");
// Call get_fallback_chain
get_fallback_chain(undefined as unknown as any, undefined as unknown as TaskCategory);
// Call route
route(undefined as unknown as any, "example_prompt", undefined as unknown as RunRegistry | None, undefined as unknown as any);
// Call route_by_capability
route_by_capability(undefined as unknown as any, "example_task_type");
// Call route_dag_tasks
route_dag_tasks(undefined as unknown as any, undefined as unknown as any);
// Call shape_task
shape_task(undefined as unknown as any, "example_prompt", undefined as unknown as TaskCategory);
// Call should_delegate_to_reviewer
should_delegate_to_reviewer(undefined as unknown as any, 0);
// Call validate
validate(undefined as unknown as any, undefined as unknown as TaskMetadata, undefined as unknown as RunRegistry | None, undefined as unknown as any);
