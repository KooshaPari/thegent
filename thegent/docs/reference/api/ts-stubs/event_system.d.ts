// Auto-generated TypeScript declarations for event_system
// Source: generate-api-docs.py

export declare class EventSystem {
  constructor();
  emit(event_type: string, data: any): void;
  subscribe(event_type: string, handler: Callable): void;
}

export declare function emit(event_type: string, data: any): void;
export declare function subscribe(event_type: string, handler: Callable): void;
