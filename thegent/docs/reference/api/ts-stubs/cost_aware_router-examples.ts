// Auto-generated usage examples for cost_aware_router
// Source: generate-api-docs.py

import { Budget, BudgetAwareRouter, BudgetExceededError, BudgetManager, BudgetStatus, BudgetType, CostAwareRouter, CostBudget, CostMeter, SimpleCostTracker, _SimpleCandidate, add_budget, check_budget, daily_total, get_project_cost, record, record_spend, remaining, reset_session, route, select, session_total, utilization } from "./cost_aware_router";

// Create a Budget instance
const budget = new Budget();
budget.remaining();
budget.utilization();

// Create a BudgetAwareRouter instance
const budgetawarerouter = new BudgetAwareRouter(undefined as unknown as BudgetManager, undefined as unknown as any, 0, 0);
budgetawarerouter.route("example_project_id", undefined as unknown as Array<RouteCandidate>, "example_strategy");

// Create a BudgetExceededError instance
const budgetexceedederror = new BudgetExceededError("example_budget_type", 0, 0);

// Create a BudgetManager instance
const budgetmanager = new BudgetManager();
budgetmanager.add_budget(undefined as unknown as Budget);
budgetmanager.check_budget("example_project_id", 0);
budgetmanager.record_spend("example_project_id", 0);

// Create a BudgetStatus instance
const budgetstatus = new BudgetStatus();

// Create a BudgetType instance
const budgettype = new BudgetType();

// Create a CostAwareRouter instance
const costawarerouter = new CostAwareRouter(undefined as unknown as CostBudget, undefined as unknown as SimpleCostTracker);
costawarerouter.select(undefined as unknown as Array<_SimpleCandidate>);

// Create a CostBudget instance
const costbudget = new CostBudget();

// Create a CostMeter instance
const costmeter = new CostMeter();
costmeter.get_project_cost("example_project_id");

// Create a SimpleCostTracker instance
const simplecosttracker = new SimpleCostTracker();
simplecosttracker.daily_total();
simplecosttracker.record(0);
simplecosttracker.reset_session();
simplecosttracker.session_total();

// Create a _SimpleCandidate instance
const _simplecandidate = new _SimpleCandidate();

// Call add_budget
add_budget(undefined as unknown as any, undefined as unknown as Budget);
// Call check_budget
check_budget(undefined as unknown as any, "example_project_id", 0);
// Call daily_total
daily_total(undefined as unknown as any);
// Call get_project_cost
get_project_cost(undefined as unknown as any, "example_project_id");
// Call record
record(undefined as unknown as any, 0);
// Call record_spend
record_spend(undefined as unknown as any, "example_project_id", 0);
// Call remaining
remaining(undefined as unknown as any);
// Call reset_session
reset_session(undefined as unknown as any);
// Call route
route(undefined as unknown as any, "example_project_id", undefined as unknown as Array<RouteCandidate>, "example_strategy");
// Call select
select(undefined as unknown as any, undefined as unknown as Array<_SimpleCandidate>);
// Call session_total
session_total(undefined as unknown as any);
// Call utilization
utilization(undefined as unknown as any);
