// Auto-generated usage examples for plan
// Source: generate-api-docs.py

import { milestone_create, milestone_list, plan_add, plan_analyze, plan_checkpoint, plan_claim, plan_complete, plan_incorporate, plan_next, plan_progress, plan_remove, plan_roadmap, plan_rollback, plan_status, plan_work_stream, sprint_create, sprint_list } from "./plan";

// Call milestone_create
milestone_create(undefined as unknown as Annotated<(str, Any)>, undefined as unknown as Annotated<(Any, Any)>);
// Call milestone_list
milestone_list(undefined as unknown as Annotated<(bool, Any)>);
// Call plan_add
plan_add("example_task_id", "example_agent", "example_prompt", undefined as unknown as any);
// Call plan_analyze
plan_analyze(undefined as unknown as any, "example_format");
// Call plan_checkpoint
plan_checkpoint("example_reason");
// Call plan_claim
plan_claim("example_item_id", undefined as unknown as any, undefined as unknown as any);
// Call plan_complete
plan_complete("example_item_id", undefined as unknown as any, undefined as unknown as any);
// Call plan_incorporate
plan_incorporate(false);
// Call plan_next
plan_next("example_format");
// Call plan_progress
plan_progress(0, "example_format");
// Call plan_remove
plan_remove("example_task_id");
// Call plan_roadmap
plan_roadmap("example_format");
// Call plan_rollback
plan_rollback("example_checkpoint_id");
// Call plan_status
plan_status("example_format");
// Call plan_work_stream
plan_work_stream(0, "example_format", undefined as unknown as any);
// Call sprint_create
sprint_create(undefined as unknown as Annotated<(str, Any)>, undefined as unknown as Annotated<(Any, Any)>);
// Call sprint_list
sprint_list(undefined as unknown as Annotated<(bool, Any)>);
