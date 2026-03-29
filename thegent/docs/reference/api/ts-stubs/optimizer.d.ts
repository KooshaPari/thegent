// Auto-generated TypeScript declarations for optimizer
// Source: generate-api-docs.py

export declare class PromptOptimizer {
  constructor(agent_id: string, registry: any);
  get_best_prompt(): void;
  optimize(current_prompt: string, feedback: any): void;
  record_run(version_id: string, result: RunResult, tokens: number, cost: number): void;
}

export declare class PromptVersion {
}

export declare function get_best_prompt(): void;
export declare function optimize(current_prompt: string, feedback: any): void;
export declare function record_run(version_id: string, result: RunResult, tokens: number, cost: number): void;
