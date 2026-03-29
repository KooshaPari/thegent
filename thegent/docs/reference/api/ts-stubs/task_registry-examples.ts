// Auto-generated usage examples for task_registry
// Source: generate-api-docs.py

import { AsyncTaskRegistry, _TaskEntry, cancel, cleanup, create, get_task_registry, list_tasks, status, update_progress } from "./task_registry";

// Create a AsyncTaskRegistry instance
const asynctaskregistry = new AsyncTaskRegistry();
asynctaskregistry.cancel("example_task_id");
asynctaskregistry.cleanup(0);
asynctaskregistry.create(undefined as unknown as asyncio.Task<any>, undefined as unknown as any);
asynctaskregistry.list_tasks();
asynctaskregistry.status("example_task_id");
asynctaskregistry.update_progress("example_task_id", 0, undefined as unknown as any, "example_message");

// Create a _TaskEntry instance
const _taskentry = new _TaskEntry("example_task_id", undefined as unknown as asyncio.Task<any>);

// Call cancel
cancel(undefined as unknown as any, "example_task_id");
// Call cleanup
cleanup(undefined as unknown as any, 0);
// Call create
create(undefined as unknown as any, undefined as unknown as asyncio.Task<any>, undefined as unknown as any);
// Call get_task_registry
get_task_registry();
// Call list_tasks
list_tasks(undefined as unknown as any);
// Call status
status(undefined as unknown as any, "example_task_id");
// Call update_progress
update_progress(undefined as unknown as any, "example_task_id", 0, undefined as unknown as any, "example_message");
