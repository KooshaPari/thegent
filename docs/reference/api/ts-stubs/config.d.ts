// Auto-generated TypeScript declarations for config
// Source: generate-api-docs.py

export declare class ConfigManager {
  constructor(config_dir: any);
  disable_plugin(plugin: string): void;
  enable_plugin(plugin: string): void;
  export(path: string): void;
  get(): void;
  get_custom_css(): void;
  get_keybindings(): void;
  get_layout(): void;
  get_plugins(): void;
  get_shell(): void;
  get_theme(): void;
  import_config(path: string, config_dir: any): void;
  remove_keybinding(key: string): void;
  reset(): void;
  set(config: TUIConfig): void;
  set_custom_css(css: string): void;
  set_keybinding(key: string, action: string): void;
  set_layout(layout: string): void;
  set_shell(shell: string): void;
  set_theme(theme: string): void;
  update(): void;
}

export declare class KeyBinding {
  to_dict(): void;
}

export declare class TUIConfig {
  from_dict(data: Record<(str, Any)>): void;
  to_dict(): void;
}

export declare function disable_plugin(plugin: string): void;
export declare function enable_plugin(plugin: string): void;
export declare function export(path: string): void;
export declare function from_dict(data: Record<(str, Any)>): TUIConfig;
export declare function get(): void;
export declare function get_config(config_dir: any): void;
export declare function get_custom_css(): void;
export declare function get_keybindings(): void;
export declare function get_layout(): void;
export declare function get_plugins(): void;
export declare function get_shell(): void;
export declare function get_theme(): void;
export declare function import_config(path: string, config_dir: any): void;
export declare function remove_keybinding(key: string): void;
export declare function reset(): void;
export declare function set(config: TUIConfig): void;
export declare function set_custom_css(css: string): void;
export declare function set_keybinding(key: string, action: string): void;
export declare function set_layout(layout: string): void;
export declare function set_shell(shell: string): void;
export declare function set_theme(theme: string): void;
export declare function to_dict(): Record<(str, str)>;
export declare function update(): void;
