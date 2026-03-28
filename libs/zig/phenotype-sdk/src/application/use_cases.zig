//! Application use cases - Orchestration of domain logic
//!
//! Use cases coordinate domain objects and ports (Application Service pattern).
//! They handle cross-cutting concerns like validation and event publishing.

const std = @import("std");
const ConfigEntry = @import("domain/entities.zig").ConfigEntry;
const FeatureFlag = @import("domain/entities.zig").FeatureFlag;
const ConfigRepository = @import("domain/ports.zig").ConfigRepository;
const EventPublisher = @import("domain/ports.zig").EventPublisher;
const ValueType = @import("domain/entities.zig").ValueType;
const ConfigValue = @import("domain/value_objects.zig").ConfigValue;

/// Data transfer objects
pub const DTO = struct {
    pub const CreateConfig = struct {
        key: []const u8,
        value: []const u8,
        value_type: ValueType,
    };

    pub const UpdateConfig = struct {
        key: []const u8,
        value: []const u8,
    };

    pub const ConfigResponse = struct {
        id: []const u8,
        key: []const u8,
        value: []const u8,
        value_type: ValueType,
        version: u32,
    };
};

/// Configuration use cases
pub const ConfigUseCases = struct {
    repository: ConfigRepository,
    publisher: EventPublisher,
    allocator: std.mem.Allocator,

    /// Create a new configuration entry
    pub fn create(self: *ConfigUseCases, dto: DTO.CreateConfig) !ConfigEntry {
        // Validate
        if (dto.key.len == 0) return error.EmptyKey;

        // Check for existing
        if (try self.repository.get(dto.key)) |_| {
            return error.KeyExists;
        }

        // Create validated value
        _ = try ConfigValue.create(dto.value, dto.value_type);

        // Create entry
        var entry = try ConfigEntry.create(dto.key, dto.value, dto.value_type, self.allocator);

        // Persist
        entry = try self.repository.save(entry);

        // Publish event
        try self.publisher.publishCreated(entry);

        return entry;
    }

    /// Update an existing configuration entry
    pub fn update(self: *ConfigUseCases, dto: DTO.UpdateConfig) !ConfigEntry {
        const existing = try self.repository.get(dto.key) orelse return error.NotFound;

        // Create new version
        var updated = existing.withValue(dto.value);

        // Persist
        updated = try self.repository.save(updated);

        // Publish event
        try self.publisher.publishUpdated(updated);

        return updated;
    }

    /// Get a configuration entry
    pub fn get(self: *ConfigUseCases, key: []const u8) !ConfigEntry {
        return self.repository.get(key) orelse return error.NotFound;
    }

    /// Delete a configuration entry
    pub fn delete(self: *ConfigUseCases, key: []const u8) !void {
        const deleted = try self.repository.delete(key);
        if (!deleted) return error.NotFound;
        try self.publisher.publishDeleted(key);
    }
};
