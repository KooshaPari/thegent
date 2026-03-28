//! HTTP response types.
//!
//! This module contains pure response types for API operations.

use crate::domain::http::StatusCode;
use core::fmt;

/// HTTP response.
#[derive(Debug)]
pub struct Response {
    status: StatusCode,
    headers: Vec<(String, String)>,
    body: String,
}

impl Response {
    /// Create a new response.
    pub fn new(status: StatusCode, headers: Vec<(String, String)>, body: String) -> Self {
        Self {
            status,
            headers,
            body,
        }
    }

    /// Get status code.
    pub fn status(&self) -> StatusCode {
        self.status
    }

    /// Get headers.
    pub fn headers(&self) -> &[(String, String)] {
        &self.headers
    }

    /// Get body.
    pub fn body(&self) -> &str {
        &self.body
    }

    /// Get body as bytes.
    pub fn body_bytes(&self) -> &[u8] {
        self.body.as_bytes()
    }

    /// Check if status is success.
    pub fn is_success(&self) -> bool {
        self.status.is_success()
    }

    /// Check if status is client error.
    pub fn is_client_error(&self) -> bool {
        self.status.is_client_error()
    }

    /// Check if status is server error.
    pub fn is_server_error(&self) -> bool {
        self.status.is_server_error()
    }

    /// Get a header value.
    pub fn header(&self, name: &str) -> Option<&str> {
        self.headers.iter()
            .find(|(n, _)| n.eq_ignore_ascii_case(name))
            .map(|(_, v)| v.as_str())
    }

    /// Get content type.
    pub fn content_type(&self) -> Option<&str> {
        self.header("content-type")
    }

    /// Parse body as JSON.
    pub fn json<T: serde::de::DeserializeOwned>(&self) -> Result<T, serde_json::Error> {
        serde_json::from_str(&self.body)
    }

    /// Parse body as JSON or return default.
    pub fn json_or<T: serde::de::DeserializeOwned + Default>(&self) -> T {
        self.json().unwrap_or_default()
    }
}

impl fmt::Display for Response {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} - {} bytes", self.status, self.body.len())
    }
}
