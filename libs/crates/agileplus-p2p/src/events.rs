//! Event store and snapshot store traits (inlined from agileplus_events crate).

use async_trait::async_trait;
use chrono::{DateTime, Utc};

/// Event store errors
#[derive(Debug, thiserror::Error)]
pub enum EventError {
    #[error("Event store error: {0}")]
    Error(String),
}

/// Snapshot store errors
#[derive(Debug, thiserror::Error)]
pub enum SnapshotError {
    #[error("Snapshot store error: {0}")]
    Error(String),
}

/// Trait for storing and retrieving events.
#[async_trait]
pub trait EventStore: Send + Sync {
    /// Append an event to the store.
    async fn append(&self, event: &crate::domain::Event) -> Result<i64, EventError>;

    /// Get all events for an entity.
    async fn get_events(
        &self,
        entity_type: &str,
        entity_id: i64,
    ) -> Result<Vec<crate::domain::Event>, EventError>;

    /// Get events since a specific sequence number.
    async fn get_events_since(
        &self,
        entity_type: &str,
        entity_id: i64,
        sequence: i64,
    ) -> Result<Vec<crate::domain::Event>, EventError>;

    /// Get events in a time range.
    async fn get_events_by_range(
        &self,
        entity_type: &str,
        entity_id: i64,
        from: DateTime<Utc>,
        to: DateTime<Utc>,
    ) -> Result<Vec<crate::domain::Event>, EventError>;

    /// Get the latest sequence number for an entity.
    async fn get_latest_sequence(
        &self,
        entity_type: &str,
        entity_id: i64,
    ) -> Result<i64, EventError>;
}

/// Trait for storing and retrieving snapshots.
#[async_trait]
pub trait SnapshotStore: Send + Sync {
    /// Save a snapshot.
    async fn save(&self, snapshot: &crate::domain::Snapshot) -> Result<(), SnapshotError>;

    /// Load the latest snapshot for an entity (alias for get_latest).
    async fn load(
        &self,
        entity_type: &str,
        entity_id: i64,
    ) -> Result<Option<crate::domain::Snapshot>, SnapshotError>;

    /// Get the latest snapshot for an entity.
    async fn get_latest(
        &self,
        entity_type: &str,
        entity_id: i64,
    ) -> Result<Option<crate::domain::Snapshot>, SnapshotError> {
        // Default implementation delegates to load
        self.load(entity_type, entity_id).await
    }

    /// Delete all snapshots before a specific date.
    async fn delete_before(
        &self,
        _entity_type: &str,
        _entity_id: i64,
        _sequence: i64,
    ) -> Result<(), SnapshotError>;
}
