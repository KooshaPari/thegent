// Auto-generated usage examples for task_queue
// Source: generate-api-docs.py

import { MaildirQueue, ack, dequeue, enqueue, list_pending, nack } from "./task_queue";

// Create a MaildirQueue instance
const maildirqueue = new MaildirQueue("example_path");
maildirqueue.ack("example_task_id");
maildirqueue.dequeue();
maildirqueue.enqueue(undefined as unknown as Record<(str, Any)>, 0);
maildirqueue.list_pending();
maildirqueue.nack("example_task_id");

// Call ack
ack(undefined as unknown as any, "example_task_id");
// Call dequeue
dequeue(undefined as unknown as any);
// Call enqueue
enqueue(undefined as unknown as any, undefined as unknown as Record<(str, Any)>, 0);
// Call list_pending
list_pending(undefined as unknown as any);
// Call nack
nack(undefined as unknown as any, "example_task_id");
