//! LogContext - Domain context for organizing log operations.
//!
//! Pure domain type with no external dependencies.

use std::collections::HashMap;

/// Logging context that holds common fields and service identification.
#[derive(Debug, Clone)]
pub struct LogContext {
    /// Service identifier
    pub service: String,
    /// Common context fields
    pub fields: HashMap<String, String>,
}

impl LogContext {
    /// Create a new logging context with service name.
    pub fn new(service: impl Into<String>) -> Self {
        Self {
            service: service.into(),
            fields: HashMap::new(),
        }
    }

    /// Add a field to the context.
    pub fn with_field(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.fields.insert(key.into(), value.into());
        self
    }
}
