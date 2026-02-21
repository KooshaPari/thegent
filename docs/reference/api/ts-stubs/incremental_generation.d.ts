// Auto-generated TypeScript declarations for incremental_generation
// Source: generate-api-docs.py

export declare class IncrementalGenerator {
  constructor(manifest_path: any);
  generate_incremental(files: Array<string>, generator_func: callable): void;
  get_changed_files(files: Array<string>): void;
}

export declare function generate_incremental(files: Array<string>, generator_func: callable): void;
export declare function get_changed_files(files: Array<string>): void;
