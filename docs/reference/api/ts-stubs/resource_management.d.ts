// Auto-generated TypeScript declarations for resource_management
// Source: generate-api-docs.py

export declare class BottleneckDetector {
  constructor();
  detect_resource_contention(snapshot: ExtendedResourceSnapshot, harness_cards: Record<(str, HarnessCard)>): void;
  identify_slow_points(): void;
  record_loop_timing(loop_id: string, duration_ms: number): void;
}

export declare class ExtendedResourceSnapshot {
}

export declare class HarnessCard {
  estimate_resources(session_count: number, isolated: boolean, use_peak: boolean, use_p95: boolean): void;
}

export declare class LeakMetrics {
}

export declare class ResourceDistribution {
  compute_stats(values: Array<number>): void;
  update(value: number): void;
}

export declare class ResourcePredictionEngine {
  constructor(history_file: any);
  detect_anomalies(current: ExtendedResourceSnapshot): void;
  predict_next_interval(interval_seconds: number): void;
  record(snapshot: ExtendedResourceSnapshot): void;
  should_throttle_speculative(new_branches: number, min_mem_available_mb: number): void;
}

export declare function compute_stats(values: Array<number>): void;
export declare function create_harness_cards(): void;
export declare function detect_anomalies(current: ExtendedResourceSnapshot): void;
export declare function detect_leaks(history: deque<ExtendedResourceSnapshot>, current: ExtendedResourceSnapshot, window_hours: number): void;
export declare function detect_resource_contention(snapshot: ExtendedResourceSnapshot, harness_cards: Record<(str, HarnessCard)>): void;
export declare function estimate_resources(session_count: number, isolated: boolean, use_peak: boolean, use_p95: boolean): void;
export declare function identify_slow_points(): void;
export declare function predict_next_interval(interval_seconds: number): void;
export declare function record(snapshot: ExtendedResourceSnapshot): void;
export declare function record_loop_timing(loop_id: string, duration_ms: number): void;
export declare function sample_extended_resources(): void;
export declare function should_throttle_speculative(new_branches: number, min_mem_available_mb: number): void;
export declare function update(value: number): void;
