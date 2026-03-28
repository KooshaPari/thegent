//! Domain layer - Pure tracing concepts with ZERO external dependencies.

mod span;
mod trace_id;
mod span_id;
mod span_context;
mod trace_flags;

pub use span::Span;
pub use trace_id::TraceId;
pub use span_id::SpanId;
pub use span_context::SpanContext;
pub use trace_flags::TraceFlags;
