// Auto-generated TypeScript declarations for file_reading
// Source: generate-api-docs.py

export declare class EfficientFileReader {
  read_chunk(file_path: string, offset: number, limit: number): void;
  read_lines(file_path: string, start_line: number, num_lines: number): void;
}

export declare function read_chunk(file_path: string, offset: number, limit: number): void;
export declare function read_lines(file_path: string, start_line: number, num_lines: number): void;
