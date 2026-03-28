//! HTTP request types.
//!
//! This module contains pure request types for API operations.

use crate::domain::http::{HttpMethod, MediaType};
use core::fmt;

/// HTTP header.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Header {
    name: String,
    value: String,
}

impl Header {
    /// Create a new header.
    pub fn new(name: impl Into<String>, value: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            value: value.into(),
        }
    }

    /// Get header name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Get header value.
    pub fn value(&self) -> &str {
        &self.value
    }
}

/// Query parameter.
#[derive(Debug, Clone)]
pub struct QueryParam {
    name: String,
    value: String,
}

impl QueryParam {
    /// Create a new query parameter.
    pub fn new(name: impl Into<String>, value: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            value: value.into(),
        }
    }
}

/// HTTP request builder.
#[derive(Debug, Default)]
pub struct Request {
    method: HttpMethod,
    url: String,
    headers: Vec<Header>,
    query_params: Vec<QueryParam>,
    body: Option<String>,
    timeout_ms: Option<u64>,
}

impl Request {
    /// Create a new request.
    pub fn new(method: HttpMethod, url: impl Into<String>) -> Self {
        Self {
            method,
            url: url.into(),
            ..Default::default()
        }
    }

    /// Create a GET request.
    pub fn get(url: impl Into<String>) -> Self {
        Self::new(HttpMethod::Get, url)
    }

    /// Create a POST request.
    pub fn post(url: impl Into<String>) -> Self {
        Self::new(HttpMethod::Post, url)
    }

    /// Create a PUT request.
    pub fn put(url: impl Into<String>) -> Self {
        Self::new(HttpMethod::Put, url)
    }

    /// Create a PATCH request.
    pub fn patch(url: impl Into<String>) -> Self {
        Self::new(HttpMethod::Patch, url)
    }

    /// Create a DELETE request.
    pub fn delete(url: impl Into<String>) -> Self {
        Self::new(HttpMethod::Delete, url)
    }

    /// Set the URL.
    pub fn url(mut self, url: impl Into<String>) -> Self {
        self.url = url.into();
        self
    }

    /// Add a header.
    pub fn header(mut self, name: impl Into<String>, value: impl Into<String>) -> Self {
        self.headers.push(Header::new(name, value));
        self
    }

    /// Add content type header.
    pub fn content_type(mut self, media_type: MediaType) -> Self {
        self.headers.push(Header::new("Content-Type", media_type.as_content_type()));
        self
    }

    /// Add authorization header.
    pub fn authorization(mut self, token: impl Into<String>) -> Self {
        self.headers.push(Header::new("Authorization", format!("Bearer {}", token.into())));
        self
    }

    /// Add a query parameter.
    pub fn query_param(mut self, name: impl Into<String>, value: impl Into<String>) -> Self {
        self.query_params.push(QueryParam::new(name, value));
        self
    }

    /// Set request body.
    pub fn body(mut self, body: impl Into<String>) -> Self {
        self.body = Some(body.into());
        self
    }

    /// Set JSON body.
    pub fn json<T: serde::Serialize>(mut self, value: &T) -> Result<Self, serde_json::Error> {
        let json = serde_json::to_string(value)?;
        self.body = Some(json);
        self.headers.push(Header::new("Content-Type", "application/json"));
        Ok(self)
    }

    /// Set timeout.
    pub fn timeout(mut self, ms: u64) -> Self {
        self.timeout_ms = Some(ms);
        self
    }

    /// Get HTTP method.
    pub fn method(&self) -> HttpMethod {
        self.method
    }

    /// Get URL.
    pub fn url(&self) -> &str {
        &self.url
    }

    /// Get headers.
    pub fn headers(&self) -> &[Header] {
        &self.headers
    }

    /// Get query params.
    pub fn query_params(&self) -> &[QueryParam] {
        &self.query_params
    }

    /// Get body.
    pub fn body(&self) -> Option<&str> {
        self.body.as_deref()
    }

    /// Get timeout.
    pub fn timeout_ms(&self) -> Option<u64> {
        self.timeout_ms
    }
}

impl fmt::Display for Request {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} {}", self.method, self.url)?;
        if !self.query_params.is_empty() {
            let params: Vec<_> = self.query_params.iter()
                .map(|p| format!("{}={}", p.name, p.value))
                .collect();
            write!(f, "?{}", params.join("&"))?;
        }
        Ok(())
    }
}
