//! Cache errors - Pure domain error types.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies

use thiserror::Error;

/// Cache error types.
#[derive(Debug, Error)]
pub enum CacheError {
    #[error("key not found: {key}")]
    KeyNotFound { key: String },

    #[error("key already exists: {key}")]
    KeyAlreadyExists { key: String },

    #[error("cache is full, cannot add more entries")]
    CacheFull,

    #[error("entry expired: {key}")]
    EntryExpired { key: String },

    #[error("serialization error: {message}")]
    SerializationError { message: String },

    #[error("deserialization error: {message}")]
    DeserializationError { message: String },

    #[error("invalid key: {key}")]
    InvalidKey { key: String },

    #[error("invalid TTL: {ttl}")]
    InvalidTtl { ttl: i64 },

    #[error("operation not supported: {operation}")]
    OperationNotSupported { operation: String },

    #[error("cache is closed")]
    CacheClosed,
}

/// Result type alias for cache operations.
pub type Result<T> = std::result::Result<T, CacheError>;
