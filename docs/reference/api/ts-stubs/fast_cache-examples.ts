// Auto-generated usage examples for fast_cache
// Source: generate-api-docs.py

import { MultiTierCache, clear, delete, enable_invalidation, get, get_cache, get_with_fetch, set, stats } from "./fast_cache";

// Create a MultiTierCache instance
const multitiercache = new MultiTierCache(0, 0, undefined as unknown as any, undefined as unknown as any);
multitiercache.clear();
multitiercache.delete("example_key");
multitiercache.enable_invalidation(undefined as unknown as any);
multitiercache.get("example_key");
multitiercache.get_with_fetch("example_key", undefined as unknown as any, undefined as unknown as any);
multitiercache.set("example_key", undefined as unknown as any, undefined as unknown as any);
multitiercache.stats();

// Call clear
clear(undefined as unknown as any);
// Call delete
delete(undefined as unknown as any, "example_key");
// Call enable_invalidation
enable_invalidation(undefined as unknown as any, undefined as unknown as any);
// Call get
get(undefined as unknown as any, "example_key");
// Call get_cache
get_cache(0, 0, undefined as unknown as any, undefined as unknown as any);
// Call get_with_fetch
get_with_fetch(undefined as unknown as any, "example_key", undefined as unknown as any, undefined as unknown as any);
// Call set
set(undefined as unknown as any, "example_key", undefined as unknown as any, undefined as unknown as any);
// Call stats
stats(undefined as unknown as any);
