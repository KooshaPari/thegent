// Auto-generated TypeScript declarations for smart_prune
// Source: generate-api-docs.py

export declare class SessionSnapshot {
}

export declare class SmartPruner {
  constructor(project_root: any);
  check_docs_written(session_start_time: number): void;
  detect_completion(output: string): void;
  discover_sessions(): void;
  run_cycle(force_prune: boolean, reprompt: boolean): void;
}

export declare function check_docs_written(session_start_time: number): void;
export declare function detect_completion(output: string): void;
export declare function discover_sessions(): void;
export declare function get_tty_path(tty: string): void;
export declare function pause_process(pid: number): void;
export declare function resume_process(pid: number): void;
export declare function run_cycle(force_prune: boolean, reprompt: boolean): void;
export declare function smart_prune_main(force: boolean, reprompt: boolean): void;
