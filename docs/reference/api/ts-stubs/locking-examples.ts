// Auto-generated usage examples for locking
// Source: generate-api-docs.py

import { QueueLock, read_entries, write_entries } from "./locking";

// Create a QueueLock instance
const queuelock = new QueueLock("example_queue_path");
queuelock.read_entries();
queuelock.write_entries(undefined as unknown as Array<Record<string, unknown>>);

// Call read_entries
read_entries(undefined as unknown as any);
// Call write_entries
write_entries(undefined as unknown as any, undefined as unknown as Array<Record<string, unknown>>);
