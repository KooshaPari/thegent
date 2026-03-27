//! LogEntry - A single structured log entry in the domain layer.
//!
//! Pure domain type with no external dependencies.

use super::LogLevel;
use std::collections::HashMap;

/// A single structured log entry containing message and context.
#[derive(Debug, Clone)]
pub struct LogEntry {
    /// Log message
    pub message: String,
    /// Log severity level
    pub level: LogLevel,
    /// Key-value context fields
    pub fields: HashMap<String, String>,
}

impl LogEntry {
    /// Create a new log entry with message and level.
    pub fn new(message: impl Into<String>, level: LogLevel) -> Self {
        Self {
            message: message.into(),
            level,
            fields: HashMap::new(),
        }
    }

    /// Add a context field to the entry.
    pub fn with_field(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.fields.insert(key.into(), value.into());
        self
    }
}
