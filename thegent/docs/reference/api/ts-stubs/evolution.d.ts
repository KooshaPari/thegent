// Auto-generated TypeScript declarations for evolution
// Source: generate-api-docs.py

export declare class PlanEvolver {
  constructor(current_dag: any);
  evolve_dag(discovery_events: Array<Record<(str, Any)>>): void;
  sandbox_evolution(proposed_changes: Array<string>): void;
}

export declare function evolve_dag(discovery_events: Array<Record<(str, Any)>>): void;
export declare function sandbox_evolution(proposed_changes: Array<string>): void;
