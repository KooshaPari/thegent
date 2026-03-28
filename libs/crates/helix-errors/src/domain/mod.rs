//! Domain layer - Pure error types with no external dependencies
//!
//! This module contains the core error types that form the domain of error handling.

#[cfg(not(feature = "std"))]
use alloc::{string::{String, ToString}, vec::Vec, boxed::Box, format};
#[cfg(feature = "std")]
use std::string::{String, ToString};
#[cfg(feature = "std")]
use std::vec::Vec;
#[cfg(feature = "std")]
use std::boxed::Box;
#[cfg(feature = "std")]
use std::error::Error as StdError;
use std::fmt;

/// Error kind categorization
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum ErrorKind {
    /// Validation failed
    Validation,
    /// Input was invalid
    InvalidInput,
    /// Resource not found
    NotFound,
    /// Resource already exists
    AlreadyExists,
    /// Permission denied
    PermissionDenied,
    /// Operation timed out
    Timeout,
    /// Resource exhausted (rate limit, quota, etc.)
    ResourceExhausted,
    /// Internal error
    Internal,
    /// Configuration error
    Configuration,
    /// Serialization error
    Serialization,
    /// Network error
    Network,
    /// Database error
    Database,
    /// Authentication error
    Authentication,
    /// Authorization error
    Authorization,
    /// Unknown/custom error
    Unknown,
}

impl ErrorKind {
    /// Get the error code as a string
    pub fn code(&self) -> &'static str {
        match self {
            ErrorKind::Validation => "VALIDATION_ERROR",
            ErrorKind::InvalidInput => "INVALID_INPUT",
            ErrorKind::NotFound => "NOT_FOUND",
            ErrorKind::AlreadyExists => "ALREADY_EXISTS",
            ErrorKind::PermissionDenied => "PERMISSION_DENIED",
            ErrorKind::Timeout => "TIMEOUT",
            ErrorKind::ResourceExhausted => "RESOURCE_EXHAUSTED",
            ErrorKind::Internal => "INTERNAL_ERROR",
            ErrorKind::Configuration => "CONFIGURATION_ERROR",
            ErrorKind::Serialization => "SERIALIZATION_ERROR",
            ErrorKind::Network => "NETWORK_ERROR",
            ErrorKind::Database => "DATABASE_ERROR",
            ErrorKind::Authentication => "AUTHENTICATION_ERROR",
            ErrorKind::Authorization => "AUTHORIZATION_ERROR",
            ErrorKind::Unknown => "UNKNOWN_ERROR",
        }
    }

    /// HTTP status code mapping (for API integration)
    #[cfg(feature = "std")]
    pub fn http_status(&self) -> u16 {
        match self {
            ErrorKind::Validation | ErrorKind::InvalidInput => 400,
            ErrorKind::NotFound => 404,
            ErrorKind::PermissionDenied => 403,
            ErrorKind::Timeout => 408,
            ErrorKind::ResourceExhausted => 429,
            ErrorKind::Authentication => 401,
            ErrorKind::Authorization => 403,
            ErrorKind::Internal | ErrorKind::Database | ErrorKind::Configuration => 500,
            ErrorKind::Serialization | ErrorKind::Network => 502,
            ErrorKind::AlreadyExists => 409,
            ErrorKind::Unknown => 500,
        }
    }
}

/// Core error type
#[derive(Debug)]
pub struct Error {
    pub(crate) kind: ErrorKind,
    pub(crate) message: String,
    pub(crate) context_entries: Vec<ContextEntry>,
    pub(crate) source: Option<Box<dyn StdError + Send + Sync>>,
    pub(crate) backtrace: Option<String>,
}

impl Clone for Error {
    fn clone(&self) -> Self {
        Self {
            kind: self.kind,
            message: self.message.clone(),
            context_entries: self.context_entries.clone(),
            source: None, // Cannot clone the source error
            backtrace: self.backtrace.clone(),
        }
    }
}

impl Error {
    /// Create a new error with kind and message
    pub fn new(kind: ErrorKind, message: impl Into<String>) -> Self {
        Self {
            kind,
            message: message.into(),
            context_entries: Vec::new(),
            source: None,
            backtrace: None,
        }
    }

    /// Create an error with formatted message
    pub fn fmt(kind: ErrorKind, format: fmt::Arguments<'_>) -> Self {
        Self::new(kind, format.to_string())
    }

    /// Add context to the error (builder pattern)
    pub fn with_context<C: Into<ContextValue>>(mut self, key: impl Into<String>, value: C) -> Self {
        self.context_entries.push(ContextEntry {
            key: key.into(),
            value: value.into(),
        });
        self
    }

