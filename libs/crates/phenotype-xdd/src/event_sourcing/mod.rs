//! Event Sourcing
//! 
//! Event Sourcing stores the complete history of state changes as events
//! rather than storing just the current state.
//! 
//! ## Benefits
//! 
//! - Complete audit trail
//! - Temporal queries ("what was state at time T?")
//! - Event replay for debugging
//! - Easy integration with event-driven architectures
//! 
//! ## Event Sourcing Pattern
//! 
//! ```text
//! ┌─────────────────────────────────────────┐
//! │              Event Store                 │
//! │  ┌───────────────────────────────────┐  │
//! │  │ Event #1: OrderCreated            │  │
//! │  │ Event #2: ItemAdded              │  │
//! │  │ Event #3: ItemAdded              │  │
//! │  │ Event #4: DiscountApplied        │  │
//! │  │ Event #5: OrderPlaced            │  │
//! │  └───────────────────────────────────┘  │
//! └─────────────────────────────────────────┘
//!                      │
//!                      ▼
//!              ┌───────────────┐
//!              │  Replay All   │
//!              │  to Get State │
//!              └───────────────┘
//!                      │
//!                      ▼
//!              ┌───────────────┐
//!              │ Current State │
//!              │   Order #42   │
//!              │ Items: [A, B] │
//!              │ Status: Placed│
//!              └───────────────┘
//! ```

use chrono::{DateTime, Utc};

/// Base event type
#[derive(Debug, Clone)]
pub struct Event {
    pub id: String,
    pub event_type: String,
    pub aggregate_id: String,
    pub version: u64,
    pub payload: serde_json::Value,
    pub metadata: EventMetadata,
    pub occurred_at: DateTime<Utc>,
}

impl Event {
    pub fn new(
        event_type: impl Into<String>,
        aggregate_id: impl Into<String>,
        version: u64,
        payload: serde_json::Value,
    ) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            event_type: event_type.into(),
            aggregate_id: aggregate_id.into(),
            version,
            payload,
            metadata: EventMetadata::new(),
            occurred_at: Utc::now(),
        }
    }
    
    pub fn with_metadata(mut self, metadata: EventMetadata) -> Self {
        self.metadata = metadata;
        self
    }
}

/// Event metadata
#[derive(Debug, Clone, Default)]
pub struct EventMetadata {
    pub correlation_id: Option<String>,
    pub causation_id: Option<String>,
    pub user_id: Option<String>,
    pub timestamp: DateTime<Utc>,
}

impl EventMetadata {
    pub fn new() -> Self {
        Self {
            correlation_id: None,
            causation_id: None,
            user_id: None,
            timestamp: Utc::now(),
        }
    }
    
    pub fn correlation_id(mut self, id: impl Into<String>) -> Self {
        self.correlation_id = Some(id.into());
        self
    }
    
    pub fn causation_id(mut self, id: impl Into<String>) -> Self {
        self.causation_id = Some(id.into());
        self
    }
    
    pub fn user_id(mut self, id: impl Into<String>) -> Self {
        self.user_id = Some(id.into());
        self
    }
}

/// Aggregate trait for event sourcing
pub trait Aggregate {
    type Event: Clone;
    
    fn aggregate_id(&self) -> &str;
    fn version(&self) -> u64;
    
    /// Apply an event to get new state
    fn apply(&mut self, event: Self::Event);
}

/// Event store trait
#[async_trait::async_trait]
pub trait EventStore<A: Aggregate>: Send + Sync {
    type Error: std::error::Error + Send + Sync + 'static;
    
    /// Append events to the store
    async fn append(&self, aggregate_id: &str, events: &[A::Event]) -> Result<(), Self::Error>;
    
    /// Get all events for an aggregate
    async fn get_events(&self, aggregate_id: &str) -> Result<Vec<A::Event>, Self::Error>;
    
    /// Get events since a specific version
    async fn get_events_since(&self, aggregate_id: &str, version: u64) -> Result<Vec<A::Event>, Self::Error>;
}

/// Snapshot trait for optimizing event replay
#[async_trait::async_trait]
pub trait Snapshot<A: Aggregate>: Send + Sync {
    type Error: std::error::Error + Send + Sync + 'static;
    
    async fn save(&self, aggregate: &A) -> Result<(), Self::Error>;
    async fn load(&self, aggregate_id: &str) -> Result<Option<A>, Self::Error>;
}
