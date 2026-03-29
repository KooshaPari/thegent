// Auto-generated usage examples for uid_pool
// Source: generate-api-docs.py

import { UidPool, allocate, get_tenant_id, get_uid, release } from "./uid_pool";

// Create a UidPool instance
const uidpool = new UidPool(0, 0, undefined as unknown as any);
uidpool.allocate("example_tenant_id");
uidpool.get_tenant_id(0);
uidpool.get_uid("example_tenant_id");
uidpool.release("example_tenant_id");

// Call allocate
allocate(undefined as unknown as any, "example_tenant_id");
// Call get_tenant_id
get_tenant_id(undefined as unknown as any, 0);
// Call get_uid
get_uid(undefined as unknown as any, "example_tenant_id");
// Call release
release(undefined as unknown as any, "example_tenant_id");
