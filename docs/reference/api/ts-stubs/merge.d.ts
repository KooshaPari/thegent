// Auto-generated TypeScript declarations for merge
// Source: generate-api-docs.py

export declare class SmartMerge {
  constructor(mesh_root: string);
  merge_ast_aware(base: string, ours: string, theirs: string, output: string): void;
  merge_structural(path_a: string, path_b: string, output: string): void;
  predict_conflicts(agent_intents: Array<Record<string, unknown>>): void;
  resolve_imports(content_a: string, content_b: string, language: string): void;
}

export declare function merge_ast_aware(base: string, ours: string, theirs: string, output: string): void;
export declare function merge_structural(path_a: string, path_b: string, output: string): void;
export declare function predict_conflicts(agent_intents: Array<Record<string, unknown>>): void;
export declare function resolve_imports(content_a: string, content_b: string, language: string): void;
