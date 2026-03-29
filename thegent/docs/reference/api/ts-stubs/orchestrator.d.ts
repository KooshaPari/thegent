// Auto-generated TypeScript declarations for orchestrator
// Source: generate-api-docs.py

export declare class CatalogSyncComponent extends SyncComponent {
  constructor();
}

export declare class DagSyncComponent extends SyncComponent {
  constructor();
}

export declare class RulesSyncComponent extends SyncComponent {
  constructor();
}

export declare class SyncComponent extends ABC {
  constructor(name: string, description: string, depends_on: any);
}

export declare class SyncOrchestrator {
  constructor(registry: any);
}

export declare class SyncRegistry {
  constructor();
  get_all_components(): void;
  get_component(name: string): void;
  register(component: SyncComponent): void;
}

export declare class SyncResult {
  to_dict(): void;
}

export declare class SyncStatus extends Enum {
}

export declare class WorkStreamSyncComponent extends SyncComponent {
  constructor();
}

export declare function get_all_components(): Array<SyncComponent>;
export declare function get_component(name: string): any;
export declare function register(component: SyncComponent): void;
export declare function resolve(comp: SyncComponent): void;
export declare function to_dict(): Record<(str, Any)>;
