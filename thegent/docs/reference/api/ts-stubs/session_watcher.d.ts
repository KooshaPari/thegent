// Auto-generated TypeScript declarations for session_watcher
// Source: generate-api-docs.py

export declare class CompletionHandler {
  constructor(watcher: SessionEventWatcher);
  on_completion(session_id: string, exit_code: number): void;
}

export declare class SessionEventWatcher {
  constructor(session_dir: string);
  on_complete(callback: Callable<(Any, None)>): void;
  start(): void;
  stop(): void;
}

export declare function on_complete(callback: Callable<(Any, None)>): void;
export declare function on_completion(session_id: string, exit_code: number): void;
export declare function start(): void;
export declare function stop(): void;
export declare function watch_loop(): void;
