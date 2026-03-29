// Auto-generated usage examples for metrics
// Source: generate-api-docs.py

import { AggregatedMetrics, MetricsCollector, ProviderMetricsSnapshot, clear_all, get_all_metrics, get_metrics, get_metrics_collector, get_query_latency_ms, initialize_metrics_collector, latency_mean, latency_p99, load_from_file, record, reliability, reset_provider, save_to_file } from "./metrics";

// Create a AggregatedMetrics instance
const aggregatedmetrics = new AggregatedMetrics();
aggregatedmetrics.latency_mean();
aggregatedmetrics.latency_p99();
aggregatedmetrics.reliability();

// Create a MetricsCollector instance
const metricscollector = new MetricsCollector(undefined as unknown as any);
metricscollector.clear_all();
metricscollector.get_all_metrics();
metricscollector.get_metrics("example_provider_id");
metricscollector.get_query_latency_ms();
metricscollector.load_from_file("example_filepath");
metricscollector.record(undefined as unknown as ProviderMetricsSnapshot);
metricscollector.reset_provider("example_provider_id");
metricscollector.save_to_file("example_provider_id");

// Create a ProviderMetricsSnapshot instance
const providermetricssnapshot = new ProviderMetricsSnapshot();

// Call clear_all
clear_all(undefined as unknown as any);
// Call get_all_metrics
get_all_metrics(undefined as unknown as any);
// Call get_metrics
get_metrics(undefined as unknown as any, "example_provider_id");
// Call get_metrics_collector
get_metrics_collector();
// Call get_query_latency_ms
get_query_latency_ms(undefined as unknown as any);
// Call initialize_metrics_collector
initialize_metrics_collector(undefined as unknown as any);
// Call latency_mean
latency_mean(undefined as unknown as any);
// Call latency_p99
latency_p99(undefined as unknown as any);
// Call load_from_file
load_from_file(undefined as unknown as any, "example_filepath");
// Call record
record(undefined as unknown as any, undefined as unknown as ProviderMetricsSnapshot);
// Call reliability
reliability(undefined as unknown as any);
// Call reset_provider
reset_provider(undefined as unknown as any, "example_provider_id");
// Call save_to_file
save_to_file(undefined as unknown as any, "example_provider_id");
