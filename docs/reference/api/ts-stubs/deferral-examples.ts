// Auto-generated usage examples for deferral
// Source: generate-api-docs.py

import { DeferralManager, DeferralRule, defer_task, list_deferred, should_defer } from "./deferral";

// Create a DeferralManager instance
const deferralmanager = new DeferralManager(undefined as unknown as ThegentSettings);
deferralmanager.defer_task("example_task_id", "example_reason");
deferralmanager.list_deferred();
deferralmanager.should_defer("example_task_priority", 0);

// Create a DeferralRule instance
const deferralrule = new DeferralRule("example_id", "example_condition", "example_action");

// Call defer_task
defer_task(undefined as unknown as any, "example_task_id", "example_reason");
// Call list_deferred
list_deferred(undefined as unknown as any);
// Call should_defer
should_defer(undefined as unknown as any, "example_task_priority", 0);
