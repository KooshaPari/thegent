// Auto-generated TypeScript declarations for cache
// Source: generate-api-docs.py

export declare class ResourceCache {
  constructor(cache_dir: string, ttl_seconds: number, max_memory_items: number);
  clear(): void;
  enable_invalidation(directory: string): void;
  get(key: string): void;
  set(key: string, payload: any): void;
}

export declare function clear(): void;
export declare function enable_invalidation(directory: string): void;
export declare function get(key: string): any;
export declare function set(key: string, payload: any): string;
