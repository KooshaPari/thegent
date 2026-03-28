//! Span - A span in a trace.

use crate::domain::{SpanContext, SpanId, SpanStatus, TraceId};
use chrono::{DateTime, Utc};
use std::collections::HashMap;

/// Span represents a unit of work in a distributed trace.
#[derive(Debug, Clone)]
pub struct Span {
    name: String,
    context: SpanContext,
    start_time: DateTime<Utc>,
    end_time: Option<DateTime<Utc>>,
    status: SpanStatus,
    attributes: HashMap<String, String>,
    events: Vec<SpanEvent>,
    links: Vec<SpanLink>,
}

impl Span {
    /// Create a new span.
    pub fn new(name: String, trace_id: TraceId, span_id: SpanId) -> Self {
        Self {
            name,
            context: SpanContext::new(trace_id, span_id, crate::domain::TraceFlags::default(), false),
            start_time: Utc::now(),
            end_time: None,
            status: SpanStatus::Unset,
            attributes: HashMap::new(),
            events: Vec::new(),
            links: Vec::new(),
        }
    }

    /// Get the span name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Get the span context.
    pub fn context(&self) -> &SpanContext {
        &self.context
    }

    /// Get the trace ID.
    pub fn trace_id(&self) -> TraceId {
        self.context.trace_id()
    }

    /// Get the span ID.
    pub fn span_id(&self) -> SpanId {
        self.context.span_id()
    }

    /// Get the start time.
    pub fn start_time(&self) -> DateTime<Utc> {
        self.start_time
    }

    /// Get the end time.
    pub fn end_time(&self) -> Option<DateTime<Utc>> {
        self.end_time
    }

    /// Get the duration.
    pub fn duration(&self) -> Option<chrono::Duration> {
        self.end_time.map(|end| end - self.start_time)
    }

    /// Get the status.
    pub fn status(&self) -> SpanStatus {
        self.status
    }

    /// Set the status.
    pub fn set_status(&mut self, status: SpanStatus) {
        self.status = status;
    }

    /// Set an attribute.
    pub fn set_attribute(&mut self, key: impl Into<String>, value: impl Into<String>) {
        self.attributes.insert(key.into(), value.into());
    }

    /// Get an attribute.
    pub fn get_attribute(&self, key: &str) -> Option<&str> {
        self.attributes.get(key).map(|s| s.as_str())
    }

    /// Add an event.
    pub fn add_event(&mut self, name: String) {
        self.events.push(SpanEvent::new(name));
    }

    /// Add an event with attributes.
    pub fn add_event_with_attributes(&mut self, name: String, attributes: HashMap<String, String>) {
        self.events.push(SpanEvent::new_with_attributes(name, attributes));
    }

    /// Record an error.
    pub fn record_error(&mut self, message: String) {
        self.add_event_with_attributes(
            "exception".to_string(),
            HashMap::from([("message".to_string(), message)]),
        );
    }

    /// End the span.
    pub fn end(&mut self) {
        self.end_time = Some(Utc::now());
    }

    /// Check if span is ended.
    pub fn is_ended(&self) -> bool {
        self.end_time.is_some()
    }
}

/// Span status.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SpanStatus {
    /// Unset status.
    Unset,
    /// OK status.
    Ok,
    /// Error status.
    Error,
    /// Unknown status.
    Unknown,
}

impl Default for SpanStatus {
    fn default() -> Self {
        Self::Unset
    }
}

/// A span event.
#[derive(Debug, Clone)]
pub struct SpanEvent {
    name: String,
    timestamp: DateTime<Utc>,
    attributes: HashMap<String, String>,
}

impl SpanEvent {
    /// Create a new span event.
    pub fn new(name: String) -> Self {
        Self {
            name,
            timestamp: Utc::now(),
            attributes: HashMap::new(),
        }
    }

    /// Create a new span event with attributes.
    pub fn new_with_attributes(name: String, attributes: HashMap<String, String>) -> Self {
        Self {
            name,
            timestamp: Utc::now(),
            attributes,
        }
    }
}

/// A span link.
#[derive(Debug, Clone)]
pub struct SpanLink {
    context: SpanContext,
    attributes: HashMap<String, String>,
}

impl SpanLink {
    /// Create a new span link.
    pub fn new(context: SpanContext) -> Self {
        Self {
            context,
            attributes: HashMap::new(),
        }
    }
}
