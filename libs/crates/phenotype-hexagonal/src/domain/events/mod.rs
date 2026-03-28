//! Domain Events - Events emitted by the domain
//! 
//! Domain events represent significant occurrences within the domain
//! that other parts of the system might want to be notified about.

use chrono::Utc;
use serde::{Serialize, Deserialize};

/// Base domain event trait
pub trait DomainEvent: Send + Sync {
    /// The event type name
    fn event_type(&self) -> &str;
    
    /// The occurred at timestamp
    fn occurred_at(&self) -> chrono::DateTime<Utc>;
}

/// Metadata for domain events
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventMetadata {
    pub correlation_id: Option<String>,
    pub causation_id: Option<String>,
    pub user_id: Option<String>,
}

impl Default for EventMetadata {
    fn default() -> Self {
        Self {
            correlation_id: None,
            causation_id: None,
            user_id: None,
        }
    }
}

impl EventMetadata {
    pub fn new() -> Self {
        Self::default()
    }
    
    pub fn with_correlation_id(mut self, id: String) -> Self {
        self.correlation_id = Some(id);
        self
    }
    
    pub fn with_causation_id(mut self, id: String) -> Self {
        self.causation_id = Some(id);
        self
    }
    
    pub fn with_user_id(mut self, id: String) -> Self {
        self.user_id = Some(id);
        self
    }
}
