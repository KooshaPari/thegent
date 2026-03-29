// Auto-generated TypeScript declarations for launch
// Source: generate-api-docs.py

export declare class LaunchObserver {
  constructor(settings: ThegentSettings);
  check_health(): void;
  trigger_rollback(reason: string): void;
}

export declare function check_health(): void;
export declare function trigger_rollback(reason: string): void;
