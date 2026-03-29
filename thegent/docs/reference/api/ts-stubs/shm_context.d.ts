// Auto-generated TypeScript declarations for shm_context
// Source: generate-api-docs.py

export declare class ContextSharer {
  constructor();
  get_context(session_id: string): void;
  release_context(session_id: string): void;
}

export declare class ZeroCopyContext {
  constructor(size: number);
  close(): void;
  read_context(size: number, offset: number): void;
  write_context(data: Uint8Array, offset: number): void;
}

export declare function close(): void;
export declare function get_context(session_id: string): void;
export declare function read_context(size: number, offset: number): void;
export declare function release_context(session_id: string): void;
export declare function write_context(data: Uint8Array, offset: number): void;
