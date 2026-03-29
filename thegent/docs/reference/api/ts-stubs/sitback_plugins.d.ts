// Auto-generated TypeScript declarations for sitback_plugins
// Source: generate-api-docs.py

export declare class SitbackPluginRegistry {
  constructor();
  get_harness_status(): void;
  get_startup_steps(): void;
  get_widgets(): void;
  register_harness_status(fn: Callable<(Any, Any)>): void;
  register_startup_step(step: string): void;
  register_widget(name: string, fn: Callable<(Any, dict<(str, Any)])>>): void;
}

export declare function get_harness_status(): void;
export declare function get_registry(): void;
export declare function get_startup_steps(): void;
export declare function get_widgets(): void;
export declare function register_harness_status(fn: Callable<(Any, Any)>): void;
export declare function register_startup_step(step: string): void;
export declare function register_widget(name: string, fn: Callable<(Any, dict<(str, Any)])>>): void;
