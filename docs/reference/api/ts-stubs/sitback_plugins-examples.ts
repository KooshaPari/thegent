// Auto-generated usage examples for sitback_plugins
// Source: generate-api-docs.py

import { SitbackPluginRegistry, get_harness_status, get_registry, get_startup_steps, get_widgets, register_harness_status, register_startup_step, register_widget } from "./sitback_plugins";

// Create a SitbackPluginRegistry instance
const sitbackpluginregistry = new SitbackPluginRegistry();
sitbackpluginregistry.get_harness_status();
sitbackpluginregistry.get_startup_steps();
sitbackpluginregistry.get_widgets();
sitbackpluginregistry.register_harness_status(undefined as unknown as Callable<(Any, Any)>);
sitbackpluginregistry.register_startup_step("example_step");
sitbackpluginregistry.register_widget("example_name", undefined as unknown as Callable<(Any, dict<(str, Any)])>>);

// Call get_harness_status
get_harness_status(undefined as unknown as any);
// Call get_registry
get_registry();
// Call get_startup_steps
get_startup_steps(undefined as unknown as any);
// Call get_widgets
get_widgets(undefined as unknown as any);
// Call register_harness_status
register_harness_status(undefined as unknown as any, undefined as unknown as Callable<(Any, Any)>);
// Call register_startup_step
register_startup_step(undefined as unknown as any, "example_step");
// Call register_widget
register_widget(undefined as unknown as any, "example_name", undefined as unknown as Callable<(Any, dict<(str, Any)])>>);
