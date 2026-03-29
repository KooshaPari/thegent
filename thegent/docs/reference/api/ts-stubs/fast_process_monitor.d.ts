// Auto-generated TypeScript declarations for fast_process_monitor
// Source: generate-api-docs.py

export declare class FastProcessMonitor {
  constructor();
  find_by_command(patterns: Array<string>): void;
  find_processes(predicate: Callable<(Any, bool)>): void;
  get_process(pid: number): void;
  get_process_count(): void;
  get_process_info_detailed(pid: number): void;
  iter_processes(attrs: any, use_cache: boolean): void;
}

export declare class ProcessInfo {
}

export declare function find_by_command(patterns: Array<string>): void;
export declare function find_processes(predicate: Callable<(Any, bool)>): void;
export declare function get_fast_monitor(): void;
export declare function get_process(pid: number): void;
export declare function get_process_count(): void;
export declare function get_process_info_detailed(pid: number): void;
export declare function iter_processes(attrs: any, use_cache: boolean): void;
export declare function matches(info: ProcessInfo): boolean;
