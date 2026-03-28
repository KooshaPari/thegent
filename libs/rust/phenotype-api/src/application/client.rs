//! HTTP client for API requests.
//!
//! This module provides a simple HTTP client following hexagonal architecture.

use crate::domain::{ApiError, ApiResult, Request, Response, http::StatusCode};

/// HTTP client trait for sending requests.
///
/// This trait abstracts over the underlying HTTP implementation,
/// allowing for different adapters (reqwest, isahc, etc.).
pub trait HttpClient: Send + Sync {
    /// Send an HTTP request.
    fn send(&self, request: &Request) -> impl std::future::Future<Output = ApiResult<Response>> + Send;
}

/// API client for making HTTP requests.
#[derive(Debug, Clone)]
pub struct ApiClient {
    default_headers: Vec<(String, String)>,
    default_timeout_ms: Option<u64>,
}

impl ApiClient {
    /// Create a new API client.
    pub fn new() -> Self {
        Self {
            default_headers: Vec::new(),
            default_timeout_ms: Some(30_000), // 30 seconds
        }
    }

    /// Set default timeout.
    pub fn timeout(mut self, ms: u64) -> Self {
        self.default_timeout_ms = Some(ms);
        self
    }

    /// Add a default header.
    pub fn header(mut self, name: impl Into<String>, value: impl Into<String>) -> Self {
        self.default_headers.push((name.into(), value.into()));
        self
    }

    /// Add authorization header.
    pub fn auth(self, token: impl Into<String>) -> Self {
        self.header("Authorization", format!("Bearer {}", token.into()))
    }

    /// Send a GET request.
    pub async fn get(&self, url: &str) -> ApiResult<Response> {
        self.send(Request::get(url)).await
    }

    /// Send a POST request.
    pub async fn post(&self, url: &str, body: Option<&str>) -> ApiResult<Response> {
        let mut req = Request::post(url);
        if let Some(b) = body {
            req = req.body(b);
        }
        self.send(req).await
    }

    /// Send a PUT request.
    pub async fn put(&self, url: &str, body: Option<&str>) -> ApiResult<Response> {
        let mut req = Request::put(url);
        if let Some(b) = body {
            req = req.body(b);
        }
        self.send(req).await
    }

    /// Send a DELETE request.
    pub async fn delete(&self, url: &str) -> ApiResult<Response> {
        self.send(Request::delete(url)).await
    }

    /// Send a request.
    pub async fn send(&self, request: Request) -> ApiResult<Response> {
        #[cfg(feature = "reqwest")]
        {
            self.send_with_reqwest(&request).await
        }

        #[cfg(not(feature = "reqwest"))]
        {
            Err(ApiError::new(
                crate::domain::ApiErrorCode::Unknown,
                "no HTTP client available (enable reqwest feature)"
            ))
        }
    }

    #[cfg(feature = "reqwest")]
    async fn send_with_reqwest(&self, request: &Request) -> ApiResult<Response> {
        use reqwest::header::{HeaderMap, HeaderName, HeaderValue};
        use std::time::Duration;

        let client = reqwest::Client::builder()
            .timeout(Duration::from_millis(self.default_timeout_ms.unwrap_or(30_000)))
            .build()
            .map_err(|e| ApiError::connection_error(request.url(), &e.to_string()))?;

        let mut req_builder = client.request(
            reqwest::Method::from_bytes(request.method().as_str().as_bytes()).unwrap(),
            request.url(),
        );

        // Add default headers
        for (name, value) in &self.default_headers {
            req_builder = req_builder.header(name.as_str(), value.as_str());
        }

        // Add request headers
        for header in request.headers() {
            req_builder = req_builder.header(header.name(), header.value());
        }

        // Add query params
        if !request.query_params().is_empty() {
            let mut query = vec![];
            for param in request.query_params() {
                query.push((param.name.as_str(), param.value.as_str()));
            }
            req_builder = req_builder.query(&query);
        }

        // Add body
        if let Some(body) = request.body() {
            req_builder = req_builder.body(body.to_string());
        }

        // Add timeout
        if let Some(timeout) = request.timeout_ms().or(self.default_timeout_ms) {
            req_builder = req_builder.timeout(Duration::from_millis(timeout));
        }

        let response = req_builder.send().await
            .map_err(|e| {
                if e.is_timeout() {
                    ApiError::timeout(request.url())
                } else if e.is_connect() {
                    ApiError::connection_error(request.url(), &e.to_string())
                } else {
                    ApiError::new(crate::domain::ApiErrorCode::ConnectionError, e.to_string())
                }
            })?;

        let status = StatusCode::from_u16(response.status().as_u16());
        let headers: Vec<(String, String)> = response.headers()
            .iter()
            .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
            .collect();
        let body = response.text().await
            .map_err(|e| ApiError::new(crate::domain::ApiErrorCode::Unknown, e.to_string()))?;

        let resp = Response::new(status, headers, body);

        // Return error for non-success status codes
        if !status.is_success() {
            return Err(ApiError::http_error(status, Some(&resp.body)));
        }

        Ok(resp)
    }
}

impl Default for ApiClient {
    fn default() -> Self {
        Self::new()
    }
}
