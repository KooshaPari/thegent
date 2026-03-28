//! # Phenotype Config
//!
//! Core domain for Phenotype's configuration management platform.
//!
//! This crate contains the pure domain logic for configuration management:
//! - Configuration entries with versioning
//! - Namespace organization
//! - Value type validation
//! - Feature flag support
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                    APPLICATION LAYER                         │
//! │  ConfigUseCases, ConfigCommands, ConfigQueries              │
//! └─────────────────────────────────────────────────────────────┘
//!                              │
//!                              ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │                      DOMAIN LAYER                           │
//! │  ConfigEntry, Namespace, ValueType, ConfigValue             │
//! └─────────────────────────────────────────────────────────────┘
//!                              │
//!                              ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │                    PORTS (INTERFACES)                        │
//! │  ConfigRepository, ConfigEventPublisher, ConfigCache         │
//! └─────────────────────────────────────────────────────────────┘
//! ```

#![forbid(unsafe_code)]
#![warn(missing_docs)]
#![deny(clippy::all)]

pub mod domain;
pub mod application;
pub mod ports;

pub use domain::*;
pub use application::*;
pub use ports::*;

/// Result type for config operations
pub type ConfigResult<T> = Result<T, ConfigError>;

/// Configuration error
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("Entry not found: {0}")]
    NotFound(String),

    #[error("Entry already exists: {0}")]
    AlreadyExists(String),

    #[error("Invalid key: {0}")]
    InvalidKey(String),

    #[error("Invalid value for type {value_type}: {message}")]
    InvalidValue { value_type: String, message: String },

    #[error("Version conflict: expected {expected}, found {found}")]
    VersionConflict { expected: u32, found: u32 },

    #[error("Namespace error: {0}")]
    Namespace(String),

    #[error("Permission denied: {0}")]
    PermissionDenied(String),

    #[error("Serialization error: {0}")]
    Serialization(String),

    #[error("Internal error: {0}")]
    Internal(String),
}

impl From<helix_errors::Error> for ConfigError {
    fn from(err: helix_errors::Error) -> Self {
        ConfigError::Internal(err.message().to_string())
    }
}
