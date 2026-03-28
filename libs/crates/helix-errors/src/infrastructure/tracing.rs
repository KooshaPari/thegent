//! Tracing integration for errors

use crate::Error;
use tracing::{Span, instrument};

impl Error {
    /// Add current span information as context
    pub fn with_span_context(self, span: &Span) -> Self {
        if let Some(meta) = span.metadata() {
            self.with_context("span_name", meta.name())
                .with_context("span_target", meta.target())
        } else {
            self
        }
    }

    /// Create error from span with automatic context capture
    #[instrument(skip_all, fields(error.kind = ?kind))]
    pub fn traced(kind: crate::ErrorKind, message: impl Into<String>) -> Error {
        Error::new(kind, message)
    }
}

/// Span extension for error recording
pub trait SpanExt {
    /// Record an error onto the span
    fn record_error(&self, error: &Error);
}

impl SpanExt for Span {
    fn record_error(&self, error: &Error) {
        self.record("error.kind", error.kind().code());
        self.record("error.message", error.message());
        self.record("error.code", error.code());
    }
}
