// Auto-generated TypeScript declarations for deferral
// Source: generate-api-docs.py

export declare class DeferralManager {
  constructor(settings: ThegentSettings);
  defer_task(task_id: string, reason: string): void;
  list_deferred(): void;
  should_defer(task_priority: string, load_level: number): void;
}

export declare class DeferralRule {
  constructor(id: string, condition: string, action: string);
}

export declare function defer_task(task_id: string, reason: string): void;
export declare function list_deferred(): void;
export declare function should_defer(task_priority: string, load_level: number): void;
