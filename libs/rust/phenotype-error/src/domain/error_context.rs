//! Error context - Additional context for errors.
//!
//! This module provides utilities for adding context to errors
//! and propagating errors through the call stack.

use crate::domain::app_error::AppError;
use crate::domain::error_code::ErrorCode;

/// Error context for adding additional information.
#[derive(Debug, Clone)]
pub struct ErrorContext {
    /// Request ID.
    pub request_id: Option<String>,
    /// User ID.
    pub user_id: Option<String>,
    /// Session ID.
    pub session_id: Option<String>,
    /// Trace ID.
    pub trace_id: Option<String>,
    /// Span ID.
    pub span_id: Option<String>,
    /// Additional metadata.
    pub metadata: std::collections::HashMap<String, String>,
}

impl ErrorContext {
    /// Create a new empty context.
    pub fn new() -> Self {
        Self {
            request_id: None,
            user_id: None,
            session_id: None,
            trace_id: None,
            span_id: None,
            metadata: std::collections::HashMap::new(),
        }
    }

    /// Set the request ID.
    pub fn with_request_id(mut self, request_id: impl Into<String>) -> Self {
        self.request_id = Some(request_id.into());
        self
    }

    /// Set the user ID.
    pub fn with_user_id(mut self, user_id: impl Into<String>) -> Self {
        self.user_id = Some(user_id.into());
        self
    }

    /// Set the session ID.
    pub fn with_session_id(mut self, session_id: impl Into<String>) -> Self {
        self.session_id = Some(session_id.into());
        self
    }

    /// Set the trace ID.
    pub fn with_trace_id(mut self, trace_id: impl Into<String>) -> Self {
        self.trace_id = Some(trace_id.into());
        self
    }

    /// Set the span ID.
    pub fn with_span_id(mut self, span_id: impl Into<String>) -> Self {
        self.span_id = Some(span_id.into());
        self
    }

    /// Add a metadata key-value pair.
    pub fn with_metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }

    /// Apply context to an error.
    pub fn apply_to(&self, error: AppError) -> AppError {
        let mut error = error;
        
        if let Some(ref request_id) = self.request_id {
            error = error.with_context("request_id", request_id);
        }
        if let Some(ref user_id) = self.user_id {
            error = error.with_context("user_id", user_id);
        }
        if let Some(ref session_id) = self.session_id {
            error = error.with_context("session_id", session_id);
        }
        if let Some(ref trace_id) = self.trace_id {
            error = error.with_context("trace_id", trace_id);
        }
        if let Some(ref span_id) = self.span_id {
            error = error.with_context("span_id", span_id);
        }
        
        for (key, value) in &self.metadata {
            error = error.with_context(key.as_str(), value);
        }
        
        error
    }
}

impl Default for ErrorContext {
    fn default() -> Self {
        Self::new()
    }
}

impl From<ErrorContext> for AppError {
    fn from(ctx: ErrorContext) -> Self {
        AppError::new(ErrorCode::Unknown, "Error with context").with_context("context", format!("{:?}", ctx))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_context_creation() {
        let ctx = ErrorContext::new()
            .with_request_id("req-123")
            .with_user_id("user-456")
            .with_trace_id("trace-789");

        assert_eq!(ctx.request_id, Some("req-123".to_string()));
        assert_eq!(ctx.user_id, Some("user-456".to_string()));
        assert_eq!(ctx.trace_id, Some("trace-789".to_string()));
    }

    #[test]
    fn test_context_apply() {
        let ctx = ErrorContext::new()
            .with_request_id("req-123")
            .with_user_id("user-456");

        let error = AppError::new(ErrorCode::EntityNotFound, "User not found");
        let enriched = ctx.apply_to(error);

        assert_eq!(enriched.context().get("request_id").map(|v| v.as_str().unwrap()), Some("req-123"));
    }
}
