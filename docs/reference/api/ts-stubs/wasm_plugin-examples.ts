// Auto-generated usage examples for wasm_plugin
// Source: generate-api-docs.py

import { ExtismPlugin, ExtismRuntime, PluginStatus, ResourceLimits, WasmCapability, WasmExecutionResult, WasmPlugin, WasmPluginManager, WasmPluginMetadata, WasmRuntimeStatus, clear, create_plugin_from_manifest, error_message, execute, execute_plugin, get_extism, get_plugin, get_plugin_manager, initialize, is_available, list_plugins, load, load_plugin, register_plugin, remove_plugin, status, unload, unload_plugin } from "./wasm_plugin";

// Create a ExtismPlugin instance
const extismplugin = new ExtismPlugin("example_plugin_path", undefined as unknown as WasmPluginMetadata, undefined as unknown as any, undefined as unknown as any, false);
extismplugin.execute(undefined as unknown as any);
extismplugin.load();
extismplugin.unload();

// Create a ExtismRuntime instance
const extismruntime = new ExtismRuntime();
extismruntime.error_message();
extismruntime.get_extism();
extismruntime.initialize();
extismruntime.is_available();
extismruntime.status();

// Create a PluginStatus instance
const pluginstatus = new PluginStatus();

// Create a ResourceLimits instance
const resourcelimits = new ResourceLimits();

// Create a WasmCapability instance
const wasmcapability = new WasmCapability();

// Create a WasmExecutionResult instance
const wasmexecutionresult = new WasmExecutionResult();

// Create a WasmPlugin instance
const wasmplugin = new WasmPlugin("example_plugin_path", undefined as unknown as WasmPluginMetadata, undefined as unknown as any, undefined as unknown as any);
wasmplugin.execute(undefined as unknown as any);
wasmplugin.load();
wasmplugin.status();
wasmplugin.unload();

// Create a WasmPluginManager instance
const wasmpluginmanager = new WasmPluginManager(undefined as unknown as any);
wasmpluginmanager.clear();
wasmpluginmanager.execute_plugin("example_name", undefined as unknown as any);
wasmpluginmanager.get_plugin("example_name");
wasmpluginmanager.initialize();
wasmpluginmanager.is_available();
wasmpluginmanager.list_plugins();
wasmpluginmanager.load_plugin("example_name");
wasmpluginmanager.register_plugin(undefined as unknown as WasmPlugin);
wasmpluginmanager.remove_plugin("example_name");
wasmpluginmanager.unload_plugin("example_name");

// Create a WasmPluginMetadata instance
const wasmpluginmetadata = new WasmPluginMetadata();

// Create a WasmRuntimeStatus instance
const wasmruntimestatus = new WasmRuntimeStatus();

// Call clear
clear(undefined as unknown as any);
// Call create_plugin_from_manifest
create_plugin_from_manifest("example_manifest_path");
// Call error_message
error_message(undefined as unknown as any);
// Call execute
execute(undefined as unknown as any, undefined as unknown as any);
// Call execute_plugin
execute_plugin(undefined as unknown as any, "example_name", undefined as unknown as any);
// Call get_extism
get_extism(undefined as unknown as any);
// Call get_plugin
get_plugin(undefined as unknown as any, "example_name");
// Call get_plugin_manager
get_plugin_manager();
// Call initialize
initialize(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
// Call list_plugins
list_plugins(undefined as unknown as any);
// Call load
load(undefined as unknown as any);
// Call load_plugin
load_plugin(undefined as unknown as any, "example_name");
// Call register_plugin
register_plugin(undefined as unknown as any, undefined as unknown as WasmPlugin);
// Call remove_plugin
remove_plugin(undefined as unknown as any, "example_name");
// Call status
status(undefined as unknown as any);
// Call unload
unload(undefined as unknown as any);
// Call unload_plugin
unload_plugin(undefined as unknown as any, "example_name");
