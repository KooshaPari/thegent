// Auto-generated usage examples for jetbrains
// Source: generate-api-docs.py

import { JetBrainsConfig, JetBrainsIntegration, detect_installed_ides, is_mcp_plugin_installed, mcp_config_path, read_existing_config, setup_all, write_mcp_config } from "./jetbrains";

// Create a JetBrainsConfig instance
const jetbrainsconfig = new JetBrainsConfig();
jetbrainsconfig.mcp_config_path();

// Create a JetBrainsIntegration instance
const jetbrainsintegration = new JetBrainsIntegration("example_mcp_server_url", "example_serena_project_root");
jetbrainsintegration.detect_installed_ides();
jetbrainsintegration.is_mcp_plugin_installed(undefined as unknown as JetBrainsConfig);
jetbrainsintegration.read_existing_config(undefined as unknown as JetBrainsConfig);
jetbrainsintegration.setup_all();
jetbrainsintegration.write_mcp_config(undefined as unknown as JetBrainsConfig);

// Call detect_installed_ides
detect_installed_ides(undefined as unknown as any);
// Call is_mcp_plugin_installed
is_mcp_plugin_installed(undefined as unknown as any, undefined as unknown as JetBrainsConfig);
// Call mcp_config_path
mcp_config_path(undefined as unknown as any);
// Call read_existing_config
read_existing_config(undefined as unknown as any, undefined as unknown as JetBrainsConfig);
// Call setup_all
setup_all(undefined as unknown as any);
// Call write_mcp_config
write_mcp_config(undefined as unknown as any, undefined as unknown as JetBrainsConfig);
