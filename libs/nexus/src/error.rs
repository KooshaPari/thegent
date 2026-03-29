//! Error types for Nexus

use thiserror::Error;

/// Errors that can occur in Nexus operations
#[derive(Debug, Error)]
pub enum NexusError {
    /// Service not found
    #[error("Service not found: {0}")]
    NotFound(String),

    /// Registration failed
    #[error("Failed to register service: {0}")]
    RegistrationFailed(String),

    /// Discovery failed
    #[error("Failed to discover service: {0}")]
    DiscoveryFailed(String),

    /// Invalid configuration
    #[error("Invalid configuration: {0}")]
    InvalidConfig(String),

    /// Internal error
    #[error("Internal error: {0}")]
    Internal(String),
}
