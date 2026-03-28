//! Common error types for the AgilePlus P2P crate.

/// Error type for connection and database operations.
#[derive(Debug, thiserror::Error)]
pub enum ConnectionError {
    #[error("Connection failed: {0}")]
    ConnectionFailed(String),

    #[error("Database error: {0}")]
    DatabaseError(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}
