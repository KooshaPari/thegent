// Auto-generated TypeScript declarations for fork_guard
// Source: generate-api-docs.py

export declare class ForkContext {
}

export declare class ForkExplosionGuard {
  constructor();
  get_stats(run_id: string): void;
  register_run(run_id: string, parent_id: any): void;
}

export declare function get_stats(run_id: string): void;
export declare function register_run(run_id: string, parent_id: any): void;
