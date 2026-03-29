// Auto-generated TypeScript declarations for jetbrains
// Source: generate-api-docs.py

export declare class JetBrainsConfig {
  mcp_config_path(): void;
}

export declare class JetBrainsIntegration {
  constructor(mcp_server_url: string, serena_project_root: string);
  detect_installed_ides(): void;
  is_mcp_plugin_installed(config: JetBrainsConfig): void;
  read_existing_config(config: JetBrainsConfig): void;
  setup_all(): void;
  write_mcp_config(config: JetBrainsConfig): void;
}

export declare function detect_installed_ides(): void;
export declare function is_mcp_plugin_installed(config: JetBrainsConfig): void;
export declare function mcp_config_path(): void;
export declare function read_existing_config(config: JetBrainsConfig): void;
export declare function setup_all(): void;
export declare function write_mcp_config(config: JetBrainsConfig): void;
