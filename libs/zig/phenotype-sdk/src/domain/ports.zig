//! Domain ports - Interfaces defining the boundaries
//!
//! Ports are interfaces defined by the domain (Hexagonal Architecture).
//! They are implemented by adapters in the infrastructure layer.

const std = @import("std");
const ConfigEntry = @import("entities.zig").ConfigEntry;
const FeatureFlag = @import("entities.zig").FeatureFlag;

/// Config repository port interface
/// Implement this to provide storage for configuration entries
pub const ConfigRepository = struct {
    /// Get a configuration entry by key
    get: fn (key: []const u8) anyerror!?ConfigEntry,

    /// Save a configuration entry
    save: fn (entry: ConfigEntry) anyerror!ConfigEntry,

    /// Delete a configuration entry
    delete: fn (key: []const u8) anyerror!bool,

    /// List all entries with optional prefix filter
    list: fn (prefix: ?[]const u8) anyerror!std.array_hash_map.ArrayHashMap([]const u8, ConfigEntry),

    /// Implementation hint: in-memory store
    pub fn inMemory() ConfigRepository {
        return .{
            .get = InMemoryConfigStore.get,
            .save = InMemoryConfigStore.save,
            .delete = InMemoryConfigStore.delete,
            .list = InMemoryConfigStore.list,
        };
    }
};

/// In-memory implementation for testing
const InMemoryConfigStore = struct {
    var entries: std.StringHashMap(ConfigEntry) = .{};
    var arena: std.heap.ArenaAllocator = undefined;

    fn get(key: []const u8) !?ConfigEntry {
        return entries.get(key);
    }

    fn save(entry: ConfigEntry) !ConfigEntry {
        try entries.put(entry.key, entry);
        return entry;
    }

    fn delete(key: []const u8) !bool {
        return entries.remove(key);
    }

    fn list(prefix: ?[]const u8) !std.array_hash_map.ArrayHashMap([]const u8, ConfigEntry) {
        _ = prefix;
        var result = std.array_hash_map.ArrayHashMap([]const u8, ConfigEntry).init(.{});
        var iterator = entries.iterator();
        while (iterator.next()) |entry| {
            try result.put(entry.key_ptr.*, entry.value_ptr.*);
        }
        return result;
    }
};

/// Event publisher port interface
pub const EventPublisher = struct {
    /// Publish configuration created event
    publishCreated: fn (entry: ConfigEntry) anyerror!void,

    /// Publish configuration updated event
    publishUpdated: fn (entry: ConfigEntry) anyerror!void,

    /// Publish configuration deleted event
    publishDeleted: fn (key: []const u8) anyerror!void,

    /// No-op implementation
    pub fn noOp() EventPublisher {
        return .{
            .publishCreated = noOpHandler,
            .publishUpdated = noOpHandler,
            .publishDeleted = noOpKeyHandler,
        };
    }

    fn noOpHandler(_: ConfigEntry) !void {}
    fn noOpKeyHandler(_: []const u8) !void {}
};
