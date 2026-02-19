/// Error types for Supermemory client operations.
use thiserror::Error;

#[derive(Error, Debug)]
pub enum SupermemoryError {
    #[error("HTTP error: {status} {message}")]
    HttpError { status: u16, message: String },

    #[error("Authentication failed: {0}")]
    AuthError(String),

    #[error("Invalid API key format")]
    InvalidApiKey,

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("Serialization error: {0}")]
    SerdeError(#[from] serde_json::Error),

    #[error("Request error: {0}")]
    RequestError(#[from] reqwest::Error),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Missing required field: {0}")]
    MissingField(String),

    #[error("Invalid response format: {0}")]
    InvalidResponse(String),

    #[error("Timeout: request took too long")]
    Timeout,

    #[error("Resource not found: {0}")]
    NotFound(String),

    #[error("Server error: {message}")]
    ServerError { code: String, message: String },

    #[error("Unknown error: {0}")]
    Unknown(String),
}

pub type Result<T> = std::result::Result<T, SupermemoryError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let err = SupermemoryError::InvalidApiKey;
        assert_eq!(err.to_string(), "Invalid API key format");
    }

    #[test]
    fn test_http_error() {
        let err = SupermemoryError::HttpError {
            status: 404,
            message: "Not found".to_string(),
        };
        assert!(err.to_string().contains("404"));
    }
}
