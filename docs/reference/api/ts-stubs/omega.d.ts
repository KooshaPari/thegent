// Auto-generated TypeScript declarations for omega
// Source: generate-api-docs.py

export declare class OmegaExecutionResult extends BaseModel {
}

export declare class OmegaLoop {
  constructor(agent_id: string);
  calculate_entropy(plan: Array<Record<(str, Any)>>): void;
  minimize_entropy(cycle_id: string, proposed_plan: Array<Record<(str, Any)>>): void;
}

export declare function calculate_entropy(plan: Array<Record<(str, Any)>>): void;
export declare function minimize_entropy(cycle_id: string, proposed_plan: Array<Record<(str, Any)>>): void;
