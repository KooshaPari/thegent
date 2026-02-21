// Auto-generated TypeScript declarations for batch_operations
// Source: generate-api-docs.py

export declare function batch_file_operations(files: Array<string>, operation: Callable<(Any, Any)>, batch_size: number): void;
export declare function batch_read_files(files: Array<string>, batch_size: number): void;
export declare function batch_write_files(file_contents: Record<(Path, str)>, batch_size: number): void;
export declare function read_file(file_path: string): [(Path, str)];
export declare function write_file(item: [(Path, str)]): void;
