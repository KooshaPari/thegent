// Auto-generated usage examples for observability
// Source: generate-api-docs.py

import { MeshLogger, MetricsAggregator, get_summary, log, mesh_status_cmd, record_metric } from "./observability";

// Create a MeshLogger instance
const meshlogger = new MeshLogger("example_mesh_root");
meshlogger.log("example_agent_id", "example_event", undefined as unknown as any);

// Create a MetricsAggregator instance
const metricsaggregator = new MetricsAggregator("example_mesh_root");
metricsaggregator.get_summary();
metricsaggregator.record_metric("example_agent_id", "example_name", 0);

// Call get_summary
get_summary(undefined as unknown as any);
// Call log
log(undefined as unknown as any, "example_agent_id", "example_event", undefined as unknown as any);
// Call mesh_status_cmd
mesh_status_cmd("example_mesh_root");
// Call record_metric
record_metric(undefined as unknown as any, "example_agent_id", "example_name", 0);
