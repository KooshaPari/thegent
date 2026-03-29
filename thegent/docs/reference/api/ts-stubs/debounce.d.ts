// Auto-generated TypeScript declarations for debounce
// Source: generate-api-docs.py

export declare class DebounceSubcommand {
  constructor(debounce_dir: any);
  clear(key: string): void;
  debounce(key: string, delay_seconds: number): void;
}

export declare function clear(key: string): void;
export declare function debounce(key: string, delay_seconds: number): void;
