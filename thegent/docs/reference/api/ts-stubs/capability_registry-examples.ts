// Auto-generated usage examples for capability_registry
// Source: generate-api-docs.py

import { Capability, CapabilityRegistry, get_capability, is_supported, list_capabilities, register } from "./capability_registry";

// Create a Capability instance
const capability = new Capability();

// Create a CapabilityRegistry instance
const capabilityregistry = new CapabilityRegistry();
capabilityregistry.get_capability("example_cap_id");
capabilityregistry.is_supported("example_cap_id", undefined as unknown as any);
capabilityregistry.list_capabilities();
capabilityregistry.register(undefined as unknown as Capability);

// Call get_capability
get_capability(undefined as unknown as any, "example_cap_id");
// Call is_supported
is_supported(undefined as unknown as any, "example_cap_id", undefined as unknown as any);
// Call list_capabilities
list_capabilities(undefined as unknown as any);
// Call register
register(undefined as unknown as any, undefined as unknown as Capability);
