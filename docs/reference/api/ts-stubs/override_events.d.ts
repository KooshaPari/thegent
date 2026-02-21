// Auto-generated TypeScript declarations for override_events
// Source: generate-api-docs.py

export declare class OverrideActivatedEvent {
  to_dict(): void;
}

export declare class OverrideEventEmitter {
  constructor(events_path: any);
  emit_activated(override_id: string, policy_id: string, owner: string, ttl_s: number): void;
  emit_expired(event: OverrideExpiredEvent): void;
  tail_events(n: number): void;
}

export declare class OverrideExpiredEvent {
  to_dict(): void;
}

export declare class OverrideExpiryMonitor {
  constructor(emitter: any, poll_interval_s: number);
  register(override_id: string, expires_at: number, on_expire: Callable<(Any, None)>, policy_id: string, owner: string): void;
  start(): void;
  stop(timeout_s: number): void;
  unregister(override_id: string): void;
}

export declare class _Registration {
}

export declare function emit_activated(override_id: string, policy_id: string, owner: string, ttl_s: number): void;
export declare function emit_expired(event: OverrideExpiredEvent): void;
export declare function register(override_id: string, expires_at: number, on_expire: Callable<(Any, None)>, policy_id: string, owner: string): void;
export declare function start(): void;
export declare function stop(timeout_s: number): void;
export declare function tail_events(n: number): void;
export declare function to_dict(): void;
export declare function unregister(override_id: string): void;
