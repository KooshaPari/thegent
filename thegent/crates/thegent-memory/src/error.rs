//! Error types for Supermemory client
//!
//! Unified error types from both supermemory-rs and thegent-memory implementations.

use thiserror::Error;

/// Result type for supermemory operations
pub type Result<T> = std::result::Result<T, Error>;

/// Error type for supermemory client (merged from both crates)
#[derive(Error, Debug)]
pub enum Error {
    // thegent-memory errors
    #[error("HTTP request failed: {0}")]
    HttpError(#[from] reqwest::Error),

    #[error("Authentication failed: {0}")]
    AuthenticationError(String),

    #[error("Invalid API key format")]
    InvalidApiKey,

    #[error("Invalid project ID: {0}")]
    InvalidProject(String),

    #[error("Query failed: {0}")]
    QueryError(String),

    #[error("Document storage failed: {0}")]
    StorageError(String),

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("Invalid argument: {0}")]
    InvalidArgument(String),

    #[error("Circuit breaker open")]
    CircuitBreakerOpen,

    #[error("Request timeout")]
    Timeout,

    #[error("Rate limited")]
    RateLimited,

    #[error("Internal error: {0}")]
    Internal(String),

    // supermemory-rs specific errors
    #[error("HTTP error: {status} {message}")]
    HttpStatusError { status: u16, message: String },

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Missing required field: {0}")]
    MissingField(String),

    #[error("Invalid response format: {0}")]
    InvalidResponse(String),

    #[error("Resource not found: {0}")]
    NotFound(String),

    #[error("Server error: {message}")]
    ServerError { code: String, message: String },

    #[error("Unknown error: {0}")]
    Unknown(String),
}

impl Error {
    /// Check if error is retryable
    pub fn is_retryable(&self) -> bool {
        matches!(
            self,
            Error::RateLimited | Error::Timeout | Error::Internal(_)
        )
    }

    /// Check if error is a temporary failure
    pub fn is_temporary(&self) -> bool {
        match self {
            Error::HttpError(e) => e.is_timeout() || e.is_connect(),
            _ => self.is_retryable(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let err = Error::InvalidApiKey;
        assert_eq!(err.to_string(), "Invalid API key format");
    }

    #[test]
    fn test_http_status_error() {
        let err = Error::HttpStatusError {
            status: 404,
            message: "Not found".to_string(),
        };
        assert!(err.to_string().contains("404"));
    }

    #[test]
    fn test_is_retryable() {
        assert!(Error::RateLimited.is_retryable());
        assert!(Error::Timeout.is_retryable());
        assert!(!Error::InvalidApiKey.is_retryable());
    }
}
