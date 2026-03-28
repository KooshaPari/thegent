//! Repository error types.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies (except async-trait)

use thiserror::Error;

/// Result type for storage operations.
pub type StorageResult<T> = Result<T, RepositoryError>;

/// Errors that can occur during repository operations.
#[derive(Debug, Error)]
pub enum RepositoryError {
    #[error("Entity not found: {entity_type} with id `{entity_id}`")]
    NotFound {
        entity_type: String,
        entity_id: String,
    },

    #[error("Entity already exists: {entity_type} with id `{entity_id}`")]
    AlreadyExists {
        entity_type: String,
        entity_id: String,
    },

    #[error("Optimistic locking conflict: expected version {expected}, actual {actual}")]
    OptimisticLockConflict {
        expected: u64,
        actual: u64,
    },

    #[error("Validation error: {message}")]
    ValidationError { message: String },

    #[error("Connection error: {message}")]
    ConnectionError { message: String },

    #[error("Transaction error: {message}")]
    TransactionError { message: String },

    #[error("Serialization error: {message}")]
    SerializationError { message: String },

    #[error("Repository error: {message}")]
    InternalError { message: String },
}

impl RepositoryError {
    /// Create a NotFound error.
    pub fn not_found<E: Into<String>>(entity_type: E, entity_id: &str) -> Self {
        RepositoryError::NotFound {
            entity_type: entity_type.into(),
            entity_id: entity_id.to_string(),
        }
    }

    /// Create an AlreadyExists error.
    pub fn already_exists<E: Into<String>>(entity_type: E, entity_id: &str) -> Self {
        RepositoryError::AlreadyExists {
            entity_type: entity_type.into(),
            entity_id: entity_id.to_string(),
        }
    }

    /// Create an OptimisticLockConflict error.
    pub fn optimistic_lock_conflict(expected: u64, actual: u64) -> Self {
        RepositoryError::OptimisticLockConflict { expected, actual }
    }
}
