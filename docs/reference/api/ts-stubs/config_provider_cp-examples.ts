// Auto-generated usage examples for config_provider_cp
// Source: generate-api-docs.py

import { ControlPlaneConfigProvider, get_tenant_config, resolve } from "./config_provider_cp";

// Create a ControlPlaneConfigProvider instance
const controlplaneconfigprovider = new ControlPlaneConfigProvider("example_url", 0);
controlplaneconfigprovider.get_tenant_config("example_tenant_id");
controlplaneconfigprovider.resolve(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);

// Call get_tenant_config
get_tenant_config(undefined as unknown as any, "example_tenant_id");
// Call resolve
resolve(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
