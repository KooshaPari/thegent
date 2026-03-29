// Auto-generated TypeScript declarations for hierarchy
// Source: generate-api-docs.py

export declare class AgentTree {
  constructor();
  get(name: string): void;
  get_ancestors(name: string): void;
  get_children(name: string): void;
  get_descendants(name: string): void;
  get_parent(name: string): void;
  list_agents(): void;
  register(agent: SmolAgent): void;
  to_dict(): void;
}

export declare function get(name: string): void;
export declare function get_ancestors(name: string): void;
export declare function get_children(name: string): void;
export declare function get_descendants(name: string): void;
export declare function get_parent(name: string): void;
export declare function list_agents(): void;
export declare function register(agent: SmolAgent): void;
export declare function to_dict(): void;
