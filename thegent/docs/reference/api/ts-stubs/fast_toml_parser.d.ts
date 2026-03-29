// Auto-generated TypeScript declarations for fast_toml_parser
// Source: generate-api-docs.py

export declare class FastTOMLParser {
  constructor(edit_mode: boolean);
  backend(): void;
  dump(data: Record<(str, Any)>, stream: any): void;
  dumps(data: Record<(str, Any)>): void;
  load(stream: any): void;
  loads(s: string): void;
}

export declare function backend(): void;
export declare function dump(data: Record<(str, Any)>, stream: any): void;
export declare function dumps(data: Record<(str, Any)>): void;
export declare function get_toml_parser(edit_mode: boolean): void;
export declare function load(stream: any): void;
export declare function loads(s: string): void;
export declare function toml_dump(data: Record<(str, Any)>, stream: any): void;
export declare function toml_dumps(data: Record<(str, Any)>): void;
export declare function toml_load(stream: any): void;
export declare function toml_loads(s: string): void;
