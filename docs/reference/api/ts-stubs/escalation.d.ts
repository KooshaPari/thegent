// Auto-generated TypeScript declarations for escalation
// Source: generate-api-docs.py

export declare class EscalationItem {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
}

export declare class EscalationPriority extends StrEnum {
}

export declare class EscalationQueue {
  constructor(settings: any);
  add(run_id: string, reason: string, priority: number): void;
  escalate(run_id: string, prompt: string, reason: string, agent: string, priority: EscalationPriority, sla_minutes: number, metadata: any): void;
  get_item(esc_id: string): void;
  list_items(status: any): void;
  resolve(esc_id: string, resolution: string, solver: string): void;
}

export declare class EscalationStatus extends StrEnum {
}

export declare function add(run_id: string, reason: string, priority: number): void;
export declare function escalate(run_id: string, prompt: string, reason: string, agent: string, priority: EscalationPriority, sla_minutes: number, metadata: any): void;
export declare function from_dict(data: Record<(str, Any)>): void;
export declare function get_item(esc_id: string): void;
export declare function list_items(status: any): void;
export declare function resolve(esc_id: string, resolution: string, solver: string): void;
export declare function to_dict(): void;
