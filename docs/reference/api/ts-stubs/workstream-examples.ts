// Auto-generated usage examples for workstream
// Source: generate-api-docs.py

import { WorkItem, claim_item, mark_completed, parse_workstream } from "./workstream";

// Create a WorkItem instance
const workitem = new WorkItem();

// Call claim_item
claim_item("example_path", "example_item_id", "example_owner");
// Call mark_completed
mark_completed("example_path", "example_item_id");
// Call parse_workstream
parse_workstream("example_path");
