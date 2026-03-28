//! AppError - Main error type for the Phenotype ecosystem.
//!
//! This is the primary error type that should be used throughout
//! the Phenotype ecosystem. It follows best practices for error
//! handling and provides structured error information.

use crate::domain::error_code::ErrorCode;
use std::error::Error;
use std::fmt;

/// Severity level for errors.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
#[non_exhaustive]
pub enum Severity {
    /// Debug information.
    Debug,
    /// Informational.
    Info,
    /// Warning condition.
    Warning,
    /// Error condition.
    Error,
    /// Critical error.
    Critical,
}

impl fmt::Display for Severity {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Debug => write!(f, "DEBUG"),
            Self::Info => write!(f, "INFO"),
            Self::Warning => write!(f, "WARNING"),
            Self::Error => write!(f, "ERROR"),
            Self::Critical => write!(f, "CRITICAL"),
        }
    }
}

impl Default for Severity {
    fn default() -> Self {
        Self::Error
    }
}

/// The main error type for the Phenotype ecosystem.
///
/// # Design Decisions
///
/// - Uses `thiserror` internally for ergonomic error creation
/// - Provides structured context via the `context` field
/// - Supports error chaining via the `source` field
/// - Implements `std::error::Error` for compatibility
///
/// # Example
///
/// ```rust
/// use phenotype_error::{AppError, ErrorCode, Severity};
///
/// let error = AppError::new(ErrorCode::EntityNotFound, "Order not found")
///     .with_context("order_id", "12345")
///     .with_severity(Severity::Warning);
///
/// assert_eq!(error.code(), ErrorCode::EntityNotFound);
/// assert_eq!(error.severity(), Severity::Warning);
/// ```
#[derive(Debug)]
pub struct AppError {
    code: ErrorCode,
    message: String,
    context: std::collections::HashMap<String, serde_json::Value>,
    severity: Severity,
    source: Option<Box<dyn Error + Send + Sync>>,
    location: Option<&'static Location>,
}

impl AppError {
    /// Create a new error.
    ///
    /// # Arguments
    ///
    /// * `code` - The error code
    /// * `message` - A human-readable message
    ///
    /// # Example
    ///
    /// ```rust
    /// use phenotype_error::{AppError, ErrorCode};
    ///
    /// let error = AppError::new(ErrorCode::EntityNotFound, "User not found");
    /// ```
    pub fn new(code: ErrorCode, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
            context: std::collections::HashMap::new(),
            severity: Severity::default(),
            source: None,
            location: None,
        }
    }

    /// Create a new error with a source error.
    ///
    /// # Arguments
    ///
    /// * `code` - The error code
    /// * `message` - A human-readable message
    /// * `source` - The source error
    ///
    /// # Example
    ///
    /// ```rust
    /// use phenotype_error::{AppError, ErrorCode};
    /// use std::io;
    ///
    /// fn read_config() -> Result<(), AppError> {
    ///     let file = std::fs::File::open("config.toml")
    ///         .map_err(|e| AppError::with_source(
    ///             ErrorCode::ConfigurationError,
    ///             "Failed to open config",
    ///             e,
    ///         ))?;
    ///     Ok(())
    /// }
    /// ```
    pub fn with_source<E>(code: ErrorCode, message: impl Into<String>, source: E) -> Self
    where
        E: Error + Send + Sync + 'static,
    {
        Self {
            code,
            message: message.into(),
            context: std::collections::HashMap::new(),
            severity: Severity::default(),
            source: Some(Box::new(source)),
            location: None,
        }
    }

    /// Get the error code.
    pub fn code(&self) -> ErrorCode {
        self.code
    }

    /// Get the error message.
    pub fn message(&self) -> &str {
        &self.message
    }

    /// Get the error severity.
    pub fn severity(&self) -> Severity {
        self.severity
    }

    /// Get the error context.
    pub fn context(&self) -> &std::collections::HashMap<String, serde_json::Value> {
        &self.context
    }

    /// Get the source error, if any.
    pub fn source_error(&self) -> Option<&(dyn Error + Send + Sync + 'static)> {
        self.source.as_ref().map(|e| e.as_ref() as _)
    }

    /// Add context to the error.
    ///
    /// # Example
    ///
    /// ```rust
    /// use phenotype_error::{AppError, ErrorCode};
    ///
    /// let error = AppError::new(ErrorCode::ValidationError, "Invalid input")
    ///     .with_context("field", "email")
    ///     .with_context("value", "not-an-email");
    /// ```
    pub fn with_context(mut self, key: impl Into<String>, value: impl serde::Serialize) -> Self {
        self.context.insert(
            key.into(),
            serde_json::to_value(value).unwrap_or(serde_json::Value::Null),
        );
        self
    }

    /// Set the severity.
    pub fn with_severity(mut self, severity: Severity) -> Self {
        self.severity = severity;
        self
    }

    /// Check if this is a client error (4xx).
    pub fn is_client_error(&self) -> bool {
        self.code.code() >= 2000 && self.code.code() < 3000
    }

    /// Check if this is a server error (5xx).
    pub fn is_server_error(&self) -> bool {
        self.code.code() >= 4000 && self.code.code() < 5000
    }

    /// Convert to JSON value.
    #[cfg(feature = "serde")]
    pub fn to_json(&self) -> serde_json::Value {
        serde_json::json!({
            "code": self.code.to_string(),
            "message": self.message,
            "context": self.context,
            "severity": self.severity.to_string(),
        })
    }
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{:?}] {}", self.code, self.message)?;
        if !self.context.is_empty() {
            write!(f, " ({:?})", self.context)?;
        }
        Ok(())
    }
}

impl Error for AppError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        self.source.as_ref().map(|e| e.as_ref() as _)
    }
}

/// Location in source code where error was created.
#[derive(Debug, Clone, Copy)]
struct Location {
    file: &'static str,
    line: u32,
    column: u32,
}

impl fmt::Display for Location {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}:{}:{}", self.file, self.line, self.column)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_creation() {
        let error = AppError::new(ErrorCode::EntityNotFound, "User not found");
        assert_eq!(error.code(), ErrorCode::EntityNotFound);
        assert_eq!(error.message(), "User not found");
        assert_eq!(error.severity(), Severity::Error);
    }

    #[test]
    fn test_error_with_context() {
        let error = AppError::new(ErrorCode::ValidationError, "Invalid email")
            .with_context("field", "email")
            .with_context("value", "test@example");

        assert_eq!(error.context().len(), 2);
    }

    #[test]
    fn test_error_display() {
        let error = AppError::new(ErrorCode::Timeout, "Connection timed out");
        let display = format!("{}", error);
        assert!(display.contains("Timeout"));
        assert!(display.contains("Connection timed out"));
    }

    #[test]
    fn test_error_source() {
        use std::io;

        let source = io::Error::new(io::ErrorKind::NotFound, "file not found");
        let error = AppError::with_source(
            ErrorCode::DatabaseError,
            "Failed to open database",
            source,
        );

        assert!(error.source_error().is_some());
    }
}
