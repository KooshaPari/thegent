// Auto-generated TypeScript declarations for redis_concurrency
// Source: generate-api-docs.py

export declare class RedisConcurrencyController {
  constructor(redis_config: any, max_concurrent: any, slot_ttl_s: number);
  get_active_count(): void;
  is_available(): void;
  list_active(): void;
}

export declare class RedisConfig {
  from_env(): void;
  from_settings(): void;
}

export declare class _InMemoryStore {
  count_with_prefix_sync(prefix: string): void;
}

export declare function count_with_prefix_sync(prefix: string): void;
export declare function from_env(): void;
export declare function from_settings(): void;
export declare function get_active_count(): void;
export declare function is_available(): void;
export declare function list_active(): void;
export declare function make_redis_concurrency_controller(max_concurrent: any, slot_ttl_s: number): void;
