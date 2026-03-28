//! Domain Events
//!
//! Domain events are the significant business occurrences that happened
//! and need to be communicated to other parts of the system.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use uuid::Uuid;

/// Marker trait for domain events.
pub trait DomainEvent: Send + Sync + Clone {
    fn event_type(&self) -> &str;
    fn occurred_at(&self) -> DateTime<Utc>;
    fn aggregate_id(&self) -> &str;
}

/// Base domain event implementation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BaseDomainEvent {
    event_id: String,
    event_type: String,
    occurred_at: DateTime<Utc>,
    aggregate_id: String,
    metadata: std::collections::HashMap<String, String>,
}

impl BaseDomainEvent {
    pub fn new(event_type: impl Into<String>, aggregate_id: impl Into<String>) -> Self {
        Self {
            event_id: Uuid::new_v4().to_string(),
            event_type: event_type.into(),
            occurred_at: Utc::now(),
            aggregate_id: aggregate_id.into(),
            metadata: std::collections::HashMap::new(),
        }
    }

    pub fn with_metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }

    pub fn event_id(&self) -> &str {
        &self.event_id
    }
}

impl DomainEvent for BaseDomainEvent {
    fn event_type(&self) -> &str {
        &self.event_type
    }

    fn occurred_at(&self) -> DateTime<Utc> {
        self.occurred_at
    }

    fn aggregate_id(&self) -> &str {
        &self.aggregate_id
    }
}

/// Event envelope for event sourcing.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventEnvelope<T: DomainEvent> {
    pub event_id: String,
    pub event_type: String,
    pub occurred_at: DateTime<Utc>,
    pub aggregate_id: String,
    pub aggregate_type: String,
    pub version: u64,
    pub payload: T,
    pub metadata: std::collections::HashMap<String, String>,
}

impl<T: DomainEvent> EventEnvelope<T> {
    pub fn new(aggregate_type: impl Into<String>, version: u64, payload: T) -> Self {
        Self {
            event_id: Uuid::new_v4().to_string(),
            event_type: payload.event_type().to_string(),
            occurred_at: payload.occurred_at(),
            aggregate_id: payload.aggregate_id().to_string(),
            aggregate_type: aggregate_type.into(),
            version,
            payload,
            metadata: std::collections::HashMap::new(),
        }
    }
}

/// Event handler trait.
pub trait EventHandler<E: DomainEvent>: Send + Sync {
    fn handle(&self, event: &E) -> Result<(), String>;
}

/// Simple typed event bus for domain events.
pub trait EventBus<E: DomainEvent>: Send + Sync {
    fn publish(&self, event: E) -> Result<(), String>;
    fn subscribe<H>(&self, handler: Arc<H>)
    where
        H: EventHandler<E> + 'static;
}
