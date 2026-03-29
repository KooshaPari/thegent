// Auto-generated usage examples for budget_alerts
// Source: generate-api-docs.py

import { BudgetAlertSystem, BudgetConfig, check_budget, from_settings, get_daily_spend, get_hourly_spend } from "./budget_alerts";

// Create a BudgetAlertSystem instance
const budgetalertsystem = new BudgetAlertSystem(undefined as unknown as any, undefined as unknown as any);
budgetalertsystem.check_budget(0, "example_context");
budgetalertsystem.from_settings(undefined as unknown as any);
budgetalertsystem.get_daily_spend();
budgetalertsystem.get_hourly_spend();

// Create a BudgetConfig instance
const budgetconfig = new BudgetConfig();

// Call check_budget
check_budget(undefined as unknown as any, 0, "example_context");
// Call from_settings
from_settings(undefined as unknown as any, undefined as unknown as any);
// Call get_daily_spend
get_daily_spend(undefined as unknown as any);
// Call get_hourly_spend
get_hourly_spend(undefined as unknown as any);
