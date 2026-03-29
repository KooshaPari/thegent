// Auto-generated TypeScript declarations for auto_launch
// Source: generate-api-docs.py

export declare class AutoLaunchSystem {
  constructor(settings: any);
  handle_completion(session_id: string, exit_code: number): void;
  record_event(event_type: string, session_id: any, item_id: any, payload: any): void;
  start(): void;
  stop(): void;
  sync_database(): void;
}

export declare function handle_completion(session_id: string, exit_code: number): void;
export declare function periodic_tasks(): void;
export declare function record_event(event_type: string, session_id: any, item_id: any, payload: any): void;
export declare function start(): void;
export declare function stop(): void;
export declare function sync_database(): void;
