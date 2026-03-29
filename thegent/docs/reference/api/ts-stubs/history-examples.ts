// Auto-generated usage examples for history
// Source: generate-api-docs.py

import { ContextHistory, HistoryEntry, get_task_sequence, record, search } from "./history";

// Create a ContextHistory instance
const contexthistory = new ContextHistory(undefined as unknown as any);
contexthistory.get_task_sequence("example_task_id");
contexthistory.record(undefined as unknown as HistoryEntry);
contexthistory.search(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, 0);

// Create a HistoryEntry instance
const historyentry = new HistoryEntry();

// Call get_task_sequence
get_task_sequence(undefined as unknown as any, "example_task_id");
// Call record
record(undefined as unknown as any, undefined as unknown as HistoryEntry);
// Call search
search(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, 0);
