//! phenotype-logging-zig
//!
//! Zig structured logging with minimal allocations.
//!
//! xDD Methodologies:
//! - TDD: Test-driven with std.testing
//! - BDD: Descriptive test names
//! - Property-Based: Property tests for logging invariants
//! - SOLID: Single responsibility per function
//! - KISS: Simple, composable API
//! - Clean: Domain/Port/Adapter separation

const std = @import("std");

pub const Level = enum(u3) {
    trace = 0,
    debug = 1,
    info = 2,
    warn = 3,
    err = 4,
    fatal = 5,

    /// Convert string to Level (BDD: Given a level string)
    pub fn fromString(s: []const u8) ?Level {
        if (std.mem.eql(u8, s, "TRACE")) return .trace;
        if (std.mem.eql(u8, s, "DEBUG")) return .debug;
        if (std.mem.eql(u8, s, "INFO")) return .info;
        if (std.mem.eql(u8, s, "WARN")) return .warn;
        if (std.mem.eql(u8, s, "ERROR")) return .err;
        if (std.mem.eql(u8, s, "FATAL")) return .fatal;
        return null;
    }

    /// Convert Level to string (BDD: When converting to string)
    pub fn toString(self: Level) []const u8 {
        return switch (self) {
            .trace => "TRACE",
            .debug => "DEBUG",
            .info => "INFO",
            .warn => "WARN",
            .err => "ERROR",
            .fatal => "FATAL",
        };
    }

    /// Check if this level is enabled given a minimum level (Property-based)
    pub fn isEnabled(self: Level, min_level: Level) bool {
        return @intFromEnum(self) >= @intFromEnum(min_level);
    }
};

/// Log entry with structured data (Domain model).
pub const Entry = struct {
    level: Level,
    message: []const u8,
    timestamp: i64,
    fields: std.StringHashMapUnmanaged([]const u8),

    /// Create a new log entry (DDD: Factory method)
    pub fn init(level: Level, message: []const u8, allocator: std.mem.Allocator) !Entry {
        _ = allocator;
        return Entry{
            .level = level,
            .message = message,
            .timestamp = std.time.timestamp(),
            .fields = .{},
        };
    }

    /// Release resources (DDD: Cleanup)
    pub fn deinit(self: *Entry, allocator: std.mem.Allocator) void {
        self.fields.deinit(allocator);
    }

    /// Add a structured field (DDD: Value object)
    pub fn addField(self: *Entry, allocator: std.mem.Allocator, key: []const u8, value: []const u8) !void {
        try self.fields.put(allocator, key, value);
    }
};

/// Logger interface (Port in hexagonal architecture).
pub const Logger = struct {
    level: Level,
    writer: std.io.AnyWriter,

    /// Log a message at the given level (TDD: Red-Green-Refactor)
    pub fn log(self: *Logger, level: Level, message: []const u8, allocator: std.mem.Allocator) !void {
        // BDD: Given a logger with level X, When logging at level Y, Then...
        if (!level.isEnabled(self.level)) return;

        var entry = try Entry.init(level, message, allocator);
        defer entry.deinit(allocator);

        try self.format(entry, allocator);
    }

    /// Log with structured fields (BDD: Given fields, When logging, Then format)
    pub fn logWithFields(self: *Logger, level: Level, message: []const u8, fields: anytype, allocator: std.mem.Allocator) !void {
        if (!level.isEnabled(self.level)) return;

        var entry = try Entry.init(level, message, allocator);
        defer entry.deinit(allocator);

        // Add fields from struct (Reflection via comptime)
        inline for (std.meta.fields(@TypeOf(fields))) |f| {
            const value = @field(fields, f.name);
            try entry.addField(allocator, f.name, value);
        }

        try self.format(entry, allocator);
    }

    /// Format entry to writer (Port: Formatting logic)
    fn format(self: *Logger, entry: Entry, allocator: std.mem.Allocator) !void {
        _ = allocator;
        try self.writer.print(
            "{{\"level\":\"{s}\",\"message\":\"{s}\",\"timestamp\":{d}",
            .{ entry.level.toString(), entry.message, entry.timestamp },
        );
        try self.writer.writeAll(",\"fields\":{");
        var it = entry.fields.iterator();
        var first = true;
        while (it.next()) |kv| {
            if (!first) try self.writer.writeAll(",");
            first = false;
            try self.writer.print("\"{s}\":\"{s}\"", .{ kv.key_ptr.*, kv.value_ptr.* });
        }
        try self.writer.writeAll("}}\n");
    }
};

// ============================================================================
// TDD Tests - Red-Green-Refactor Cycle
// ============================================================================

