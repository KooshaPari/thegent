// Auto-generated TypeScript declarations for api_evolution
// Source: generate-api-docs.py

export declare class APIEvolutionManager {
  constructor(current_version: string);
  is_feature_enabled(flag: string): void;
  negotiate_version(client_version: string): void;
}

export declare function is_feature_enabled(flag: string): void;
export declare function negotiate_version(client_version: string): void;
