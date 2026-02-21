// Auto-generated usage examples for priority_queue
// Source: generate-api-docs.py

import { QueuedRun, RunPriorityQueue, cancel, drain, empty, from_lane, full, get, get_nowait, make_priority_queue, peek, put, put_nowait, qsize } from "./priority_queue";

// Create a QueuedRun instance
const queuedrun = new QueuedRun();
queuedrun.from_lane("example_run_id", "example_lane_name", undefined as unknown as any);

// Create a RunPriorityQueue instance
const runpriorityqueue = new RunPriorityQueue();
runpriorityqueue.cancel("example_run_id");
runpriorityqueue.drain();
runpriorityqueue.empty();
runpriorityqueue.full();
runpriorityqueue.get(false, undefined as unknown as any);
runpriorityqueue.get_nowait();
runpriorityqueue.peek();
runpriorityqueue.put(undefined as unknown as QueuedRun, false, undefined as unknown as any);
runpriorityqueue.put_nowait(undefined as unknown as QueuedRun);
runpriorityqueue.qsize();

// Call cancel
cancel(undefined as unknown as any, "example_run_id");
// Call drain
drain(undefined as unknown as any);
// Call empty
empty(undefined as unknown as any);
// Call from_lane
from_lane(undefined as unknown as any, "example_run_id", "example_lane_name", undefined as unknown as any);
// Call full
full(undefined as unknown as any);
// Call get
get(undefined as unknown as any, false, undefined as unknown as any);
// Call get_nowait
get_nowait(undefined as unknown as any);
// Call make_priority_queue
make_priority_queue(0);
// Call peek
peek(undefined as unknown as any);
// Call put
put(undefined as unknown as any, undefined as unknown as QueuedRun, false, undefined as unknown as any);
// Call put_nowait
put_nowait(undefined as unknown as any, undefined as unknown as QueuedRun);
// Call qsize
qsize(undefined as unknown as any);
