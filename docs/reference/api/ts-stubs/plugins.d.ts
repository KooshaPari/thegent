// Auto-generated TypeScript declarations for plugins
// Source: generate-api-docs.py

export declare class BuiltinPlugins {
  create_dialog_plugin(info: PluginInfo): void;
  create_status_plugin(info: PluginInfo): void;
  create_terminal_plugin(info: PluginInfo): void;
  get_plugin(name: string, info: any): void;
}

export declare class DialogPlugin extends WidgetPlugin {
  constructor(info: PluginInfo);
}

export declare class ExtensionPlugin extends Plugin {
  constructor(info: PluginInfo);
  call_hooks(hook_name: string): void;
  register_hook(hook_name: string, callback: Callable): void;
}

export declare class Plugin {
  constructor(info: PluginInfo);
  enabled(value: boolean): void;
  get_compose(): void;
  get_widgets(): void;
  load(): void;
  loaded(): void;
  on_mount(): void;
  on_unmount(): void;
  unload(): void;
}

export declare class PluginInfo {
  to_dict(): void;
}

export declare class PluginLoader {
  constructor(plugin_dir: any);
  discover_plugins(): void;
  get_plugin(name: string): void;
  get_plugin_info(name: string): void;
  list_plugins(): void;
  load_plugin(name: string): void;
  on_plugin_load(callback: Callable<(Any, None)>): void;
  reload_all(): void;
  unload_plugin(name: string): void;
}

export declare class StatusPlugin extends WidgetPlugin {
  constructor(info: PluginInfo);
}

export declare class TerminalPlugin extends WidgetPlugin {
  constructor(info: PluginInfo);
}

export declare class WidgetPlugin extends Plugin {
  constructor(info: PluginInfo);
  get_widgets(): void;
  register_widget(widget_class: type<Widget>): void;
}

export declare function call_hooks(hook_name: string): void;
export declare function create_dialog_plugin(info: PluginInfo): void;
export declare function create_status_plugin(info: PluginInfo): void;
export declare function create_terminal_plugin(info: PluginInfo): void;
export declare function discover_plugins(): void;
export declare function enabled(value: boolean): void;
export declare function get_compose(): void;
export declare function get_plugin(name: string, info: any): void;
export declare function get_plugin_info(name: string): void;
export declare function get_widgets(): Array<type<Widget>>;
export declare function list_plugins(): void;
export declare function load(): void;
export declare function load_plugin(name: string): void;
export declare function loaded(): boolean;
export declare function on_mount(): void;
export declare function on_plugin_load(callback: Callable<(Any, None)>): void;
export declare function on_unmount(): void;
export declare function register_hook(hook_name: string, callback: Callable): void;
export declare function register_widget(widget_class: type<Widget>): void;
export declare function reload_all(): void;
export declare function to_dict(): Record<(str, Any)>;
export declare function unload(): void;
export declare function unload_plugin(name: string): void;
