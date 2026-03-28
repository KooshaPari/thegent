//! Application DTOs - Data transfer objects for API boundaries

pub const ConfigEntryDTO = struct {
    id: []const u8,
    key: []const u8,
    value: []const u8,
    value_type: []const u8,
    version: u32,
};

pub const FeatureFlagDTO = struct {
    id: []const u8,
    key: []const u8,
    enabled: bool,
    rollout_percentage: f64,
};
