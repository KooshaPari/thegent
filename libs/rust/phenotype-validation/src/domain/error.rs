//! Validation error types.

use std::fmt;

/// Validation error - represents a validation failure.
#[derive(Debug, Clone)]
pub struct ValidationError {
    pub field: String,
    pub message: String,
    pub code: String,
    pub context: std::collections::HashMap<String, String>,
}

impl ValidationError {
    /// Create a new validation error.
    pub fn new(field: &str, code: &str, message: &str) -> Self {
        Self {
            field: field.to_string(),
            code: code.to_string(),
            message: message.to_string(),
            context: std::collections::HashMap::new(),
        }
    }

    /// Add context to the error.
    pub fn with_context(mut self, key: &str, value: &str) -> Self {
        self.context.insert(key.to_string(), value.to_string());
        self
    }

    /// Get the formatted error message.
    pub fn formatted(&self) -> String {
        if self.context.is_empty() {
            format!("{}: {}", self.field, self.message)
        } else {
            let ctx: Vec<String> = self.context
                .iter()
                .map(|(k, v)| format!("{}={}", k, v))
                .collect();
            format!("{}: {} ({})", self.field, self.message, ctx.join(", "))
        }
    }
}

impl fmt::Display for ValidationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.formatted())
    }
}

impl std::error::Error for ValidationError {}
