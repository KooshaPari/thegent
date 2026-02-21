// Auto-generated TypeScript declarations for cache_v2
// Source: generate-api-docs.py

export declare class CacheInvalidator {
  constructor(cache: any);
  stop(): void;
  watch(directory: string): void;
}

export declare class CacheV2 {
  constructor(root: string, namespace: string);
}

export declare class CrossProcessSingleflight {
  constructor(coordination_dir: string);
  do(key: string, func: Callable<(Any, Any)>, ttl: number): void;
}

export declare class Handler extends watchdog.events.FileSystemEventHandler {
  constructor(cache: any);
  on_modified(event: any): void;
}

export declare class HeatBasedLRU {
  constructor(capacity: number, decay_factor: number);
  get(key: string): void;
  put(key: string, value: any): void;
}

export declare class Singleflight {
  constructor();
  do(key: string, func: Callable<(Any, Any)>): void;
}

export declare function do(key: string, func: Callable<(Any, Any)>, ttl: number): void;
export declare function get(key: string): any;
export declare function on_modified(event: any): void;
export declare function put(key: string, value: any): void;
export declare function stop(): void;
export declare function watch(directory: string): void;
