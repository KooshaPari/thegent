// Auto-generated TypeScript declarations for handoff
// Source: generate-api-docs.py

export declare class HandoffIntegrity {
  constructor(workspace_root: string);
  analyze_prompt(prompt: string): void;
  suggest_improvements(prompt: string, analysis: any): void;
  validate_handoff(prompt: string, min_completeness_score: number): void;
}

export declare function analyze_prompt(prompt: string): void;
export declare function suggest_improvements(prompt: string, analysis: any): void;
export declare function validate_handoff(prompt: string, min_completeness_score: number): void;
