// Auto-generated usage examples for collector
// Source: generate-api-docs.py

import { MetricsCollector, get_stats, record } from "./collector";

// Create a MetricsCollector instance
const metricscollector = new MetricsCollector();
metricscollector.get_stats("example_metric_name");
metricscollector.record("example_metric_name", 0);

// Call get_stats
get_stats(undefined as unknown as any, "example_metric_name");
// Call record
record(undefined as unknown as any, "example_metric_name", 0);
