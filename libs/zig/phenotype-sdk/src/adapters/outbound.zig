//! Outbound adapters - Infrastructure implementations
//!
//! Adapters implement the domain ports using external systems.
//! Following Hexagonal Architecture, they are the outermost layer.

pub const http_client = @import("http_client.zig");
pub const memory_store = @import("memory_store.zig");
