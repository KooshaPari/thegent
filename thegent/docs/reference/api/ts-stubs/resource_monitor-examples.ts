// Auto-generated usage examples for resource_monitor
// Source: generate-api-docs.py

import { ResourceMonitor, ResourceStats, detect_leak, get_history, get_process_info, get_resource_monitor, get_stats, get_suspicion_level, is_critical, start, stop } from "./resource_monitor";

// Create a ResourceMonitor instance
const resourcemonitor = new ResourceMonitor(0);
resourcemonitor.detect_leak();
resourcemonitor.get_history();
resourcemonitor.get_process_info(0);
resourcemonitor.get_stats();
resourcemonitor.start();
resourcemonitor.stop();

// Create a ResourceStats instance
const resourcestats = new ResourceStats();
resourcestats.get_suspicion_level();
resourcestats.is_critical();

// Call detect_leak
detect_leak(undefined as unknown as any);
// Call get_history
get_history(undefined as unknown as any);
// Call get_process_info
get_process_info(undefined as unknown as any, 0);
// Call get_resource_monitor
get_resource_monitor();
// Call get_stats
get_stats(undefined as unknown as any);
// Call get_suspicion_level
get_suspicion_level(undefined as unknown as any);
// Call is_critical
is_critical(undefined as unknown as any);
// Call start
start(undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
