//! Error kinds - Categories of errors.
//!
//! Error kinds provide a higher-level categorization
//! that can be used for control flow and error handling.

use std::fmt;

/// Error kinds for categorizing errors.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum ErrorKind {
    /// Validation errors.
    Validation,
    /// Not found errors.
    NotFound,
    /// Conflict errors.
    Conflict,
    /// Permission errors.
    Permission,
    /// Timeout errors.
    Timeout,
    /// Network errors.
    Network,
    /// Database errors.
    Database,
    /// External service errors.
    ExternalService,
    /// Internal errors.
    Internal,
}

impl ErrorKind {
    /// Check if error should be retried.
    pub fn is_retryable(&self) -> bool {
        matches!(
            self,
            Self::Network | Self::Timeout | Self::ExternalService | Self::Database
        )
    }

    /// Check if error is client error.
    pub fn is_client_error(&self) -> bool {
        matches!(
            self,
            Self::Validation | Self::NotFound | Self::Conflict | Self::Permission
        )
    }

    /// Check if error is server error.
    pub fn is_server_error(&self) -> bool {
        matches!(
            self,
            Self::Network | Self::Timeout | Self::Database | Self::ExternalService | Self::Internal
        )
    }
}

impl fmt::Display for ErrorKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Validation => write!(f, "validation"),
            Self::NotFound => write!(f, "not_found"),
            Self::Conflict => write!(f, "conflict"),
            Self::Permission => write!(f, "permission"),
            Self::Timeout => write!(f, "timeout"),
            Self::Network => write!(f, "network"),
            Self::Database => write!(f, "database"),
            Self::ExternalService => write!(f, "external_service"),
            Self::Internal => write!(f, "internal"),
        }
    }
}

impl Default for ErrorKind {
    fn default() -> Self {
        Self::Internal
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_retryable() {
        assert!(ErrorKind::Network.is_retryable());
        assert!(ErrorKind::Timeout.is_retryable());
        assert!(!ErrorKind::Validation.is_retryable());
        assert!(!ErrorKind::Permission.is_retryable());
    }

    #[test]
    fn test_is_client_error() {
        assert!(ErrorKind::Validation.is_client_error());
        assert!(ErrorKind::NotFound.is_client_error());
        assert!(!ErrorKind::Internal.is_client_error());
    }
}
