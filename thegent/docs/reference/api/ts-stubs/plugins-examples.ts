// Auto-generated usage examples for plugins
// Source: generate-api-docs.py

import { BuiltinPlugins, DialogPlugin, ExtensionPlugin, Plugin, PluginInfo, PluginLoader, StatusPlugin, TerminalPlugin, WidgetPlugin, call_hooks, create_dialog_plugin, create_status_plugin, create_terminal_plugin, discover_plugins, enabled, get_compose, get_plugin, get_plugin_info, get_widgets, list_plugins, load, load_plugin, loaded, on_mount, on_plugin_load, on_unmount, register_hook, register_widget, reload_all, to_dict, unload, unload_plugin } from "./plugins";

// Create a BuiltinPlugins instance
const builtinplugins = new BuiltinPlugins();
builtinplugins.create_dialog_plugin(undefined as unknown as PluginInfo);
builtinplugins.create_status_plugin(undefined as unknown as PluginInfo);
builtinplugins.create_terminal_plugin(undefined as unknown as PluginInfo);
builtinplugins.get_plugin("example_name", undefined as unknown as any);

// Create a DialogPlugin instance
const dialogplugin = new DialogPlugin(undefined as unknown as PluginInfo);

// Create a ExtensionPlugin instance
const extensionplugin = new ExtensionPlugin(undefined as unknown as PluginInfo);
extensionplugin.call_hooks("example_hook_name");
extensionplugin.register_hook("example_hook_name", undefined as unknown as Callable);

// Create a Plugin instance
const plugin = new Plugin(undefined as unknown as PluginInfo);
plugin.enabled(false);
plugin.get_compose();
plugin.get_widgets();
plugin.load();
plugin.loaded();
plugin.on_mount();
plugin.on_unmount();
plugin.unload();

// Create a PluginInfo instance
const plugininfo = new PluginInfo();
plugininfo.to_dict();

// Create a PluginLoader instance
const pluginloader = new PluginLoader(undefined as unknown as any);
pluginloader.discover_plugins();
pluginloader.get_plugin("example_name");
pluginloader.get_plugin_info("example_name");
pluginloader.list_plugins();
pluginloader.load_plugin("example_name");
pluginloader.on_plugin_load(undefined as unknown as Callable<(Any, None)>);
pluginloader.reload_all();
pluginloader.unload_plugin("example_name");

// Create a StatusPlugin instance
const statusplugin = new StatusPlugin(undefined as unknown as PluginInfo);

// Create a TerminalPlugin instance
const terminalplugin = new TerminalPlugin(undefined as unknown as PluginInfo);

// Create a WidgetPlugin instance
const widgetplugin = new WidgetPlugin(undefined as unknown as PluginInfo);
widgetplugin.get_widgets();
widgetplugin.register_widget(undefined as unknown as type<Widget>);

// Call call_hooks
call_hooks(undefined as unknown as any, "example_hook_name");
// Call create_dialog_plugin
create_dialog_plugin(undefined as unknown as PluginInfo);
// Call create_status_plugin
create_status_plugin(undefined as unknown as PluginInfo);
// Call create_terminal_plugin
create_terminal_plugin(undefined as unknown as PluginInfo);
// Call discover_plugins
discover_plugins(undefined as unknown as any);
// Call enabled
enabled(undefined as unknown as any, false);
// Call get_compose
get_compose(undefined as unknown as any);
// Call get_plugin
get_plugin(undefined as unknown as any, "example_name", undefined as unknown as any);
// Call get_plugin_info
get_plugin_info(undefined as unknown as any, "example_name");
// Call get_widgets
get_widgets(undefined as unknown as any);
// Call list_plugins
list_plugins(undefined as unknown as any);
// Call load
load(undefined as unknown as any);
// Call load_plugin
load_plugin(undefined as unknown as any, "example_name");
// Call loaded
loaded(undefined as unknown as any);
// Call on_mount
on_mount(undefined as unknown as any);
// Call on_plugin_load
on_plugin_load(undefined as unknown as any, undefined as unknown as Callable<(Any, None)>);
// Call on_unmount
on_unmount(undefined as unknown as any);
// Call register_hook
register_hook(undefined as unknown as any, "example_hook_name", undefined as unknown as Callable);
// Call register_widget
register_widget(undefined as unknown as any, undefined as unknown as type<Widget>);
// Call reload_all
reload_all(undefined as unknown as any);
// Call to_dict
to_dict(undefined as unknown as any);
// Call unload
unload(undefined as unknown as any);
// Call unload_plugin
unload_plugin(undefined as unknown as any, "example_name");
