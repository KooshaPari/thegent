//! Error builder - Fluent builder for errors.
//!
//! This module provides a builder pattern for creating errors
//! with additional context.

use crate::domain::app_error::{AppError, Severity};
use crate::domain::error_code::ErrorCode;

/// Builder for creating errors with fluent API.
#[derive(Debug)]
pub struct ErrorBuilder {
    code: ErrorCode,
    message: String,
    severity: Severity,
    context: Vec<(&'static str, serde_json::Value)>,
}

impl ErrorBuilder {
    /// Create a new builder.
    pub fn new(code: ErrorCode, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
            severity: Severity::Error,
            context: Vec::new(),
        }
    }

    /// Set severity.
    pub fn severity(mut self, severity: Severity) -> Self {
        self.severity = severity;
        self
    }

    /// Add a context field.
    pub fn context<T: serde::Serialize>(mut self, key: &'static str, value: T) -> Self {
        self.context.push((
            key,
            serde_json::to_value(value).unwrap_or(serde_json::Value::Null),
        ));
        self
    }

    /// Add multiple context fields from a struct.
    pub fn context_from<T: serde::Serialize + std::fmt::Debug>(mut self, data: &T) -> Self {
        if let Ok(json) = serde_json::to_value(data) {
            if let Some(obj) = json.as_object() {
                for (k, v) in obj {
                    self.context.push((Box::leak(k.clone().into_boxed_str()) as &str, v.clone()));
                }
            }
        }
        self
    }

    /// Build the error.
    pub fn build(self) -> AppError {
        let mut error = AppError::new(self.code, self.message).with_severity(self.severity);
        for (key, value) in self.context {
            error = error.with_context(key, value);
        }
        error
    }
}

/// Helper function to create errors quickly.
pub fn error(code: ErrorCode, message: impl Into<String>) -> ErrorBuilder {
    ErrorBuilder::new(code, message)
}

/// Validation error helper.
pub fn validation_error(field: &str, message: &str) -> AppError {
    error(crate::domain::ErrorCode::ValidationError, message)
        .context("field", field)
        .build()
}

/// Not found error helper.
pub fn not_found(entity: &str, id: &str) -> AppError {
    error(crate::domain::ErrorCode::EntityNotFound, format!("{} not found", entity))
        .context("entity_type", entity)
        .context("entity_id", id)
        .build()
}

/// Business rule violation helper.
pub fn business_rule(rule: &str, details: &str) -> AppError {
    error(crate::domain::ErrorCode::BusinessRuleViolation, format!("Rule violated: {}", rule))
        .context("rule", rule)
        .context("details", details)
        .build()
}

/// Configuration error helper.
pub fn configuration_error(key: &str, message: &str) -> AppError {
    error(crate::domain::ErrorCode::ConfigurationError, message)
        .context("config_key", key)
        .build()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_builder() {
        let error = error(ErrorCode::EntityNotFound, "User not found")
            .severity(Severity::Warning)
            .context("user_id", "123")
            .context("reason", "deleted")
            .build();

        assert_eq!(error.code(), ErrorCode::EntityNotFound);
        assert_eq!(error.severity(), Severity::Warning);
        assert!(!error.context().is_empty());
    }

    #[test]
    fn test_validation_error() {
        let error = validation_error("email", "Invalid format");
        assert_eq!(error.code(), ErrorCode::ValidationError);
    }

    #[test]
    fn test_not_found() {
        let error = not_found("Order", "456");
        assert_eq!(error.code(), ErrorCode::EntityNotFound);
    }
}
