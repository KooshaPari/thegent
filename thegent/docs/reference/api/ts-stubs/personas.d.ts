// Auto-generated TypeScript declarations for personas
// Source: generate-api-docs.py

export declare class PersonaManager {
  constructor(agents_dir: any);
  check_access(persona: string, operation: string, lane: string): void;
  discover_teammates(): void;
  list_teammates(): void;
}

export declare function check_access(persona: string, operation: string, lane: string): void;
export declare function discover_teammates(): void;
export declare function list_teammates(): void;
