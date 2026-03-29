// Auto-generated usage examples for config
// Source: generate-api-docs.py

import { ConfigManager, KeyBinding, TUIConfig, disable_plugin, enable_plugin, export, from_dict, get, get_config, get_custom_css, get_keybindings, get_layout, get_plugins, get_shell, get_theme, import_config, remove_keybinding, reset, set, set_custom_css, set_keybinding, set_layout, set_shell, set_theme, to_dict, update } from "./config";

// Create a ConfigManager instance
const configmanager = new ConfigManager(undefined as unknown as any);
configmanager.disable_plugin("example_plugin");
configmanager.enable_plugin("example_plugin");
configmanager.export("example_path");
configmanager.get();
configmanager.get_custom_css();
configmanager.get_keybindings();
configmanager.get_layout();
configmanager.get_plugins();
configmanager.get_shell();
configmanager.get_theme();
configmanager.import_config("example_path", undefined as unknown as any);
configmanager.remove_keybinding("example_key");
configmanager.reset();
configmanager.set(undefined as unknown as TUIConfig);
configmanager.set_custom_css("example_css");
configmanager.set_keybinding("example_key", "example_action");
configmanager.set_layout("example_layout");
configmanager.set_shell("example_shell");
configmanager.set_theme("example_theme");
configmanager.update();

// Create a KeyBinding instance
const keybinding = new KeyBinding();
keybinding.to_dict();

// Create a TUIConfig instance
const tuiconfig = new TUIConfig();
tuiconfig.from_dict(undefined as unknown as Record<(str, Any)>);
tuiconfig.to_dict();

// Call disable_plugin
disable_plugin(undefined as unknown as any, "example_plugin");
// Call enable_plugin
enable_plugin(undefined as unknown as any, "example_plugin");
// Call export
export(undefined as unknown as any, "example_path");
// Call from_dict
from_dict(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call get
get(undefined as unknown as any);
// Call get_config
get_config(undefined as unknown as any);
// Call get_custom_css
get_custom_css(undefined as unknown as any);
// Call get_keybindings
get_keybindings(undefined as unknown as any);
// Call get_layout
get_layout(undefined as unknown as any);
// Call get_plugins
get_plugins(undefined as unknown as any);
// Call get_shell
get_shell(undefined as unknown as any);
// Call get_theme
get_theme(undefined as unknown as any);
// Call import_config
import_config(undefined as unknown as any, "example_path", undefined as unknown as any);
// Call remove_keybinding
remove_keybinding(undefined as unknown as any, "example_key");
// Call reset
reset(undefined as unknown as any);
// Call set
set(undefined as unknown as any, undefined as unknown as TUIConfig);
// Call set_custom_css
set_custom_css(undefined as unknown as any, "example_css");
// Call set_keybinding
set_keybinding(undefined as unknown as any, "example_key", "example_action");
// Call set_layout
set_layout(undefined as unknown as any, "example_layout");
// Call set_shell
set_shell(undefined as unknown as any, "example_shell");
// Call set_theme
set_theme(undefined as unknown as any, "example_theme");
// Call to_dict
to_dict(undefined as unknown as any);
// Call update
update(undefined as unknown as any);
