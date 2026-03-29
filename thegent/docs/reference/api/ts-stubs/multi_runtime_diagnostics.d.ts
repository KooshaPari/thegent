// Auto-generated TypeScript declarations for multi_runtime_diagnostics
// Source: generate-api-docs.py

export declare class RuntimeStatus {
}

export declare function check_all_runtimes(mesh_root: any): void;
export declare function check_cpython_313(): void;
export declare function check_cpython_314(): void;
export declare function check_go(): void;
export declare function check_hardware(): void;
export declare function check_ipc_mesh(mesh_root: string): void;
export declare function check_mojo(): void;
export declare function check_network_latency(target_host: string): void;
export declare function check_pypy(): void;
export declare function check_rust(): void;
export declare function check_zig(): void;
export declare function display_runtime_status(data: Record<(str, Any)>): void;