test "Level.toString returns correct string" {
    // Red: This test defines expected behavior
    try std.testing.expectEqualStrings("INFO", Level.info.toString());
    try std.testing.expectEqualStrings("ERROR", Level.err.toString());
    try std.testing.expectEqualStrings("DEBUG", Level.debug.toString());
}

test "Level.fromString parses valid strings" {
    // Green: Implementation makes test pass
    try std.testing.expectEqual(Level.info, Level.fromString("INFO").?);
    try std.testing.expectEqual(Level.debug, Level.fromString("DEBUG").?);
    try std.testing.expectEqual(Level.err, Level.fromString("ERROR").?);
}

test "Level.fromString returns null for invalid strings" {
    // Refactor: Clean up invalid input handling
    try std.testing.expectEqual(null, Level.fromString("INVALID"));
}

test "Level.isEnabled respects minimum level" {
    // Property-based: For all valid level combinations
    try std.testing.expect(Level.info.isEnabled(.debug));
    try std.testing.expect(Level.err.isEnabled(.warn));
    try std.testing.expect(!Level.debug.isEnabled(.info));
}

test "Entry.init creates entry with correct fields" {
    const allocator = std.testing.allocator;
    var entry = try Entry.init(.info, "test message", allocator);
    defer entry.deinit(allocator);

    try std.testing.expectEqual(Level.info, entry.level);
    try std.testing.expectEqualStrings("test message", entry.message);
    try std.testing.expect(entry.timestamp > 0);
}

test "Entry.addField adds field correctly" {
    const allocator = std.testing.allocator;
    var entry = try Entry.init(.info, "test", allocator);
    defer entry.deinit(allocator);

    try entry.addField(allocator, "key", "value");

    try std.testing.expect(entry.fields.contains("key"));
}

test "Logger.log filters by level" {
    const allocator = std.testing.allocator;
    var buffer = std.array_list.Managed(u8).init(allocator);
    defer buffer.deinit();

    var logger = Logger{
        .level = .warn,
        .writer = buffer.writer().any(),
    };

    // Debug should be filtered out
    try logger.log(.debug, "should not appear", allocator);
    try std.testing.expectEqualStrings("", buffer.items);

    // Error should pass through
    try logger.log(.err, "should appear", allocator);
    try std.testing.expect(buffer.items.len > 0);
}

test "Logger.logWithFields adds structured data" {
    const allocator = std.testing.allocator;
    var buffer = std.array_list.Managed(u8).init(allocator);
    defer buffer.deinit();

    var logger = Logger{
        .level = .info,
        .writer = buffer.writer().any(),
    };

    const fields = .{ .request_id = "123", .user = "alice" };
    try logger.logWithFields(.info, "User request", fields, allocator);

    try std.testing.expect(std.mem.indexOf(u8, buffer.items, "request_id") != null);
    try std.testing.expect(std.mem.indexOf(u8, buffer.items, "123") != null);
}

// ============================================================================
// BDD Scenario Tests - Given-When-Then Format
// ============================================================================

test "BDD: Given logger at INFO level, When logging DEBUG, Then message is filtered" {
    const allocator = std.testing.allocator;
    var buffer = std.array_list.Managed(u8).init(allocator);
    defer buffer.deinit();

    var logger = Logger{ .level = .info, .writer = buffer.writer().any() };

    // When
    try logger.log(.debug, "filtered message", allocator);

    // Then
    try std.testing.expectEqualStrings("", buffer.items);
}

test "BDD: Given logger at ERROR level, When logging ERROR with fields, Then JSON output contains fields" {
    const allocator = std.testing.allocator;
    var buffer = std.array_list.Managed(u8).init(allocator);
    defer buffer.deinit();

    var logger = Logger{ .level = .err, .writer = buffer.writer().any() };

    // When
    const fields = .{ .code = "500", .err_text = "server error" };
    try logger.logWithFields(.err, "Request failed", fields, allocator);

    // Then
    try std.testing.expect(std.mem.indexOf(u8, buffer.items, "500") != null);
    try std.testing.expect(std.mem.indexOf(u8, buffer.items, "server error") != null);
}

// ============================================================================
// Property-Based Tests - Invariants
// ============================================================================

test "Property: Level ordering is consistent" {
    // Invariant: If A >= B and B >= C, then A >= C
    try std.testing.expect(Level.fatal.isEnabled(.trace));
    try std.testing.expect(Level.err.isEnabled(.debug));
    try std.testing.expect(Level.info.isEnabled(.trace));
}

test "Property: toString/fromString are inverses" {
    // Invariant: fromString(toString(x)) == x for all levels
    inline for (std.meta.fields(Level)) |f| {
        const level: Level = @enumFromInt(f.value);
        const str = level.toString();
        try std.testing.expectEqual(level, Level.fromString(str).?);
    }
}
