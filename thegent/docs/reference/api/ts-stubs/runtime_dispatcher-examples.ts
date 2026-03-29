// Auto-generated usage examples for runtime_dispatcher
// Source: generate-api-docs.py

import { MojoDispatcher, PerformanceModule, WasmDispatcher, call_plugin, get_impl, get_json_dumps, get_json_loads, get_router, get_runtime_status, get_toml_loads, register } from "./runtime_dispatcher";

// Create a MojoDispatcher instance
const mojodispatcher = new MojoDispatcher();

// Create a PerformanceModule instance
const performancemodule = new PerformanceModule("example_name");
performancemodule.get_impl();
performancemodule.register("example_runtime", undefined as unknown as any);

// Create a WasmDispatcher instance
const wasmdispatcher = new WasmDispatcher();
wasmdispatcher.call_plugin("example_plugin_path", "example_func_name", undefined as unknown as Uint8Array);

// Call call_plugin
call_plugin("example_plugin_path", "example_func_name", undefined as unknown as Uint8Array);
// Call get_impl
get_impl(undefined as unknown as any);
// Call get_json_dumps
get_json_dumps();
// Call get_json_loads
get_json_loads();
// Call get_router
get_router();
// Call get_runtime_status
get_runtime_status();
// Call get_toml_loads
get_toml_loads();
// Call register
register(undefined as unknown as any, "example_runtime", undefined as unknown as any);
