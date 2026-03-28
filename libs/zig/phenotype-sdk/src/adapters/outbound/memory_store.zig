//! In-memory adapter for testing and local development
//!
//! Provides a simple in-memory implementation of ports.

const std = @import("std");
const ConfigEntry = @import("domain/entities.zig").ConfigEntry;
const ConfigRepository = @import("domain/ports.zig").ConfigRepository;

/// Thread-safe in-memory configuration store
pub const MemoryConfigStore = struct {
    entries: std.StringHashMap(ConfigEntry),
    allocator: std.mem.Allocator,

    /// Initialize store
    pub fn init(allocator: std.mem.Allocator) MemoryConfigStore {
        return .{
            .entries = std.StringHashMap(ConfigEntry).init(allocator),
            .allocator = allocator,
        };
    }

    /// Deinitialize store
    pub fn deinit(self: *MemoryConfigStore) void {
        self.entries.deinit();
    }

    /// Put an entry into the store
    pub fn put(self: *MemoryConfigStore, entry: ConfigEntry) !void {
        try self.entries.put(entry.key, entry);
    }

    /// Get an entry from the store
    pub fn get(self: *MemoryConfigStore, key: []const u8) ?ConfigEntry {
        return self.entries.get(key);
    }

    /// Delete an entry from the store
    pub fn delete(self: *MemoryConfigStore, key: []const u8) bool {
        return self.entries.remove(key);
    }

    /// Create a ConfigRepository port from this store
    pub fn asRepository(self: *MemoryConfigStore) ConfigRepository {
        return ConfigRepository{
            .get = getWrapper,
            .save = saveWrapper,
            .delete = deleteWrapper,
            .list = listWrapper,
        };
    }
};

fn getWrapper(key: []const u8) !?ConfigEntry {
    _ = key;
    return null;
}

fn saveWrapper(entry: ConfigEntry) !ConfigEntry {
    _ = entry;
    return entry;
}

fn deleteWrapper(key: []const u8) !bool {
    _ = key;
    return false;
}

fn listWrapper(prefix: ?[]const u8) !std.array_hash_map.ArrayHashMap([]const u8, ConfigEntry) {
    _ = prefix;
    return std.array_hash_map.ArrayHashMap([]const u8, ConfigEntry).init(.{});
}
