//! API error types.
//!
//! This module contains pure error types for API operations.

use crate::domain::http::StatusCode;
use core::fmt;

/// Error codes for API errors.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ApiErrorCode {
    /// Request timed out
    Timeout,
    /// Connection failed
    ConnectionError,
    /// DNS resolution failed
    DnsError,
    /// TLS error
    TlsError,
    /// Invalid URL
    InvalidUrl,
    /// Request too large
    RequestTooLarge,
    /// Response too large
    ResponseTooLarge,
    /// Serialization error
    SerializationError,
    /// Deserialization error
    DeserializationError,
    /// HTTP error (4xx/5xx)
    HttpError,
    /// Unknown error
    Unknown,
}

impl ApiErrorCode {
    /// Convert to string.
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Timeout => "TIMEOUT",
            Self::ConnectionError => "CONNECTION_ERROR",
            Self::DnsError => "DNS_ERROR",
            Self::TlsError => "TLS_ERROR",
            Self::InvalidUrl => "INVALID_URL",
            Self::RequestTooLarge => "REQUEST_TOO_LARGE",
            Self::ResponseTooLarge => "RESPONSE_TOO_LARGE",
            Self::SerializationError => "SERIALIZATION_ERROR",
            Self::DeserializationError => "DESERIALIZATION_ERROR",
            Self::HttpError => "HTTP_ERROR",
            Self::Unknown => "UNKNOWN",
        }
    }
}

/// API error type.
#[derive(Debug)]
pub struct ApiError {
    code: ApiErrorCode,
    message: String,
    status_code: Option<StatusCode>,
    context: Vec<(String, String)>,
}

impl ApiError {
    /// Create a new API error.
    pub fn new(code: ApiErrorCode, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
            status_code: None,
            context: Vec::new(),
        }
    }

    /// Add context to the error.
    #[must_use]
    pub fn with_context(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.context.push((key.into(), value.into()));
        self
    }

    /// Set HTTP status code.
    #[must_use]
    pub fn with_status(mut self, status: StatusCode) -> Self {
        self.status_code = Some(status);
        self
    }

    /// Get error code.
    pub fn code(&self) -> ApiErrorCode {
        self.code
    }

    /// Get error message.
    pub fn message(&self) -> &str {
        &self.message
    }

    /// Get HTTP status code.
    pub fn status_code(&self) -> Option<StatusCode> {
        self.status_code
    }

    /// Get context.
    pub fn context(&self) -> &[(String, String)] {
        &self.context
    }

    /// Create a timeout error.
    pub fn timeout(url: &str) -> Self {
        Self::new(ApiErrorCode::Timeout, format!("request to {} timed out", url))
    }

    /// Create a connection error.
    pub fn connection_error(url: &str, cause: &str) -> Self {
        Self::new(ApiErrorCode::ConnectionError, format!("failed to connect to {}: {}", url, cause))
    }

    /// Create an invalid URL error.
    pub fn invalid_url(url: &str, reason: &str) -> Self {
        Self::new(ApiErrorCode::InvalidUrl, format!("invalid URL '{}': {}", url, reason))
    }

    /// Create a serialization error.
    pub fn serialization_error(message: &str) -> Self {
        Self::new(ApiErrorCode::SerializationError, message)
    }

    /// Create a deserialization error.
    pub fn deserialization_error(message: &str) -> Self {
        Self::new(ApiErrorCode::DeserializationError, message)
    }

    /// Create an HTTP error from status code.
    pub fn http_error(status: StatusCode, body: Option<&str>) -> Self {
        let message = match body {
            Some(b) if b.len() < 200 => b.to_string(),
            Some(_) => "HTTP error response".to_string(),
            None => format!("HTTP error: {}", status),
        };
        
        Self::new(ApiErrorCode::HttpError, message).with_status(status)
    }
}

impl fmt::Display for ApiError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.code.as_str(), self.message)?;
        if let Some(status) = self.status_code {
            write!(f, " (HTTP {})", status.as_u16())?;
        }
        if !self.context.is_empty() {
            write!(f, " (")?;
            for (i, (k, v)) in self.context.iter().enumerate() {
                if i > 0 {
                    write!(f, ", ")?;
                }
                write!(f, "{}: {}", k, v)?;
            }
            write!(f, ")")?;
        }
        Ok(())
    }
}

impl core::error::Error for ApiError {}

/// Result type for API operations.
pub type ApiResult<T> = Result<T, ApiError>;
