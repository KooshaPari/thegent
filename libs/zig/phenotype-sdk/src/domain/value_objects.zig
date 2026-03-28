//! Domain value objects - Immutable types representing specific values
//!
//! Value objects are characterized by their attributes, not identity.
//! They are immutable and validated at construction time (DDD Value Object).

const std = @import("std");
const ValueType = @import("entities.zig").ValueType;

/// A validated configuration value
pub const ConfigValue = struct {
    raw: []const u8,
    value_type: ValueType,

    /// Create a validated ConfigValue
    pub fn create(raw: []const u8, value_type: ValueType) !ConfigValue {
        // Type validation
        switch (value_type) {
            .string => {},
            .integer => _ = try std.fmt.parseInt(i64, raw, 10),
            .float => _ = try std.fmt.parseFloat(f64, raw),
            .boolean => {
                if (!std.mem.eql(u8, raw, "true") and !std.mem.eql(u8, raw, "false")) {
                    return error.InvalidBoolean;
                }
            },
            .json => {
                // Basic JSON validation (would use json parser in production)
                if (raw.len < 2 or raw[0] != '{' and raw[0] != '[') {
                    return error.InvalidJson;
                }
            },
            .secret => {},
        }

        return ConfigValue{ .raw = raw, .value_type = value_type };
    }

    /// Get the typed value
    pub fn asTyped(self: *const ConfigValue, allocator: std.mem.Allocator) ![]const u8 {
        return try allocator.dupe(u8, self.raw);
    }
};

/// Result type for SDK operations (Railway-oriented programming)
pub const Result = union(enum) {
    ok: []const u8,
    err: []const u8,

    pub fn isOk(self: *const Result) bool {
        return self.* == .ok;
    }

    pub fn isErr(self: *const Result) bool {
        return self.* == .err;
    }

    pub fn unwrap(self: *Result) []const u8 {
        return switch (self.*) {
            .ok => |v| v,
            .err => @panic("unwrap on err"),
        };
    }
};

test "ConfigValue: type validation" {
    const testing = std.testing;

    // Valid values
    try testing.expect((try ConfigValue.create("hello", .string)).value_type == .string);
    try testing.expect((try ConfigValue.create("42", .integer)).value_type == .integer);
    try testing.expect((try ConfigValue.create("3.14", .float)).value_type == .float);
    try testing.expect((try ConfigValue.create("true", .boolean)).value_type == .boolean);

    // Invalid values should fail
    try testing.expectError(error.InvalidBoolean, ConfigValue.create("yes", .boolean));
    try testing.expectError(error.InvalidJson, ConfigValue.create("invalid", .json));
}
