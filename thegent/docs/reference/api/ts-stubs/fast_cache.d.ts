// Auto-generated TypeScript declarations for fast_cache
// Source: generate-api-docs.py

export declare class MultiTierCache {
  constructor(l1_size: number, l2_size: number, l3_path: any, default_ttl: any);
  clear(): void;
  delete(key: string): void;
  enable_invalidation(directory: any): void;
  get(key: string): void;
  get_with_fetch(key: string, fetch_func: any, ttl: any): void;
  set(key: string, value: any, ttl: any): void;
  stats(): void;
}

export declare function clear(): void;
export declare function delete(key: string): void;
export declare function enable_invalidation(directory: any): void;
export declare function get(key: string): void;
export declare function get_cache(l1_size: number, l2_size: number, l3_path: any, default_ttl: any): void;
export declare function get_with_fetch(key: string, fetch_func: any, ttl: any): void;
export declare function set(key: string, value: any, ttl: any): void;
export declare function stats(): void;
