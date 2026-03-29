// Auto-generated TypeScript declarations for architecture_generator
// Source: generate-api-docs.py

export declare class ArchitectureGenerator {
  constructor();
  analyze_structure(root_path: string): void;
  generate_mermaid(structure: Record<(str, Any)>): void;
}

export declare function add_nodes(d: Record<(str, Any)>, prefix: string): void;
export declare function analyze_structure(root_path: string): void;
export declare function generate_mermaid(structure: Record<(str, Any)>): void;
