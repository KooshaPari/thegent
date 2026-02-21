// Auto-generated TypeScript declarations for processor
// Source: generate-api-docs.py

export declare class DocumentProcessor {
  constructor(pipeline: any);
  get_statistics(): void;
  process_batch(filepaths: Array<string>): void;
  process_file(filepath: string): void;
}

export declare class ProcessingPipeline {
  constructor();
  add_stage(stage: Callable<(Any, dict<(str, Any)])>>): void;
  process(filepath: string): void;
}

export declare class ProcessingResult {
}

export declare class ProcessingStatus extends Enum {
}

export declare function add_stage(stage: Callable<(Any, dict<(str, Any)])>>): void;
export declare function calculate_readability(filepath: string): void;
export declare function compute_file_hash(filepath: string): void;
export declare function count_lines(filepath: string): void;
export declare function extract_code_blocks(filepath: string): void;
export declare function extract_frontmatter(filepath: string): void;
export declare function extract_headings(filepath: string): void;
export declare function extract_links(filepath: string): void;
export declare function extract_metadata(filepath: string): void;
export declare function get_statistics(): void;
export declare function process(filepath: string): void;
export declare function process_batch(filepaths: Array<string>): void;
export declare function process_file(filepath: string): void;
