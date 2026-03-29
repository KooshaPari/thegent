// Auto-generated TypeScript declarations for multi_level
// Source: generate-api-docs.py

export declare class MultiLevelCache {
  constructor(l1_maxsize: number, l1_ttl: number, l2_dir: any, l2_ttl: number);
  clear(): void;
  close(): void;
  delete(key: any): void;
  get(key: any): void;
  l2_available(): void;
  l2_dir(): void;
  set(key: any, value: any, ttl: any): void;
  stats(): void;
}

export declare function cached_multi(cache: MultiLevelCache): void;
export declare function clear(): void;
export declare function close(): void;
export declare function decorator(func: any): void;
export declare function delete(key: any): void;
export declare function get(key: any): void;
export declare function l2_available(): void;
export declare function l2_dir(): void;
export declare function set(key: any, value: any, ttl: any): void;
export declare function stats(): void;
export declare function wrapper(): void;
