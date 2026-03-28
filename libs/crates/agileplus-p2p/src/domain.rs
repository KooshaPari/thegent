//! Domain types (inlined from agileplus_domain crate).

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// An event representing a change to an entity.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    /// Type of entity this event belongs to
    pub entity_type: String,
    /// ID of the entity
    pub entity_id: i64,
    /// Sequence number of this event
    pub sequence: i64,
    /// Event type/action
    pub event_type: String,
    /// Event payload as JSON
    pub payload: serde_json::Value,
    /// User/actor who triggered this event
    pub actor: String,
    /// When this event occurred
    pub timestamp: DateTime<Utc>,
}

impl Event {
    /// Create a new event
    pub fn new(
        entity_type: impl Into<String>,
        entity_id: i64,
        event_type: impl Into<String>,
        payload: serde_json::Value,
        actor: impl Into<String>,
    ) -> Self {
        Self {
            entity_type: entity_type.into(),
            entity_id,
            sequence: 0,
            event_type: event_type.into(),
            payload,
            actor: actor.into(),
            timestamp: Utc::now(),
        }
    }
}

/// A snapshot of entity state at a point in time.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Snapshot {
    /// Type of entity
    pub entity_type: String,
    /// ID of the entity
    pub entity_id: i64,
    /// Sequence number of the snapshot (event_sequence)
    pub sequence: i64,
    /// For backward compatibility with tests
    #[serde(skip)]
    pub event_sequence: Option<i64>,
    /// Snapshot state as JSON
    pub state: serde_json::Value,
    /// When this snapshot was taken
    pub timestamp: DateTime<Utc>,
}

impl Snapshot {
    /// Create a new snapshot
    pub fn new(
        entity_type: impl Into<String>,
        entity_id: i64,
        state: serde_json::Value,
        sequence: i64,
    ) -> Self {
        Self {
            entity_type: entity_type.into(),
            entity_id,
            sequence,
            event_sequence: Some(sequence),
            state,
            timestamp: Utc::now(),
        }
    }
}

/// Sync mapping for P2P synchronization between devices.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncMapping {
    /// Device ID of the peer
    pub device_id: String,
    /// Entity type
    pub entity_type: String,
    /// Entity ID
    pub entity_id: i64,
    /// Last known sequence number
    pub sequence: i64,
    /// Last sync timestamp
    pub last_sync: DateTime<Utc>,
}

impl SyncMapping {
    /// Create a new sync mapping
    pub fn new(
        entity_type: impl Into<String>,
        entity_id: i64,
        device_id: impl Into<String>,
        sequence: impl Into<i64>,
    ) -> Self {
        Self {
            entity_type: entity_type.into(),
            entity_id,
            device_id: device_id.into(),
            sequence: sequence.into(),
            last_sync: Utc::now(),
        }
    }
}
