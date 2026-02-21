// Auto-generated TypeScript declarations for watcher_daemon
// Source: generate-api-docs.py

export declare class WatchEvent {
}

export declare class WatchSpec {
}

export declare class WatcherDaemon {
  constructor();
  add_watch(spec: WatchSpec): void;
  is_running(): void;
  list_watches(): void;
  remove_watch(watch_id: string): void;
  start(): void;
  stop(): void;
}

export declare class _SpecHandler extends PatternMatchingEventHandler {
  constructor(watch_id: string, spec: WatchSpec, breaker: any);
  on_created(event: any): void;
  on_deleted(event: any): void;
  on_modified(event: any): void;
  on_moved(event: any): void;
}

export declare function add_watch(spec: WatchSpec): void;
export declare function get_watcher_daemon(): void;
export declare function is_running(): void;
export declare function list_watches(): void;
export declare function on_created(event: any): void;
export declare function on_deleted(event: any): void;
export declare function on_modified(event: any): void;
export declare function on_moved(event: any): void;
export declare function remove_watch(watch_id: string): void;
export declare function start(): void;
export declare function stop(): void;
