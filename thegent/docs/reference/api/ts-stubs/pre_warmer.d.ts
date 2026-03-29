// Auto-generated TypeScript declarations for pre_warmer
// Source: generate-api-docs.py

export declare class CachePreWarmer {
  constructor(cache: MultiLevelCache);
  get_stats(): void;
  is_running(): void;
  register_strategy(strategy: WarmingStrategy): void;
  start_background(): void;
  stop_background(timeout: number): void;
  unregister_strategy(name: string): void;
  warm_all(): void;
  warm_key(key: string, load_fn: Callable<(Any, Any)>): void;
}

export declare class WarmingStrategy {
}

export declare class _StrategyState {
}

export declare function get_stats(): void;
export declare function is_running(): void;
export declare function model_list_strategy(load_fn: Callable<(Any, Any)>, model_keys: any, schedule_seconds: number): void;
export declare function register_strategy(strategy: WarmingStrategy): void;
export declare function session_list_strategy(load_fn: Callable<(Any, Any)>, session_keys: any, schedule_seconds: number): void;
export declare function start_background(): void;
export declare function stop_background(timeout: number): void;
export declare function unregister_strategy(name: string): void;
export declare function warm_all(): void;
export declare function warm_key(key: string, load_fn: Callable<(Any, Any)>): void;
