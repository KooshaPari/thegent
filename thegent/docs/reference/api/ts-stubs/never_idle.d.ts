// Auto-generated TypeScript declarations for never_idle
// Source: generate-api-docs.py

export declare class NeverIdleLoop {
  constructor(session_dir: any, sleep_interval: number, project_root: any);
  current_step(): void;
  get_findings(): void;
  get_last_completion(): void;
  get_status(): void;
  is_running(): void;
  register_wake_callback(callback: WakeCallback): void;
  start(): void;
  stop(): void;
}

export declare function current_step(): void;
export declare function get_findings(): void;
export declare function get_last_completion(): void;
export declare function get_never_idle(): void;
export declare function get_never_idle_status(): void;
export declare function get_status(): void;
export declare function is_running(): void;
export declare function register_wake_callback(callback: WakeCallback): void;
export declare function start(): void;
export declare function start_never_idle(sleep_interval: number, session_dir: any, project_root: any): void;
export declare function stop(): void;
export declare function stop_never_idle(): void;
