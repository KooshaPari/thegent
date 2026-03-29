// Auto-generated TypeScript declarations for plugin_lifecycle
// Source: generate-api-docs.py

export declare class PluginLifecycleManager {
  constructor();
  get_plugin_status(plugin_id: string): void;
  register_plugin(plugin_id: string, metadata: Record<(str, Any)>): void;
  run_conformance(plugin_id: string): void;
}

export declare class PluginStatus extends StrEnum {
}

export declare function get_plugin_status(plugin_id: string): void;
export declare function register_plugin(plugin_id: string, metadata: Record<(str, Any)>): void;
export declare function run_conformance(plugin_id: string): void;
