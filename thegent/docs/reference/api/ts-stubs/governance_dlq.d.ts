// Auto-generated TypeScript declarations for governance_dlq
// Source: generate-api-docs.py

export declare class EscalationQueueDLQ {
  constructor();
  enqueue(item: Record<(str, Any)>): void;
  move_to_dlq(item: Record<(str, Any)>, reason: string): void;
  process(): void;
}

export declare function enqueue(item: Record<(str, Any)>): void;
export declare function move_to_dlq(item: Record<(str, Any)>, reason: string): void;
export declare function process(): void;
