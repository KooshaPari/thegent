// Auto-generated TypeScript declarations for shm_manager
// Source: generate-api-docs.py

export declare class SHMManager {
  constructor(shm_path: any);
  award_xp(amount: number): void;
  get_health_score(): void;
  get_provider_metrics(provider: string): void;
  get_router_metrics(): void;
  get_xp_state(): void;
  record_failure(target: string, category: number): void;
  record_resource_usage(pid: number, cpu_percent: number, memory_kb: number): void;
  set_health_score(score: number): void;
  update_provider_metrics(provider: string, request_count: number, success_count: number, latency_ms: number): void;
  update_router_metrics(lifecycle_inc: number, thegent_inc: number, changes_inc: number, hysteresis_inc: number): void;
}

export declare function award_xp(amount: number): void;
export declare function get_health_score(): number;
export declare function get_provider_metrics(provider: string): any;
export declare function get_router_metrics(): any;
export declare function get_xp_state(): any;
export declare function record_failure(target: string, category: number): void;
export declare function record_resource_usage(pid: number, cpu_percent: number, memory_kb: number): void;
export declare function set_health_score(score: number): void;
export declare function update_provider_metrics(provider: string, request_count: number, success_count: number, latency_ms: number): void;
export declare function update_router_metrics(lifecycle_inc: number, thegent_inc: number, changes_inc: number, hysteresis_inc: number): void;
