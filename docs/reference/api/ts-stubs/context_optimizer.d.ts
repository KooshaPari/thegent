// Auto-generated TypeScript declarations for context_optimizer
// Source: generate-api-docs.py

export declare class ContextOptimizer {
  constructor(max_tokens: any, target_tokens: any);
  compress_whitespace(text: string): void;
  estimate_tokens(text: string): void;
  optimize(context: string, remove_secrets: boolean): void;
  optimize_prompt(prompt: string, system_prompt: any): void;
  remove_secrets(text: string): void;
  truncate_smart(text: string, max_tokens: number): void;
}

export declare function compress_whitespace(text: string): void;
export declare function estimate_tokens(text: string): void;
export declare function optimize(context: string, remove_secrets: boolean): void;
export declare function optimize_context(context: string, max_tokens: any, remove_secrets: boolean): void;
export declare function optimize_prompt(prompt: string, system_prompt: any): void;
export declare function remove_secrets(text: string): void;
export declare function truncate_smart(text: string, max_tokens: number): void;
