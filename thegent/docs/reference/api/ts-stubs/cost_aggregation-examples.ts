// Auto-generated usage examples for cost_aggregation
// Source: generate-api-docs.py

import { CostAggregator, get_cost_by_model, get_total_cost, record_run_cost } from "./cost_aggregation";

// Create a CostAggregator instance
const costaggregator = new CostAggregator();
costaggregator.get_cost_by_model();
costaggregator.get_total_cost();
costaggregator.record_run_cost("example_run_id", 0, "example_model", undefined as unknown as Record<(str, int)>);

// Call get_cost_by_model
get_cost_by_model(undefined as unknown as any);
// Call get_total_cost
get_total_cost(undefined as unknown as any);
// Call record_run_cost
record_run_cost(undefined as unknown as any, "example_run_id", 0, "example_model", undefined as unknown as Record<(str, int)>);
