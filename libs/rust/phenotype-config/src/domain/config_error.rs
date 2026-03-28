//! Configuration error types.
//!
//! This module contains pure domain error types.
//! No external dependencies allowed in this module.

use core::fmt;

/// Error codes for configuration errors.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ConfigErrorCode {
    /// Key not found in configuration
    KeyNotFound,
    /// Invalid type conversion
    TypeMismatch,
    /// Parse error
    ParseError,
    /// Validation error
    ValidationError,
    /// IO error (file not found, permission denied)
    IoError,
    /// Unknown error
    Unknown,
}

impl ConfigErrorCode {
    /// Convert to string representation.
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::KeyNotFound => "KEY_NOT_FOUND",
            Self::TypeMismatch => "TYPE_MISMATCH",
            Self::ParseError => "PARSE_ERROR",
            Self::ValidationError => "VALIDATION_ERROR",
            Self::IoError => "IO_ERROR",
            Self::Unknown => "UNKNOWN",
        }
    }
}

/// Configuration error type.
#[derive(Debug)]
pub struct ConfigError {
    code: ConfigErrorCode,
    message: String,
    context: Vec<(String, String)>,
}

impl ConfigError {
    /// Create a new configuration error.
    pub fn new(code: ConfigErrorCode, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
            context: Vec::new(),
        }
    }

    /// Add context to the error.
    #[must_use]
    pub fn with_context(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.context.push((key.into(), value.into()));
        self
    }

    /// Get the error code.
    pub fn code(&self) -> ConfigErrorCode {
        self.code
    }

    /// Get the error message.
    pub fn message(&self) -> &str {
        &self.message
    }

    /// Get the error context.
    pub fn context(&self) -> &[(String, String)] {
        &self.context
    }

    /// Create a key not found error.
    pub fn key_not_found(key: impl Into<String>) -> Self {
        Self::new(ConfigErrorCode::KeyNotFound, format!("configuration key not found: {}", key.into()))
    }

    /// Create a type mismatch error.
    pub fn type_mismatch(expected: &str, actual: &str, key: &str) -> Self {
        Self::new(
            ConfigErrorCode::TypeMismatch,
            format!(
                "type mismatch for key '{}': expected {}, got {}",
                key, expected, actual
            ),
        )
    }

    /// Create a parse error.
    pub fn parse_error(message: impl Into<String>, value: &str) -> Self {
        Self::new(ConfigErrorCode::ParseError, message.into())
            .with_context("value", value)
    }

    /// Create a validation error.
    pub fn validation_error(message: impl Into<String>) -> Self {
        Self::new(ConfigErrorCode::ValidationError, message)
    }
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.code.as_str(), self.message)?;
        if !self.context.is_empty() {
            write!(f, " (")?;
            for (i, (k, v)) in self.context.iter().enumerate() {
                if i > 0 {
                    write!(f, ", ")?;
                }
                write!(f, "{}: {}", k, v)?;
            }
            write!(f, ")")?;
        }
        Ok(())
    }
}

impl core::error::Error for ConfigError {}

/// Result type for configuration operations.
pub type ConfigResult<T> = Result<T, ConfigError>;
