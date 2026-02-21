// Auto-generated usage examples for shm_context
// Source: generate-api-docs.py

import { ContextSharer, ZeroCopyContext, close, get_context, read_context, release_context, write_context } from "./shm_context";

// Create a ContextSharer instance
const contextsharer = new ContextSharer();
contextsharer.get_context("example_session_id");
contextsharer.release_context("example_session_id");

// Create a ZeroCopyContext instance
const zerocopycontext = new ZeroCopyContext(0);
zerocopycontext.close();
zerocopycontext.read_context(0, 0);
zerocopycontext.write_context(undefined as unknown as Uint8Array, 0);

// Call close
close(undefined as unknown as any);
// Call get_context
get_context(undefined as unknown as any, "example_session_id");
// Call read_context
read_context(undefined as unknown as any, 0, 0);
// Call release_context
release_context(undefined as unknown as any, "example_session_id");
// Call write_context
write_context(undefined as unknown as any, undefined as unknown as Uint8Array, 0);
