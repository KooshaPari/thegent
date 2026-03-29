// Auto-generated usage examples for ghostty
// Source: generate-api-docs.py

import { GhosttyConfig, GhosttyError, GhosttyIntegration, get_config, get_env_info, is_available, open_tab, send_notification, set_theme } from "./ghostty";

// Create a GhosttyConfig instance
const ghosttyconfig = new GhosttyConfig();

// Create a GhosttyError instance
const ghosttyerror = new GhosttyError();

// Create a GhosttyIntegration instance
const ghosttyintegration = new GhosttyIntegration(undefined as unknown as any);
ghosttyintegration.get_config();
ghosttyintegration.get_env_info();
ghosttyintegration.is_available();
ghosttyintegration.open_tab(undefined as unknown as any);
ghosttyintegration.send_notification("example_title", "example_body");
ghosttyintegration.set_theme("example_theme");

// Call get_config
get_config(undefined as unknown as any);
// Call get_env_info
get_env_info(undefined as unknown as any);
// Call is_available
is_available(undefined as unknown as any);
// Call open_tab
open_tab(undefined as unknown as any, undefined as unknown as any);
// Call send_notification
send_notification(undefined as unknown as any, "example_title", "example_body");
// Call set_theme
set_theme(undefined as unknown as any, "example_theme");
