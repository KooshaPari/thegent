// Auto-generated usage examples for tenancy
// Source: generate-api-docs.py

import { KeyIsolator, delete_tenant, get_key, get_tenant_dir, isolate_key, list_tenants } from "./tenancy";

// Create a KeyIsolator instance
const keyisolator = new KeyIsolator(undefined as unknown as any);
keyisolator.delete_tenant("example_owner");
keyisolator.get_key("example_owner", "example_provider");
keyisolator.get_tenant_dir("example_owner");
keyisolator.isolate_key("example_owner", "example_provider", "example_api_key");
keyisolator.list_tenants();

// Call delete_tenant
delete_tenant(undefined as unknown as any, "example_owner");
// Call get_key
get_key(undefined as unknown as any, "example_owner", "example_provider");
// Call get_tenant_dir
get_tenant_dir(undefined as unknown as any, "example_owner");
// Call isolate_key
isolate_key(undefined as unknown as any, "example_owner", "example_provider", "example_api_key");
// Call list_tenants
list_tenants(undefined as unknown as any);