    /// Add a source error
    pub fn cause<E: StdError + Send + Sync + 'static>(mut self, source: E) -> Self {
        self.source = Some(Box::new(source));
        self
    }

    /// Add a backtrace (if std feature enabled)
    #[cfg(feature = "std")]
    pub fn with_backtrace(mut self) -> Self {
        use std::backtrace::Backtrace;
        self.backtrace = Some(Backtrace::capture().to_string());
        self
    }

    /// Get the error kind
    pub fn kind(&self) -> ErrorKind {
        self.kind
    }

    /// Get the error message
    pub fn message(&self) -> &str {
        &self.message
    }

    /// Get the error code
    pub fn code(&self) -> &'static str {
        self.kind.code()
    }

    /// Get context entries
    pub fn context(&self) -> &[ContextEntry] {
        &self.context_entries
    }

    /// Get the source error if present
    pub fn error_source(&self) -> Option<&(dyn StdError + Send + Sync)> {
        self.source.as_ref().map(|e| e.as_ref())
    }

    // Convenience constructors

    /// Create a validation error
    pub fn validation(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Validation, msg)
    }

    /// Create an invalid input error
    pub fn invalid_input(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::InvalidInput, msg)
    }

    /// Create a not found error
    pub fn not_found(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::NotFound, msg)
    }

    /// Create an already exists error
    pub fn already_exists(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::AlreadyExists, msg)
    }

    /// Create an internal error
    pub fn internal(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Internal, msg)
    }

    /// Create a configuration error
    pub fn configuration(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Configuration, msg)
    }

    /// Create a network error
    pub fn network(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Network, msg)
    }

    /// Create a database error
    pub fn database(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Database, msg)
    }

    /// Create a timeout error
    pub fn timeout(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Timeout, msg)
    }

    /// Create an authentication error
    pub fn authentication(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Authentication, msg)
    }

    /// Create an authorization error
    pub fn authorization(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Authorization, msg)
    }

    /// Create a permission denied error
    pub fn permission_denied(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::PermissionDenied, msg)
    }

    /// Create a serialization error
    pub fn serialization(msg: impl Into<String>) -> Self {
        Self::new(ErrorKind::Serialization, msg)
    }
}

/// Context entry for error
#[derive(Debug, Clone, PartialEq)]
pub struct ContextEntry {
    /// Context key
    pub key: String,
    /// Context value
    pub value: ContextValue,
}

/// Context value types
#[derive(Debug, Clone, PartialEq)]
pub enum ContextValue {
    /// String value
    String(String),
    /// Signed integer value
    Int(i64),
    /// Unsigned integer value
    UInt(u64),
    /// Floating point value
    Float(f64),
    /// Boolean value
    Bool(bool),
    /// JSON string value
    Json(String),
}

impl From<&str> for ContextValue {
    fn from(s: &str) -> Self {
        ContextValue::String(s.to_string())
    }
}

impl From<String> for ContextValue {
    fn from(s: String) -> Self {
        ContextValue::String(s)
    }
}

impl From<i32> for ContextValue {
    fn from(n: i32) -> Self {
        ContextValue::Int(n as i64)
    }
}

impl From<i64> for ContextValue {
    fn from(n: i64) -> Self {
        ContextValue::Int(n)
    }
}

impl From<u64> for ContextValue {
    fn from(n: u64) -> Self {
        ContextValue::UInt(n)
    }
}

impl From<f64> for ContextValue {
    fn from(n: f64) -> Self {
        ContextValue::Float(n)
    }
}

impl From<bool> for ContextValue {
    fn from(b: bool) -> Self {
        ContextValue::Bool(b)
    }
}

/// Trait for converting values into errors
pub trait IntoError {
    /// Convert into an error
    fn into_error(self) -> Error;
}

impl IntoError for Error {
    fn into_error(self) -> Error {
        self
    }
}

impl IntoError for &str {
    fn into_error(self) -> Error {
        Error::internal(self)
    }
}

impl IntoError for String {
    fn into_error(self) -> Error {
        Error::internal(self)
    }
}

// Conversion from standard error traits
#[cfg(feature = "std")]
impl From<std::io::Error> for Error {
    fn from(err: std::io::Error) -> Self {
        match err.kind() {
            std::io::ErrorKind::NotFound => Error::not_found(err.to_string()),
            std::io::ErrorKind::PermissionDenied => Error::permission_denied(err.to_string()),
            std::io::ErrorKind::AlreadyExists => Error::already_exists(err.to_string()),
            std::io::ErrorKind::TimedOut => Error::timeout(err.to_string()),
            _ => Error::internal(err.to_string()),
        }
    }
}

#[cfg(feature = "std")]
impl From<std::fmt::Error> for Error {
    fn from(err: std::fmt::Error) -> Self {
        Error::internal(err.to_string())
    }
}

#[cfg(feature = "serde")]
impl From<serde_json::Error> for Error {
    fn from(err: serde_json::Error) -> Self {
        Error::serialization(err.to_string())
    }
}
