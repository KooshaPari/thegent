// Auto-generated usage examples for cost_controller
// Source: generate-api-docs.py

import { BudgetTier, CostController, DailyUsage, calls_remaining, can_spawn, get_tier, get_today_usage, record_call, usage_path } from "./cost_controller";

// Create a BudgetTier instance
const budgettier = new BudgetTier();

// Create a CostController instance
const costcontroller = new CostController("example_session_dir", "example_health_targets_path");
costcontroller.calls_remaining();
costcontroller.can_spawn(0);
costcontroller.get_tier();
costcontroller.get_today_usage();
costcontroller.record_call("example_dimension", "example_agent");
costcontroller.usage_path();

// Create a DailyUsage instance
const dailyusage = new DailyUsage();

// Call calls_remaining
calls_remaining(undefined as unknown as any);
// Call can_spawn
can_spawn(undefined as unknown as any, 0);
// Call get_tier
get_tier(undefined as unknown as any);
// Call get_today_usage
get_today_usage(undefined as unknown as any);
// Call record_call
record_call(undefined as unknown as any, "example_dimension", "example_agent");
// Call usage_path
usage_path(undefined as unknown as any);
