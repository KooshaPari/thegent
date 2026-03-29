// Auto-generated TypeScript declarations for collector
// Source: generate-api-docs.py

export declare class MetricsCollector {
  constructor();
  get_stats(metric_name: string): void;
  record(metric_name: string, value: number): void;
}

export declare function get_stats(metric_name: string): void;
export declare function record(metric_name: string, value: number): void;
