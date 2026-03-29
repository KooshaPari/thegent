// Auto-generated TypeScript declarations for wasm_plugin
// Source: generate-api-docs.py

export declare class ExtismPlugin extends WasmPlugin {
  constructor(plugin_path: string, metadata: WasmPluginMetadata, limits: any, config: any, allow_wasi: boolean);
  execute(input_data: any): void;
  load(): void;
  unload(): void;
}

export declare class ExtismRuntime {
  constructor();
  error_message(): void;
  get_extism(): void;
  initialize(): void;
  is_available(): void;
  status(): void;
}

export declare class PluginStatus extends Enum {
}

export declare class ResourceLimits {
}

export declare class WasmCapability extends Enum {
}

export declare class WasmExecutionResult {
}

export declare class WasmPlugin extends ABC {
  constructor(plugin_path: string, metadata: WasmPluginMetadata, limits: any, config: any);
  execute(input_data: any): void;
  load(): void;
  status(): void;
  unload(): void;
}

export declare class WasmPluginManager {
  constructor(plugin_dir: any);
  clear(): void;
  execute_plugin(name: string, input_data: any): void;
  get_plugin(name: string): void;
  initialize(): void;
  is_available(): void;
  list_plugins(): void;
  load_plugin(name: string): void;
  register_plugin(plugin: WasmPlugin): void;
  remove_plugin(name: string): void;
  unload_plugin(name: string): void;
}

export declare class WasmPluginMetadata {
}

export declare class WasmRuntimeStatus extends Enum {
}

export declare function clear(): void;
export declare function create_plugin_from_manifest(manifest_path: string): void;
export declare function error_message(): void;
export declare function execute(input_data: any): void;
export declare function execute_plugin(name: string, input_data: any): void;
export declare function get_extism(): void;
export declare function get_plugin(name: string): void;
export declare function get_plugin_manager(): void;
export declare function initialize(): void;
export declare function is_available(): void;
export declare function list_plugins(): void;
export declare function load(): void;
export declare function load_plugin(name: string): void;
export declare function register_plugin(plugin: WasmPlugin): void;
export declare function remove_plugin(name: string): void;
export declare function status(): void;
export declare function unload(): void;
export declare function unload_plugin(name: string): void;
