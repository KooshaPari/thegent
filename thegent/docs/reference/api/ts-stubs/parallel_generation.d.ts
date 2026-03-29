// Auto-generated TypeScript declarations for parallel_generation
// Source: generate-api-docs.py

export declare class ParallelGenerator {
  constructor(max_workers: number, use_processes: boolean);
  generate_batch(files: Array<string>, generator_func: Callable<(Any, dict<(str, Any)])>>, batch_size: number): void;
  generate_parallel(files: Array<string>, generator_func: Callable<(Any, dict<(str, Any)])>>): void;
}

export declare function generate_batch(files: Array<string>, generator_func: Callable<(Any, dict<(str, Any)])>>, batch_size: number): void;
export declare function generate_parallel(files: Array<string>, generator_func: Callable<(Any, dict<(str, Any)])>>): void;
