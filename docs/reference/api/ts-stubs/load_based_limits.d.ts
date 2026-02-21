// Auto-generated TypeScript declarations for load_based_limits
// Source: generate-api-docs.py

export declare class DeadlineMonitor {
  constructor(interval_s: number);
  active_deadlines(): void;
  is_running(): void;
  register(run_id: string, deadline_ts: number, warn_at_pct: number): void;
  start(): void;
  stop(timeout: number): void;
  unregister(run_id: string): void;
}

export declare class HysteresisController {
  constructor(upper_threshold: any, lower_threshold: any, dwell_time_s: any);
  get_limit(current_limit: number, running_count: number, target_limit: number): void;
}

export declare class LimitGateConfig {
  from_dict(d: any): void;
}

export declare class OwnerStats {
  avg_elapsed_ms(): void;
  to_dict(): void;
}

export declare class ResourceSnapshot {
}

export declare class SoftDeadline {
  elapsed(): void;
  is_overdue(): void;
  is_warn_zone(): void;
  warn_threshold(): void;
}

export declare class UsageTracker {
  constructor();
  get_all_stats(): void;
  get_stats(owner: string): void;
  record_end(owner: string, run_id: string, elapsed_ms: number): void;
  record_start(owner: string, run_id: string): void;
  reset(owner: any): void;
}

export declare function active_deadlines(): void;
export declare function avg_elapsed_ms(): void;
export declare function compute_dynamic_limit(snapshot: ResourceSnapshot, config: any, running_count: number): void;
export declare function elapsed(): void;
export declare function from_dict(d: any): void;
export declare function get_all_stats(): void;
export declare function get_deadline_monitor(): void;
export declare function get_limit(current_limit: number, running_count: number, target_limit: number): void;
export declare function get_stats(owner: string): void;
export declare function get_usage_tracker(): void;
export declare function is_overdue(): void;
export declare function is_running(): void;
export declare function is_warn_zone(): void;
export declare function record_end(owner: string, run_id: string, elapsed_ms: number): void;
export declare function record_start(owner: string, run_id: string): void;
export declare function register(run_id: string, deadline_ts: number, warn_at_pct: number): void;
export declare function reset(owner: any): void;
export declare function sample_resources(): void;
export declare function start(): void;
export declare function stop(timeout: number): void;
export declare function to_dict(): void;
export declare function unregister(run_id: string): void;
export declare function warn_threshold(): void;
