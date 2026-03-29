// Auto-generated TypeScript declarations for selector
// Source: generate-api-docs.py

export declare class ObjectiveSelector {
  constructor(weights: any);
  select(models: Array<Record<(str, Any)>>, profile: any): void;
  select_best_model(candidate_ids: Array<string>): void;
}

export declare class ObjectiveWeights {
  validate(): void;
}

export declare function get_objective_profile(profile_name: string): void;
export declare function score_model(m: any): void;
export declare function select(models: Array<Record<(str, Any)>>, profile: any): void;
export declare function select_best_model(candidate_ids: Array<string>): void;
export declare function validate(): void;
