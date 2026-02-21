// Auto-generated TypeScript declarations for runtime_dispatcher
// Source: generate-api-docs.py

export declare class MojoDispatcher {
}

export declare class PerformanceModule {
  constructor(name: string);
  get_impl(): void;
  register(runtime: string, impl: any): void;
}

export declare class WasmDispatcher {
  call_plugin(plugin_path: string, func_name: string, data: Uint8Array): void;
}

export declare function call_plugin(plugin_path: string, func_name: string, data: Uint8Array): Uint8Array;
export declare function get_impl(): any;
export declare function get_json_dumps(): Callable;
export declare function get_json_loads(): Callable;
export declare function get_router(): any;
export declare function get_runtime_status(): Record<(str, Any)>;
export declare function get_toml_loads(): Callable;
export declare function register(runtime: string, impl: any): void;
