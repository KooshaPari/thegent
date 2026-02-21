// Auto-generated usage examples for load_based_limits
// Source: generate-api-docs.py

import { DeadlineMonitor, HysteresisController, LimitGateConfig, OwnerStats, ResourceSnapshot, SoftDeadline, UsageTracker, active_deadlines, avg_elapsed_ms, compute_dynamic_limit, elapsed, from_dict, get_all_stats, get_deadline_monitor, get_limit, get_stats, get_usage_tracker, is_overdue, is_running, is_warn_zone, record_end, record_start, register, reset, sample_resources, start, stop, to_dict, unregister, warn_threshold } from "./load_based_limits";

// Create a DeadlineMonitor instance
const deadlinemonitor = new DeadlineMonitor(0);
deadlinemonitor.active_deadlines();
deadlinemonitor.is_running();
deadlinemonitor.register("example_run_id", 0, 0);
deadlinemonitor.start();
deadlinemonitor.stop(0);
deadlinemonitor.unregister("example_run_id");

// Create a HysteresisController instance
const hysteresiscontroller = new HysteresisController(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
hysteresiscontroller.get_limit(0, 0, 0);

// Create a LimitGateConfig instance
const limitgateconfig = new LimitGateConfig();
limitgateconfig.from_dict(undefined as unknown as any);

// Create a OwnerStats instance
const ownerstats = new OwnerStats();
ownerstats.avg_elapsed_ms();
ownerstats.to_dict();

// Create a ResourceSnapshot instance
const resourcesnapshot = new ResourceSnapshot();

// Create a SoftDeadline instance
const softdeadline = new SoftDeadline();
softdeadline.elapsed();
softdeadline.is_overdue();
softdeadline.is_warn_zone();
softdeadline.warn_threshold();

// Create a UsageTracker instance
const usagetracker = new UsageTracker();
usagetracker.get_all_stats();
usagetracker.get_stats("example_owner");
usagetracker.record_end("example_owner", "example_run_id", 0);
usagetracker.record_start("example_owner", "example_run_id");
usagetracker.reset(undefined as unknown as any);

// Call active_deadlines
active_deadlines(undefined as unknown as any);
// Call avg_elapsed_ms
avg_elapsed_ms(undefined as unknown as any);
// Call compute_dynamic_limit
compute_dynamic_limit(undefined as unknown as ResourceSnapshot, undefined as unknown as any, 0);
// Call elapsed
elapsed(undefined as unknown as any);
// Call from_dict
from_dict(undefined as unknown as any, undefined as unknown as any);
// Call get_all_stats
get_all_stats(undefined as unknown as any);
// Call get_deadline_monitor
get_deadline_monitor();
// Call get_limit
get_limit(undefined as unknown as any, 0, 0, 0);
// Call get_stats
get_stats(undefined as unknown as any, "example_owner");
// Call get_usage_tracker
get_usage_tracker();
// Call is_overdue
is_overdue(undefined as unknown as any);
// Call is_running
is_running(undefined as unknown as any);
// Call is_warn_zone
is_warn_zone(undefined as unknown as any);
// Call record_end
record_end(undefined as unknown as any, "example_owner", "example_run_id", 0);
// Call record_start
record_start(undefined as unknown as any, "example_owner", "example_run_id");
// Call register
register(undefined as unknown as any, "example_run_id", 0, 0);
// Call reset
reset(undefined as unknown as any, undefined as unknown as any);
// Call sample_resources
sample_resources();
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any, 0);
// Call to_dict
to_dict(undefined as unknown as any);
// Call unregister
unregister(undefined as unknown as any, "example_run_id");
// Call warn_threshold
warn_threshold(undefined as unknown as any);
