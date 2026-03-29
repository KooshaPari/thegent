// Auto-generated usage examples for sandbox
// Source: generate-api-docs.py

import { ResourceUsage, SandboxConfig, SandboxFeature, SandboxStatus, WasmSandbox, check_wasm_support, create_sandboxed_executor, is_available, run_function, run_with_timeout, shutdown } from "./sandbox";

// Create a ResourceUsage instance
const resourceusage = new ResourceUsage();

// Create a SandboxConfig instance
const sandboxconfig = new SandboxConfig();

// Create a SandboxFeature instance
const sandboxfeature = new SandboxFeature();

// Create a SandboxStatus instance
const sandboxstatus = new SandboxStatus();

// Create a WasmSandbox instance
const wasmsandbox = new WasmSandbox("example_sandbox_id", undefined as unknown as any);
wasmsandbox.is_available();
wasmsandbox.run_function("example_wasm_binary_path", "example_function_name", undefined as unknown as any, undefined as unknown as any);
wasmsandbox.shutdown();

// Call check_wasm_support
check_wasm_support();
// Call create_sandboxed_executor
create_sandboxed_executor(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
// Call run_function
run_function(undefined as unknown as any, "example_wasm_binary_path", "example_function_name", undefined as unknown as any, undefined as unknown as any);
// Call run_with_timeout
run_with_timeout();
// Call shutdown
shutdown(undefined as unknown as any);
