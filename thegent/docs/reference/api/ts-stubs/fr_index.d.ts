// Auto-generated TypeScript declarations for fr_index
// Source: generate-api-docs.py

export declare class FRIndexSubcommands {
  constructor();
  extract_fr_ids(content: string): void;
  get_fr_references(fr_id: string): void;
  index_file(file_path: string): void;
}

export declare function extract_fr_ids(content: string): void;
export declare function get_fr_references(fr_id: string): void;
export declare function index_file(file_path: string): void;
