// Auto-generated usage examples for marketplace
// Source: generate-api-docs.py

import { PluginContract, PluginVerifier, check_permissions, verify_contract } from "./marketplace";

// Create a PluginContract instance
const plugincontract = new PluginContract();

// Create a PluginVerifier instance
const pluginverifier = new PluginVerifier(undefined as unknown as any);
pluginverifier.check_permissions(undefined as unknown as PluginContract, "example_requested_action");
pluginverifier.verify_contract(undefined as unknown as PluginContract);

// Call check_permissions
check_permissions(undefined as unknown as any, undefined as unknown as PluginContract, "example_requested_action");
// Call verify_contract
verify_contract(undefined as unknown as any, undefined as unknown as PluginContract);
