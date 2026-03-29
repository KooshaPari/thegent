// Auto-generated TypeScript declarations for learning
// Source: generate-api-docs.py

export declare class LearningSubcommands {
  constructor(learning_db_path: any);
  record(pattern: string, skipped: boolean, reason: string): void;
  should_skip(pattern: string, threshold: number): void;
}

export declare function record(pattern: string, skipped: boolean, reason: string): void;
export declare function should_skip(pattern: string, threshold: number): void;
