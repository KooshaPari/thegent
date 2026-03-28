const std = @import("std");

/// SDK version
pub const version = "0.1.0";

/// Domain layer - Pure business logic
pub const domain = struct {
    pub usingnamespace @import("domain/entities.zig");
    pub usingnamespace @import("domain/value_objects.zig");
    pub usingnamespace @import("domain/ports.zig");
};

/// Application layer - Use cases
pub const application = struct {
    pub usingnamespace @import("application/use_cases.zig");
    pub usingnamespace @import("application/dto.zig");
};

/// Adapters layer - Infrastructure
pub const adapters = struct {
    pub usingnamespace @import("adapters/outbound/http_client.zig");
    pub usingnamespace @import("adapters/outbound/memory_store.zig");
};

test "phenotype-sdk: basic integration" {
    // Test module loads correctly
    try std.testing.expect(version.len > 0);
}
