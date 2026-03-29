// Auto-generated TypeScript declarations for recorder
// Source: generate-api-docs.py

export declare class RecorderConfig {
}

export declare class RedactionConfig {
}

export declare class TraceCleanup {
  constructor(trace_dir: string, ttl_days: number);
}

export declare class TraceRecorder {
  constructor(session_id: string, config: any);
  delete_trace(): void;
  get_trace_file_size(): void;
}

export declare class TruncationConfig {
}

export declare function delete_trace(): void;
export declare function get_trace_file_size(): void;
