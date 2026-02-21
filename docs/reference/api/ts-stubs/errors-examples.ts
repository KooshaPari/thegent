// Auto-generated usage examples for errors
// Source: generate-api-docs.py

import { ConfigError, MCPError, ProviderError, ThegentError, get_hint_for_message, get_install_hint, print_error } from "./errors";

// Create a ConfigError instance
const configerror = new ConfigError("example_message", undefined as unknown as any);

// Create a MCPError instance
const mcperror = new MCPError("example_message", undefined as unknown as any);

// Create a ProviderError instance
const providererror = new ProviderError("example_message", undefined as unknown as any);

// Create a ThegentError instance
const thegenterror = new ThegentError("example_message", undefined as unknown as any);

// Call get_hint_for_message
get_hint_for_message("example_message");
// Call get_install_hint
get_install_hint("example_tool");
// Call print_error
print_error("example_message", undefined as unknown as any, undefined as unknown as any);
