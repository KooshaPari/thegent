// Auto-generated TypeScript declarations for schema
// Source: generate-api-docs.py

export declare class DecisionRecord {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
}

export declare class SessionRecord {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
}

export declare class ToolCallRecord {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
}

export declare class TraceFile {
  constructor(path: string, compression: any);
  delete(): void;
  get_file_size(): void;
  read_records(): void;
  write_record(record: any): void;
}

export declare class TraceRecord {
  from_dict(data: Record<(str, Any)>): void;
}

export declare function delete(): void;
export declare function from_dict(data: Record<(str, Any)>): void;
export declare function get_file_size(): void;
export declare function read_records(): void;
export declare function to_dict(): void;
export declare function validate_record(record: any): void;
export declare function write_record(record: any): void;
