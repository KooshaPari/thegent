// Auto-generated usage examples for edge_sync
// Source: generate-api-docs.py

import { EdgeSyncController, apply_remote_delta, compute_delta, get_adaptive_polling_interval } from "./edge_sync";

// Create a EdgeSyncController instance
const edgesynccontroller = new EdgeSyncController("example_device_id");
edgesynccontroller.apply_remote_delta(undefined as unknown as Uint8Array);
edgesynccontroller.compute_delta(undefined as unknown as Record<(str, Any)>);
edgesynccontroller.get_adaptive_polling_interval(0);

// Call apply_remote_delta
apply_remote_delta(undefined as unknown as any, undefined as unknown as Uint8Array);
// Call compute_delta
compute_delta(undefined as unknown as any, undefined as unknown as Record<(str, Any)>);
// Call get_adaptive_polling_interval
get_adaptive_polling_interval(undefined as unknown as any, 0);
