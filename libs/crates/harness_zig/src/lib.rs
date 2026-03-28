//! # harness_zig - Zig Harness for heliosCLI
//!
//! Provides Zig integration for the harness system

/// Zig harness configuration
pub struct ZigConfig {
    pub version: String,
    pub path: Option<String>,
}

impl ZigConfig {
    pub fn new() -> Self {
        Self {
            version: "0.13".to_string(),
            path: None,
        }
    }
}

impl Default for ZigConfig {
    fn default() -> Self {
        Self::new()
    }
}
