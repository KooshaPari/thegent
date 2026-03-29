// Auto-generated TypeScript declarations for process_registry
// Source: generate-api-docs.py

export declare class ProcessHandle {
  get_psutil_process(): void;
  get_resource_usage(): void;
  is_alive(): void;
  terminate(timeout: number): void;
}

export declare class ProcessRegistry {
  constructor();
  cleanup_all(timeout: number): void;
  cleanup_orphaned(): void;
  cleanup_process_tree(pid: number, timeout: number): void;
  get(pid: number): void;
  get_stats(): void;
  list_alive(): void;
  register(proc: subprocess.Popen, name: string, cleanup_on_exit: boolean, timeout: any): void;
  unregister(pid: number): void;
}

export declare function cleanup_all(timeout: number): void;
export declare function cleanup_orphaned(): void;
export declare function cleanup_process_tree(pid: number, timeout: number): void;
export declare function get(pid: number): void;
export declare function get_psutil_process(): void;
export declare function get_registry(): void;
export declare function get_resource_usage(): void;
export declare function get_stats(): void;
export declare function is_alive(): void;
export declare function list_alive(): void;
export declare function register(proc: subprocess.Popen, name: string, cleanup_on_exit: boolean, timeout: any): void;
export declare function terminate(timeout: number): void;
export declare function unregister(pid: number): void;
