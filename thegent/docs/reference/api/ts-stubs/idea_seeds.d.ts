// Auto-generated TypeScript declarations for idea_seeds
// Source: generate-api-docs.py

export declare class IdeaSeed {
  to_dict(): void;
}

export declare class IdeaSeedScanner {
  constructor(context_lines: number);
  export_markdown(seeds: Array<IdeaSeed>, output: string): void;
  filter_by_type(seeds: Array<IdeaSeed>, types: Array<string>): void;
  scan_directory(root: string, extensions: any): void;
  scan_file(path: string): void;
  to_work_stream_items(seeds: Array<IdeaSeed>): void;
}

export declare function export_markdown(seeds: Array<IdeaSeed>, output: string): void;
export declare function filter_by_type(seeds: Array<IdeaSeed>, types: Array<string>): void;
export declare function scan_directory(root: string, extensions: any): void;
export declare function scan_file(path: string): void;
export declare function seeds_add_to_workstream(directory: string, workstream: string, types: string, dry_run: boolean): void;
export declare function seeds_export(directory: string, output: string, types: string, extensions: string): void;
export declare function seeds_scan(directory: string, types: string, extensions: string, output_json: boolean): void;
export declare function to_dict(): void;
export declare function to_work_stream_items(seeds: Array<IdeaSeed>): void;
