// Auto-generated usage examples for config_provider
// Source: generate-api-docs.py

import { ConfigProvider, EnvConfigProvider, get_config_provider, get_tenant_config, resolve } from "./config_provider";

// Create a ConfigProvider instance
const configprovider = new ConfigProvider();
configprovider.get_tenant_config("example_tenant_id");
configprovider.resolve(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);

// Create a EnvConfigProvider instance
const envconfigprovider = new EnvConfigProvider();
envconfigprovider.get_tenant_config("example_tenant_id");
envconfigprovider.resolve(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);

// Call get_config_provider
get_config_provider();
// Call get_tenant_config
get_tenant_config(undefined as unknown as any, "example_tenant_id");
// Call resolve
resolve(undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any, undefined as unknown as any);
