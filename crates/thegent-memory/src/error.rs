//! Error types for Supermemory client

use thiserror::Error;

/// Result type for supermemory operations
pub type Result<T> = std::result::Result<T, Error>;

/// Error type for supermemory client
#[derive(Error, Debug)]
pub enum Error {
    #[error("HTTP request failed: {0}")]
    HttpError(#[from] reqwest::Error),

    #[error("Authentication failed: {0}")]
    AuthenticationError(String),

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
