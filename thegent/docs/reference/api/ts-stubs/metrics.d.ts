// Auto-generated TypeScript declarations for metrics
// Source: generate-api-docs.py

export declare class AggregatedMetrics {
  latency_mean(): void;
  latency_p99(): void;
  reliability(): void;
}

export declare class MetricsCollector {
  constructor(storage_dir: any);
  clear_all(): void;
  get_all_metrics(): void;
  get_metrics(provider_id: string): void;
  get_query_latency_ms(): void;
  load_from_file(filepath: string): void;
  record(snapshot: ProviderMetricsSnapshot): void;
  reset_provider(provider_id: string): void;
  save_to_file(provider_id: string): void;
}

export declare class ProviderMetricsSnapshot {
}

export declare function clear_all(): void;
export declare function get_all_metrics(): void;
export declare function get_metrics(provider_id: string): void;
export declare function get_metrics_collector(): void;
export declare function get_query_latency_ms(): void;
export declare function initialize_metrics_collector(storage_dir: any): void;
export declare function latency_mean(): void;
export declare function latency_p99(): void;
export declare function load_from_file(filepath: string): void;
export declare function record(snapshot: ProviderMetricsSnapshot): void;
export declare function reliability(): void;
export declare function reset_provider(provider_id: string): void;
export declare function save_to_file(provider_id: string): void;
