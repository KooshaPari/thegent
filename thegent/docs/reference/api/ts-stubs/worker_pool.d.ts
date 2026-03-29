// Auto-generated TypeScript declarations for worker_pool
// Source: generate-api-docs.py

export declare class PersistentWorkerPool {
  constructor(size: any);
  get_instance(size: any): void;
  start(): void;
  stop(): void;
}

export declare function get_instance(size: any): PersistentWorkerPool;
export declare function get_worker_pool(): void;
export declare function start(): void;
export declare function stop(): void;
