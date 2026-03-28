//! Domain entities - Core business objects
//!
//! These entities are pure domain logic with no external dependencies.
//! Following Hexagonal Architecture: Domain is the innermost layer.

const std = @import("std");
const uuid = @import("uuid");

/// Value type enumeration for configuration entries
pub const ValueType = enum(u8) {
    string = 0,
    integer = 1,
    float = 2,
    boolean = 3,
    json = 4,
    secret = 5,
};

/// Configuration entry entity
/// Immutable once created (DDD: Entity with value semantics)
pub const ConfigEntry = struct {
    id: []const u8,
    key: []const u8,
    value: []const u8,
    value_type: ValueType,
    version: u32,
    created_at: i64,
    updated_at: i64,
    metadata: std.StringHashMap([]const u8),

    /// Create a new ConfigEntry
    pub fn create(
        key: []const u8,
        value: []const u8,
        value_type: ValueType,
        allocator: std.mem.Allocator,
    ) !ConfigEntry {
        if (key.len == 0) return error.EmptyKey;

        const now = std.time.timestamp();
        var metadata = std.StringHashMap([]const u8).init(allocator);
        errdefer metadata.deinit();

        return ConfigEntry{
            .id = try uuid.v4().toString(allocator),
            .key = key,
            .value = value,
            .value_type = value_type,
            .version = 1,
            .created_at = now,
            .updated_at = now,
            .metadata = metadata,
        };
    }

    /// Create a new version with updated value (immutable update pattern)
    pub fn withValue(self: *const ConfigEntry, new_value: []const u8) ConfigEntry {
        return ConfigEntry{
            .id = self.id,
            .key = self.key,
            .value = new_value,
            .value_type = self.value_type,
            .version = self.version + 1,
            .created_at = self.created_at,
            .updated_at = std.time.timestamp(),
            .metadata = self.metadata,
        };
    }
};

/// Feature flag entity
pub const FeatureFlag = struct {
    id: []const u8,
    key: []const u8,
    enabled: bool,
    rollout_percentage: f64,
    targeting_rules: []const []const u8, // JSON strings
    created_at: i64,
    updated_at: i64,

    /// Create a new FeatureFlag
    pub fn create(key: []const u8, enabled: bool, rollout_percentage: f64, allocator: std.mem.Allocator) !FeatureFlag {
        if (key.len == 0) return error.EmptyKey;
        if (rollout_percentage < 0 or rollout_percentage > 100) return error.InvalidPercentage;

        return FeatureFlag{
            .id = try uuid.v4().toString(allocator),
            .key = key,
            .enabled = enabled,
            .rollout_percentage = rollout_percentage,
            .targeting_rules = &.{},
            .created_at = std.time.timestamp(),
            .updated_at = std.time.timestamp(),
        };
    }

    /// Check if feature is enabled for a user (consistent hashing for rollout)
    pub fn isEnabled(self: *const FeatureFlag, user_id: []const u8) bool {
        if (!self.enabled) return false;

        // Consistent hashing for stable percentage assignment
        const hash = std.hash.Fnv1a_64.hash(std.fmt.comptimePrint("{s}:{s}", .{ self.key, user_id }));
        const bucket = @mod(@abs(@as(i64, @intCast(hash))), 100);
        return @intToFloat(f64, bucket) < self.rollout_percentage;
    }
};

test "ConfigEntry: creation and validation" {
    const testing = std.testing;
    const allocator = testing.allocator;

    // Valid entry
    const entry = try ConfigEntry.create("database.host", "localhost", .string, allocator);
    defer allocator.free(entry.id);
    try testing.expect(entry.version == 1);
    try testing.expect(entry.key.len > 0);

    // Empty key should fail
    try testing.expectError(error.EmptyKey, ConfigEntry.create("", "value", .string, allocator));
}

test "FeatureFlag: percentage rollout" {
    const testing = std.testing;
    const allocator = testing.allocator;

    var flag = try FeatureFlag.create("test-feature", true, 100.0, allocator);
    defer allocator.free(flag.id);

    // 100% rollout should always return true
    try testing.expect(flag.isEnabled("user-123"));
    try testing.expect(flag.isEnabled("user-456"));
}
