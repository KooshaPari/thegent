// Auto-generated usage examples for router
// Source: generate-api-docs.py

import { DependencyRouter, from_tasks, get_ready_tasks, is_finished, mark_completed, mark_started } from "./router";

// Create a DependencyRouter instance
const dependencyrouter = new DependencyRouter(undefined as unknown as Mapping<(str, Iterable<str])>>);
dependencyrouter.from_tasks(undefined as unknown as Array<Record<(str, Any)>>);
dependencyrouter.get_ready_tasks();
dependencyrouter.is_finished();
dependencyrouter.mark_completed("example_task_id");
dependencyrouter.mark_started("example_task_id");

// Call from_tasks
from_tasks(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
// Call get_ready_tasks
get_ready_tasks(undefined as unknown as any);
// Call is_finished
is_finished(undefined as unknown as any);
// Call mark_completed
mark_completed(undefined as unknown as any, "example_task_id");
// Call mark_started
mark_started(undefined as unknown as any, "example_task_id");
