// Auto-generated usage examples for vfs
// Source: generate-api-docs.py

import { VfsAdapter, cleanup_home_dir, create_home_dir } from "./vfs";

// Create a VfsAdapter instance
const vfsadapter = new VfsAdapter(undefined as unknown as any);
vfsadapter.cleanup_home_dir("example_target_dir", "example_tenant_id");
vfsadapter.create_home_dir("example_target_dir", "example_tenant_id");

// Call cleanup_home_dir
cleanup_home_dir(undefined as unknown as any, "example_target_dir", "example_tenant_id");
// Call create_home_dir
create_home_dir(undefined as unknown as any, "example_target_dir", "example_tenant_id");
