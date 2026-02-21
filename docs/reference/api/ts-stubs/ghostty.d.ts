// Auto-generated TypeScript declarations for ghostty
// Source: generate-api-docs.py

export declare class GhosttyConfig {
}

export declare class GhosttyError extends Exception {
}

export declare class GhosttyIntegration {
  constructor(config_path: any);
  get_config(): void;
  get_env_info(): void;
  is_available(): void;
  open_tab(command: any): void;
  send_notification(title: string, body: string): void;
  set_theme(theme: string): void;
}

export declare function get_config(): void;
export declare function get_env_info(): void;
export declare function is_available(): void;
export declare function open_tab(command: any): void;
export declare function send_notification(title: string, body: string): void;
export declare function set_theme(theme: string): void;
