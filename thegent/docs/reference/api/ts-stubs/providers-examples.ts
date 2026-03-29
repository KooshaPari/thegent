// Auto-generated usage examples for providers
// Source: generate-api-docs.py

import { ProviderConfig, ProviderRegistry, ProviderType, clear, count, get, get_fallback_order, list_providers, register, unregister } from "./providers";

// Create a ProviderConfig instance
const providerconfig = new ProviderConfig();

// Create a ProviderRegistry instance
const providerregistry = new ProviderRegistry();
providerregistry.clear();
providerregistry.count();
providerregistry.get("example_provider_id");
providerregistry.get_fallback_order("example_provider_id");
providerregistry.list_providers();
providerregistry.register(undefined as unknown as ProviderConfig);
providerregistry.unregister("example_provider_id");

// Create a ProviderType instance
const providertype = new ProviderType();

// Call clear
clear(undefined as unknown as any);
// Call count
count(undefined as unknown as any);
// Call get
get(undefined as unknown as any, "example_provider_id");
// Call get_fallback_order
get_fallback_order(undefined as unknown as any, "example_provider_id");
// Call list_providers
list_providers(undefined as unknown as any);
// Call register
register(undefined as unknown as any, undefined as unknown as ProviderConfig);
// Call unregister
unregister(undefined as unknown as any, "example_provider_id");
