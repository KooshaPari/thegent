// Auto-generated TypeScript declarations for dispatch_graph
// Source: generate-api-docs.py

export declare class DispatchResolver {
  constructor(registry: any);
  add_alias(alias: string, target_command: string): void;
  resolve(envelope: any): void;
}

export declare function add_alias(alias: string, target_command: string): void;
export declare function resolve(envelope: any): void;
