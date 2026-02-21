// Auto-generated TypeScript declarations for refactoring
// Source: generate-api-docs.py

export declare class CognitiveRefactorer {
  constructor(agent_id: string);
  analyze_reasoning_efficiency(run_history: Array<Record<(str, Any)>>): void;
  apply_refactor(refactor_plan: string): void;
  propose_refactor(efficiency_report: Record<(str, float)>): void;
}

export declare function analyze_reasoning_efficiency(run_history: Array<Record<(str, Any)>>): void;
export declare function apply_refactor(refactor_plan: string): void;
export declare function propose_refactor(efficiency_report: Record<(str, float)>): void;
