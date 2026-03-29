// Auto-generated usage examples for queue
// Source: generate-api-docs.py

import { TaskQueue, complete, dequeue, enqueue } from "./queue";

// Create a TaskQueue instance
const taskqueue = new TaskQueue();
taskqueue.complete("example_task_id");
taskqueue.dequeue();
taskqueue.enqueue("example_task_id", undefined as unknown as Record<(str, Any)>);

// Call complete
complete(undefined as unknown as any, "example_task_id");
// Call dequeue
dequeue(undefined as unknown as any);
// Call enqueue
enqueue(undefined as unknown as any, "example_task_id", undefined as unknown as Record<(str, Any)>);
