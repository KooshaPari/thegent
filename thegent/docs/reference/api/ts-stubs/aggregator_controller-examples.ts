// Auto-generated usage examples for aggregator_controller
// Source: generate-api-docs.py

import { BudgetTier, CostController, UsageSnapshot, can_spawn, get_tier, get_today_usage, record_call, utilization_pct } from "./aggregator_controller";

// Create a BudgetTier instance
const budgettier = new BudgetTier();

// Create a CostController instance
const costcontroller = new CostController("example_session_dir", undefined as unknown as any);
costcontroller.can_spawn();
costcontroller.get_tier();
costcontroller.get_today_usage();
costcontroller.record_call("example_dimension", "example_agent");

// Create a UsageSnapshot instance
const usagesnapshot = new UsageSnapshot();
usagesnapshot.utilization_pct();

// Call can_spawn
can_spawn(undefined as unknown as any);
// Call get_tier
get_tier(undefined as unknown as any);
// Call get_today_usage
get_today_usage(undefined as unknown as any);
// Call record_call
record_call(undefined as unknown as any, "example_dimension", "example_agent");
// Call utilization_pct
utilization_pct(undefined as unknown as any);
