// Auto-generated usage examples for task
// Source: generate-api-docs.py

import { Task, TaskStatus, add_dependency, is_ready, mark_completed, mark_failed, mark_running, remove_dependency } from "./task";

// Create a Task instance
const task = new Task();
task.add_dependency("example_task_id");
task.is_ready(undefined as unknown as set<string>);
task.mark_completed(undefined as unknown as any);
task.mark_failed("example_error");
task.mark_running();
task.remove_dependency("example_task_id");

// Create a TaskStatus instance
const taskstatus = new TaskStatus();

// Call add_dependency
add_dependency(undefined as unknown as any, "example_task_id");
// Call is_ready
is_ready(undefined as unknown as any, undefined as unknown as set<string>);
// Call mark_completed
mark_completed(undefined as unknown as any, undefined as unknown as any);
// Call mark_failed
mark_failed(undefined as unknown as any, "example_error");
// Call mark_running
mark_running(undefined as unknown as any);
// Call remove_dependency
remove_dependency(undefined as unknown as any, "example_task_id");
