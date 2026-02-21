// Auto-generated usage examples for cost_tracker
// Source: generate-api-docs.py

import { CostEntry, CostTracker, RoutingStats, clear, daily_budget, get_budget_burn_ratio, get_budget_remaining, get_cost_tracker, get_daily_spend, get_stats, is_over_budget, log_path, reset_cost_tracker, to_json, track } from "./cost_tracker";

// Create a CostEntry instance
const costentry = new CostEntry();
costentry.to_json();

// Create a CostTracker instance
const costtracker = new CostTracker(undefined as unknown as any, undefined as unknown as any);
costtracker.clear();
costtracker.daily_budget();
costtracker.get_budget_burn_ratio();
costtracker.get_budget_remaining();
costtracker.get_daily_spend();
costtracker.get_stats();
costtracker.is_over_budget();
costtracker.log_path();
costtracker.track("example_provider", "example_model", undefined as unknown as Record<(str, int)>, 0, 0, undefined as unknown as any, false, false);

// Create a RoutingStats instance
const routingstats = new RoutingStats();

// Call clear
clear(undefined as unknown as any);
// Call daily_budget
daily_budget(undefined as unknown as any);
// Call get_budget_burn_ratio
get_budget_burn_ratio(undefined as unknown as any);
// Call get_budget_remaining
get_budget_remaining(undefined as unknown as any);
// Call get_cost_tracker
get_cost_tracker();
// Call get_daily_spend
get_daily_spend(undefined as unknown as any);
// Call get_stats
get_stats(undefined as unknown as any);
// Call is_over_budget
is_over_budget(undefined as unknown as any);
// Call log_path
log_path(undefined as unknown as any);
// Call reset_cost_tracker
reset_cost_tracker();
// Call to_json
to_json(undefined as unknown as any);
// Call track
track(undefined as unknown as any, "example_provider", "example_model", undefined as unknown as Record<(str, int)>, 0, 0, undefined as unknown as any, false, false);
