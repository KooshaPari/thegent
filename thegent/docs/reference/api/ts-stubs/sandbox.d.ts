// Auto-generated TypeScript declarations for sandbox
// Source: generate-api-docs.py

export declare class ResourceUsage {
}

export declare class SandboxConfig extends BaseModel {
}

export declare class SandboxFeature extends Enum {
}

export declare class SandboxStatus extends Enum {
}

export declare class WasmSandbox {
  constructor(sandbox_id: string, config: any);
  is_available(): void;
  run_function(wasm_binary_path: string, function_name: string, input_data: any, fallback_fn: any): void;
  shutdown(): void;
}

export declare function check_wasm_support(): void;
export declare function create_sandboxed_executor(config: any): void;
export declare function is_available(): void;
export declare function run_function(wasm_binary_path: string, function_name: string, input_data: any, fallback_fn: any): void;
export declare function run_with_timeout(): void;
export declare function shutdown(): void;
