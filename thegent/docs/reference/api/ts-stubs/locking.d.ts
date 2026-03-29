// Auto-generated TypeScript declarations for locking
// Source: generate-api-docs.py

export declare class QueueLock {
  constructor(queue_path: string);
  read_entries(): void;
  write_entries(entries: Array<Record<string, unknown>>): void;
}

export declare function read_entries(): void;
export declare function write_entries(entries: Array<Record<string, unknown>>): void;
