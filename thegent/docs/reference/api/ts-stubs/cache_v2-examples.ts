// Auto-generated usage examples for cache_v2
// Source: generate-api-docs.py

import { CacheInvalidator, CacheV2, CrossProcessSingleflight, Handler, HeatBasedLRU, Singleflight, do, get, on_modified, put, stop, watch } from "./cache_v2";

// Create a CacheInvalidator instance
const cacheinvalidator = new CacheInvalidator(undefined as unknown as any);
cacheinvalidator.stop();
cacheinvalidator.watch("example_directory");

// Create a CacheV2 instance
const cachev2 = new CacheV2("example_root", "example_namespace");

// Create a CrossProcessSingleflight instance
const crossprocesssingleflight = new CrossProcessSingleflight("example_coordination_dir");
crossprocesssingleflight.do("example_key", undefined as unknown as Callable<(Any, Any)>, 0);

// Create a Handler instance
const handler = new Handler(undefined as unknown as any);
handler.on_modified(undefined as unknown as any);

// Create a HeatBasedLRU instance
const heatbasedlru = new HeatBasedLRU(0, 0);
heatbasedlru.get("example_key");
heatbasedlru.put("example_key", undefined as unknown as any);

// Create a Singleflight instance
const singleflight = new Singleflight();
singleflight.do("example_key", undefined as unknown as Callable<(Any, Any)>);

// Call do
do(undefined as unknown as any, "example_key", undefined as unknown as Callable<(Any, Any)>, 0);
// Call get
get(undefined as unknown as any, "example_key");
// Call on_modified
on_modified(undefined as unknown as any, undefined as unknown as any);
// Call put
put(undefined as unknown as any, "example_key", undefined as unknown as any);
// Call stop
stop(undefined as unknown as any);
// Call watch
watch(undefined as unknown as any, "example_directory");
