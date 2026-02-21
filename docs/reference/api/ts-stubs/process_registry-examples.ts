// Auto-generated usage examples for process_registry
// Source: generate-api-docs.py

import { ProcessHandle, ProcessRegistry, cleanup_all, cleanup_orphaned, cleanup_process_tree, get, get_psutil_process, get_registry, get_resource_usage, get_stats, is_alive, list_alive, register, terminate, unregister } from "./process_registry";

// Create a ProcessHandle instance
const processhandle = new ProcessHandle();
processhandle.get_psutil_process();
processhandle.get_resource_usage();
processhandle.is_alive();
processhandle.terminate(0);

// Create a ProcessRegistry instance
const processregistry = new ProcessRegistry();
processregistry.cleanup_all(0);
processregistry.cleanup_orphaned();
processregistry.cleanup_process_tree(0, 0);
processregistry.get(0);
processregistry.get_stats();
processregistry.list_alive();
processregistry.register(undefined as unknown as subprocess.Popen, "example_name", false, undefined as unknown as any);
processregistry.unregister(0);

// Call cleanup_all
cleanup_all(undefined as unknown as any, 0);
// Call cleanup_orphaned
cleanup_orphaned(undefined as unknown as any);
// Call cleanup_process_tree
cleanup_process_tree(undefined as unknown as any, 0, 0);
// Call get
get(undefined as unknown as any, 0);
// Call get_psutil_process
get_psutil_process(undefined as unknown as any);
// Call get_registry
get_registry();
// Call get_resource_usage
get_resource_usage(undefined as unknown as any);
// Call get_stats
get_stats(undefined as unknown as any);
// Call is_alive
is_alive(undefined as unknown as any);
// Call list_alive
list_alive(undefined as unknown as any);
// Call register
register(undefined as unknown as any, undefined as unknown as subprocess.Popen, "example_name", false, undefined as unknown as any);
// Call terminate
terminate(undefined as unknown as any, 0);
// Call unregister
unregister(undefined as unknown as any, 0);
