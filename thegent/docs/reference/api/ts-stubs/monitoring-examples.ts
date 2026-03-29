// Auto-generated usage examples for monitoring
// Source: generate-api-docs.py

import { CostMetrics, HealthStatus, MonitoringEngine, PerformanceMetrics, check_health, get_summary, record_execution, track_costs, track_performance } from "./monitoring";

// Create a CostMetrics instance
const costmetrics = new CostMetrics();

// Create a HealthStatus instance
const healthstatus = new HealthStatus();

// Create a MonitoringEngine instance
const monitoringengine = new MonitoringEngine();
monitoringengine.check_health(undefined as unknown as Crew);
monitoringengine.get_summary("example_crew_id");
monitoringengine.record_execution("example_crew_id", undefined as unknown as Record<(str, ExecutionResult)>, undefined as unknown as any);
monitoringengine.track_costs("example_crew_id", undefined as unknown as Record<(str, ExecutionResult)>);
monitoringengine.track_performance("example_crew_id", undefined as unknown as Record<(str, ExecutionResult)>);

// Create a PerformanceMetrics instance
const performancemetrics = new PerformanceMetrics();

// Call check_health
check_health(undefined as unknown as any, undefined as unknown as Crew);
// Call get_summary
get_summary(undefined as unknown as any, "example_crew_id");
// Call record_execution
record_execution(undefined as unknown as any, "example_crew_id", undefined as unknown as Record<(str, ExecutionResult)>, undefined as unknown as any);
// Call track_costs
track_costs(undefined as unknown as any, "example_crew_id", undefined as unknown as Record<(str, ExecutionResult)>);
// Call track_performance
track_performance(undefined as unknown as any, "example_crew_id", undefined as unknown as Record<(str, ExecutionResult)>);
