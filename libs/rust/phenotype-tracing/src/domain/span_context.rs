//! SpanContext - Context for a span including trace and span IDs.

use crate::domain::{SpanId, TraceFlags, TraceId};

/// SpanContext represents the context of a span.
///
/// It contains the trace ID, span ID, and trace flags that uniquely
/// identify a span in a distributed trace.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SpanContext {
    trace_id: TraceId,
    span_id: SpanId,
    trace_flags: TraceFlags,
    is_remote: bool,
}

impl SpanContext {
    /// Create a new span context.
    pub fn new(
        trace_id: TraceId,
        span_id: SpanId,
        trace_flags: TraceFlags,
        is_remote: bool,
    ) -> Self {
        Self {
            trace_id,
            span_id,
            trace_flags,
            is_remote,
        }
    }

    /// Get the trace ID.
    pub fn trace_id(&self) -> TraceId {
        self.trace_id
    }

    /// Get the span ID.
    pub fn span_id(&self) -> SpanId {
        self.span_id
    }

    /// Get the trace flags.
    pub fn trace_flags(&self) -> TraceFlags {
        self.trace_flags
    }

    /// Check if this context is from a remote parent.
    pub fn is_remote(&self) -> bool {
        self.is_remote
    }

    /// Check if sampling is enabled.
    pub fn is_sampled(&self) -> bool {
        self.trace_flags.is_sampled()
    }

    /// Check if this is a valid context.
    pub fn is_valid(&self) -> bool {
        !self.trace_id.is_null() && !self.span_id.is_null()
    }

    /// Get the null context.
    pub fn nil() -> Self {
        Self {
            trace_id: TraceId::nil(),
            span_id: SpanId::nil(),
            trace_flags: TraceFlags::default(),
            is_remote: false,
        }
    }
}

impl Default for SpanContext {
    fn default() -> Self {
        Self::nil()
    }
}
