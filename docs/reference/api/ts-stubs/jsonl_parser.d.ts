// Auto-generated TypeScript declarations for jsonl_parser
// Source: generate-api-docs.py

export declare class JsonlParser {
  count(path: string): void;
  filter(path: string, key: string, value: string): void;
  sample(path: string, n: number): void;
  stream(path: string): void;
}

export declare function count(path: string): void;
export declare function filter(path: string, key: string, value: string): void;
export declare function sample(path: string, n: number): void;
export declare function stream(path: string): void;
