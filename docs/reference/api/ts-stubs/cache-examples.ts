// Auto-generated usage examples for cache
// Source: generate-api-docs.py

import { ResourceCache, clear, enable_invalidation, get, set } from "./cache";

// Create a ResourceCache instance
const resourcecache = new ResourceCache("example_cache_dir", 0, 0);
resourcecache.clear();
resourcecache.enable_invalidation("example_directory");
resourcecache.get("example_key");
resourcecache.set("example_key", undefined as unknown as any);

// Call clear
clear(undefined as unknown as any);
// Call enable_invalidation
enable_invalidation(undefined as unknown as any, "example_directory");
// Call get
get(undefined as unknown as any, "example_key");
// Call set
set(undefined as unknown as any, "example_key", undefined as unknown as any);
