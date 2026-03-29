// Auto-generated TypeScript declarations for idea_seed_system
// Source: generate-api-docs.py

export declare class IdeaSeedSystem {
  constructor(storage_path: any);
  detect_seed(content: string, context: any): void;
  get_seeds(keyword: any): void;
  store_seed(seed: Record<(str, Any)>): void;
}

export declare function detect_seed(content: string, context: any): void;
export declare function get_seeds(keyword: any): void;
export declare function store_seed(seed: Record<(str, Any)>): void;
