//! Error types for ports

use thiserror::Error;

/// Port-related errors
#[derive(Debug, Error)]
pub enum PortError {
    /// Indicates a port operation is not yet implemented
    #[error("Port not implemented: {0}")]
    NotImplemented(String),

    /// Indicates a port configuration error
    #[error("Port configuration error: {0}")]
    Configuration(String),

    /// Indicates a port initialization error
    #[error("Port initialization error: {0}")]
    Initialization(String),

    /// Indicates a port validation error
    #[error("Port validation error: {0}")]
    Validation(String),
}
