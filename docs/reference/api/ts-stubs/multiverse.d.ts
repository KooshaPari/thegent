// Auto-generated TypeScript declarations for multiverse
// Source: generate-api-docs.py

export declare class TimelineFork {
}

export declare class multiverseSimulator {
  constructor(current_plan: any);
  create_fork(divergence_wp: string, proposed_delta: string): void;
  merge_timeline(fork_id: string): void;
  simulate_impact(fork_id: string): void;
}

export declare function create_fork(divergence_wp: string, proposed_delta: string): void;
export declare function merge_timeline(fork_id: string): void;
export declare function simulate_impact(fork_id: string): void;
