// Auto-generated TypeScript declarations for memory
// Source: generate-api-docs.py

export declare class FrictionScope extends StrEnum {
}

export declare class MemoryCategory extends StrEnum {
}

export declare class MemoryFragment {
}

export declare class MemorySystem {
  constructor(project_root: string);
  get_recent(limit: number, category: any): void;
  record(content: string, category: MemoryCategory, agent_id: string, scope: any, metadata: any): void;
  synthesize_to_markdown(): void;
}

export declare function get_recent(limit: number, category: any): Array<MemoryFragment>;
export declare function record(content: string, category: MemoryCategory, agent_id: string, scope: any, metadata: any): MemoryFragment;
export declare function synthesize_to_markdown(): void;
