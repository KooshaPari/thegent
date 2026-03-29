// Auto-generated usage examples for tracker
// Source: generate-api-docs.py

import { CostEntry, RunCostTracker, end_run, get_run_cost_tracker, record_entry, start_run, to_dict } from "./tracker";

// Create a CostEntry instance
const costentry = new CostEntry();
costentry.to_dict();

// Create a RunCostTracker instance
const runcosttracker = new RunCostTracker(undefined as unknown as any);
runcosttracker.end_run();
runcosttracker.record_entry(undefined as unknown as CostEntry);
runcosttracker.start_run("example_run_id");

// Call end_run
end_run(undefined as unknown as any);
// Call get_run_cost_tracker
get_run_cost_tracker();
// Call record_entry
record_entry(undefined as unknown as any, undefined as unknown as CostEntry);
// Call start_run
start_run(undefined as unknown as any, "example_run_id");
// Call to_dict
to_dict(undefined as unknown as any);
