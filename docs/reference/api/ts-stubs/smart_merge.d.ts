// Auto-generated TypeScript declarations for smart_merge
// Source: generate-api-docs.py

export declare class SmartMerger {
  constructor(mergiraf_path: string);
  merge_ast(base: string, local: string, remote: string, output: string): void;
  merge_structural(base_file: string, local_file: string, remote_file: string, output_file: string): void;
  predict_conflicts(intents: Array<Record<(str, Any)>>): void;
  resolve_imports(content: string, lang: string): void;
}

export declare function merge_ast(base: string, local: string, remote: string, output: string): void;
export declare function merge_structural(base_file: string, local_file: string, remote_file: string, output_file: string): void;
export declare function predict_conflicts(intents: Array<Record<(str, Any)>>): void;
export declare function resolve_imports(content: string, lang: string): void;
