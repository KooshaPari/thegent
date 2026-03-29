// Auto-generated TypeScript declarations for reusable_helpers
// Source: generate-api-docs.py

export declare class ReusableHelpers {
  ensure_directory(path: string): void;
  find_files(directory: string, pattern: string, recursive: boolean): void;
  read_file_efficiency(file_path: string, offset: number, limit: any): void;
  read_json_safe(file_path: string): void;
  retry_on_failure(func: Callable, max_retries: number, delay: number): void;
  safe_execute(func: Callable): void;
  write_json_safe(file_path: string, data: Record<(str, Any)>): void;
}

export declare function ensure_directory(path: string): void;
export declare function find_files(directory: string, pattern: string, recursive: boolean): void;
export declare function read_file_efficiency(file_path: string, offset: number, limit: any): void;
export declare function read_json_safe(file_path: string): void;
export declare function retry_on_failure(func: Callable, max_retries: number, delay: number): void;
export declare function safe_execute(func: Callable): void;
export declare function write_json_safe(file_path: string, data: Record<(str, Any)>): void;
