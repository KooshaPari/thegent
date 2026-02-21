// Auto-generated usage examples for agileplus
// Source: generate-api-docs.py

import { AgilePlusLoop, CycleResult, CycleState, cycle_id, get_status, request_shutdown, run_continuous, run_once, shutdown_requested, state } from "./agileplus";

// Create a AgilePlusLoop instance
const agileplusloop = new AgilePlusLoop("example_project_dir", "example_health_targets_path", 0, 0, 0, "example_lifecycle_mode");
agileplusloop.cycle_id();
agileplusloop.get_status();
agileplusloop.request_shutdown();
agileplusloop.run_continuous(0, undefined as unknown as any);
agileplusloop.run_once(false);
agileplusloop.shutdown_requested();
agileplusloop.state();

// Create a CycleResult instance
const cycleresult = new CycleResult();

// Create a CycleState instance
const cyclestate = new CycleState();

// Call cycle_id
cycle_id(undefined as unknown as any);
// Call get_status
get_status(undefined as unknown as any);
// Call request_shutdown
request_shutdown(undefined as unknown as any);
// Call run_continuous
run_continuous(undefined as unknown as any, 0, undefined as unknown as any);
// Call run_once
run_once(undefined as unknown as any, false);
// Call shutdown_requested
shutdown_requested(undefined as unknown as any);
// Call state
state(undefined as unknown as any);
