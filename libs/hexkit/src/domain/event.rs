//! Domain Events - Significant Business Occurrences
//!
//! Domain events represent significant occurrences in the business domain.

/// Marker trait for domain events
pub trait DomainEvent: Send + Sync {
    /// The type name of the event
    fn event_type(&self) -> &'static str;

    /// Event version for versioning
    fn version(&self) -> u32 {
        1
    }
}

/// Event metadata for event sourcing
#[derive(Debug, Clone)]
pub struct EventMetadata {
    pub event_id: String,
    pub version: u32,
    pub correlation_id: Option<String>,
    pub causation_id: Option<String>,
}

impl EventMetadata {
    pub fn new(event_id: String) -> Self {
        Self {
            event_id,
            version: 1,
            correlation_id: None,
            causation_id: None,
        }
    }

    pub fn with_correlation(mut self, correlation_id: String) -> Self {
        self.correlation_id = Some(correlation_id);
        self
    }

    pub fn with_causation(mut self, causation_id: String) -> Self {
        self.causation_id = Some(causation_id);
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Debug, Clone)]
    struct TestEvent {
        event_id: String,
        order_id: String,
    }

    impl DomainEvent for TestEvent {
        fn event_type(&self) -> &'static str {
            "test.order_created"
        }
    }

    #[test]
    fn test_event_type() {
        let event = TestEvent {
            event_id: "evt-123".to_string(),
            order_id: "order-456".to_string(),
        };

        assert_eq!(event.event_type(), "test.order_created");
        assert_eq!(event.version(), 1);
    }

    #[test]
    fn test_event_metadata() {
        let metadata = EventMetadata::new("evt-123".to_string())
            .with_correlation("corr-789".to_string())
            .with_causation("cause-abc".to_string());

        assert_eq!(metadata.event_id, "evt-123");
        assert_eq!(metadata.correlation_id, Some("corr-789".to_string()));
    }
}
