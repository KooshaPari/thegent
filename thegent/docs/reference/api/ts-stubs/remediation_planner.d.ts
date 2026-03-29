// Auto-generated TypeScript declarations for remediation_planner
// Source: generate-api-docs.py

export declare class Finding {
}

export declare class RemediationPlan extends BaseModel {
}

export declare class RemediationPlanner {
  constructor(health_targets_path: string);
  plan(findings: Array<Finding>, budget_remaining_calls: number): void;
}

export declare class RemediationTask extends BaseModel {
}

export declare function plan(findings: Array<Finding>, budget_remaining_calls: number): void;
