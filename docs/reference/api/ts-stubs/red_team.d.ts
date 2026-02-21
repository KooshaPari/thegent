// Auto-generated TypeScript declarations for red_team
// Source: generate-api-docs.py

export declare class RedTeamAgent {
  constructor(target_registry: any);
  evaluate_resilience(scenario: RedTeamScenario, outcome: Record<(str, Any)>): void;
  generate_attack(target_agent: string): void;
}

export declare class RedTeamScenario extends BaseModel {
}

export declare function evaluate_resilience(scenario: RedTeamScenario, outcome: Record<(str, Any)>): void;
export declare function generate_attack(target_agent: string): void;
