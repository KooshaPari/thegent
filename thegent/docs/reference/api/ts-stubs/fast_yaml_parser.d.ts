// Auto-generated TypeScript declarations for fast_yaml_parser
// Source: generate-api-docs.py

export declare class FastYAMLParser {
  constructor(preserve_formatting: boolean);
  backend(): void;
  dump(data: Record<(str, Any)>, stream: any): void;
  dumps(data: Record<(str, Any)>): void;
  load(stream: any): void;
  loads(s: string): void;
}

export declare function backend(): void;
export declare function dump(data: Record<(str, Any)>, stream: any): void;
export declare function dumps(data: Record<(str, Any)>): void;
export declare function get_yaml_parser(preserve_formatting: boolean): void;
export declare function load(stream: any): void;
export declare function loads(s: string): void;
export declare function yaml_dump(data: Record<(str, Any)>, stream: any): void;
export declare function yaml_dumps(data: Record<(str, Any)>): void;
export declare function yaml_load(stream: any): void;
export declare function yaml_loads(s: string): void;
