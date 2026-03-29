// Auto-generated usage examples for aggregators
// Source: generate-api-docs.py

import { BudgetAlert, CostCap, CostTracker, check, get_session_cost, is_within_budget, record_cost, set_budget, should_alert, start_session } from "./aggregators";

// Create a BudgetAlert instance
const budgetalert = new BudgetAlert(0);
budgetalert.set_budget(0);
budgetalert.should_alert(0);

// Create a CostCap instance
const costcap = new CostCap(0);
costcap.check(0);

// Create a CostTracker instance
const costtracker = new CostTracker();
costtracker.get_session_cost("example_session_id");
costtracker.is_within_budget("example_session_id", 0);
costtracker.record_cost("example_session_id", 0);
costtracker.start_session("example_session_id");

// Call check
check(undefined as unknown as any, 0);
// Call get_session_cost
get_session_cost(undefined as unknown as any, "example_session_id");
// Call is_within_budget
is_within_budget(undefined as unknown as any, "example_session_id", 0);
// Call record_cost
record_cost(undefined as unknown as any, "example_session_id", 0);
// Call set_budget
set_budget(undefined as unknown as any, 0);
// Call should_alert
should_alert(undefined as unknown as any, 0);
// Call start_session
start_session(undefined as unknown as any, "example_session_id");
