// Auto-generated TypeScript declarations for scanner
// Source: generate-api-docs.py

export declare class MarkdownScanner {
  constructor(config: ScanConfig);
  get_file_date(filepath: string): void;
  get_summary(): void;
  save_results(output_path: any): void;
  scan(): void;
  scan_directory(base_path: string, recursive: boolean, max_depth: any): void;
  should_exclude(filepath: string): void;
}

export declare class ScanConfig {
}

export declare function get_file_date(filepath: string): void;
export declare function get_summary(): void;
export declare function save_results(output_path: any): void;
export declare function scan(): void;
export declare function scan_directory(base_path: string, recursive: boolean, max_depth: any): void;
export declare function should_exclude(filepath: string): void;
