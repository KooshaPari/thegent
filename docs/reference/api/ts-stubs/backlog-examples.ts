// Auto-generated usage examples for backlog
// Source: generate-api-docs.py

import { BacklogItem, BacklogManager, BacklogStatus, add, backlog_path, defer, get_all, get_pending, increment_attempt, resolve, update_status } from "./backlog";

// Create a BacklogItem instance
const backlogitem = new BacklogItem();

// Create a BacklogManager instance
const backlogmanager = new BacklogManager("example_session_dir");
backlogmanager.add("example_finding_id", "example_dimension", 0, "example_description");
backlogmanager.backlog_path();
backlogmanager.defer("example_item_id", "example_reason");
backlogmanager.get_all();
backlogmanager.get_pending();
backlogmanager.increment_attempt("example_item_id");
backlogmanager.resolve("example_item_id");
backlogmanager.update_status("example_item_id", undefined as unknown as BacklogStatus, undefined as unknown as any);

// Create a BacklogStatus instance
const backlogstatus = new BacklogStatus();

// Call add
add(undefined as unknown as any, "example_finding_id", "example_dimension", 0, "example_description");
// Call backlog_path
backlog_path(undefined as unknown as any);
// Call defer
defer(undefined as unknown as any, "example_item_id", "example_reason");
// Call get_all
get_all(undefined as unknown as any);
// Call get_pending
get_pending(undefined as unknown as any);
// Call increment_attempt
increment_attempt(undefined as unknown as any, "example_item_id");
// Call resolve
resolve(undefined as unknown as any, "example_item_id");
// Call update_status
update_status(undefined as unknown as any, "example_item_id", undefined as unknown as BacklogStatus, undefined as unknown as any);
