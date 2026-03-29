// Auto-generated usage examples for context
// Source: generate-api-docs.py

import { ContextCompressor, generate_continuity_packet, prune_context, should_compress } from "./context";

// Create a ContextCompressor instance
const contextcompressor = new ContextCompressor("example_session_dir", 0);
contextcompressor.generate_continuity_packet("example_intent", undefined as unknown as Array<string>, undefined as unknown as Array<string>, undefined as unknown as Array<string>);
contextcompressor.prune_context(undefined as unknown as Array<Record<(str, Any)>>);
contextcompressor.should_compress(0, 0);

// Call generate_continuity_packet
generate_continuity_packet(undefined as unknown as any, "example_intent", undefined as unknown as Array<string>, undefined as unknown as Array<string>, undefined as unknown as Array<string>);
// Call prune_context
prune_context(undefined as unknown as any, undefined as unknown as Array<Record<(str, Any)>>);
// Call should_compress
should_compress(undefined as unknown as any, 0, 0);
