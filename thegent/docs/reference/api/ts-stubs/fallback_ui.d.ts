// Auto-generated TypeScript declarations for fallback_ui
// Source: generate-api-docs.py

export declare class FallbackOption {
  constructor(id: string, label: string, description: string, command: string);
}

export declare class FallbackRegistry {
  constructor(settings: ThegentSettings);
  get_recommendations(failure_kind: string): void;
}

export declare function get_recommendations(failure_kind: string): void;
