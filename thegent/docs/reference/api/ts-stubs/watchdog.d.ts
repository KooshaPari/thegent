// Auto-generated TypeScript declarations for watchdog
// Source: generate-api-docs.py

export declare class BackgroundTaskWatcher {
  constructor(session_dir: any, poll_interval: number);
  check_completions(): void;
  get_known_sessions(): void;
  register_callback(callback: CompletionCallback): void;
  reset(): void;
  run_once(): void;
  wait_for_completion(timeout: any): void;
}

export declare function check_completions(): void;
export declare function get_known_sessions(): void;
export declare function register_callback(callback: CompletionCallback): void;
export declare function reset(): void;
export declare function run_once(): void;
export declare function wait_for_completion(timeout: any): void;
