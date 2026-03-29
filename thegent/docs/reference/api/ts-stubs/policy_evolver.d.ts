// Auto-generated TypeScript declarations for policy_evolver
// Source: generate-api-docs.py

export declare class PolicyEvolver {
  constructor(session_dir: string, settings: any);
  evolve(lookback_runs: number): void;
}

export declare function evolve(lookback_runs: number): void;
