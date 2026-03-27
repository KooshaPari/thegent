//! Domain events

use chrono::{DateTime, Utc};
use uuid::Uuid;
use serde::{Serialize, Deserialize};

/// Domain event types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum ConfigEvent {
    /// Config entry was created
    Created {
        entry_id: Uuid,
        key: String,
        namespace: String,
        created_by: Option<String>,
        timestamp: DateTime<Utc>,
    },
    /// Config entry was updated
    Updated {
        entry_id: Uuid,
        key: String,
        old_version: u32,
        new_version: u32,
        updated_by: Option<String>,
        timestamp: DateTime<Utc>,
    },
    /// Config entry was deleted
    Deleted {
        entry_id: Uuid,
        key: String,
        deleted_by: Option<String>,
        timestamp: DateTime<Utc>,
    },
    /// Config entry was published/approved
    Published {
        entry_id: Uuid,
        key: String,
        version: u32,
        published_by: String,
        timestamp: DateTime<Utc>,
    },
}

impl ConfigEvent {
    /// Get the event timestamp
    pub fn timestamp(&self) -> DateTime<Utc> {
        match self {
            ConfigEvent::Created { timestamp, .. } => *timestamp,
            ConfigEvent::Updated { timestamp, .. } => *timestamp,
            ConfigEvent::Deleted { timestamp, .. } => *timestamp,
            ConfigEvent::Published { timestamp, .. } => *timestamp,
        }
    }

    /// Get the entry ID
    pub fn entry_id(&self) -> Uuid {
        match self {
            ConfigEvent::Created { entry_id, .. } => *entry_id,
            ConfigEvent::Updated { entry_id, .. } => *entry_id,
            ConfigEvent::Deleted { entry_id, .. } => *entry_id,
            ConfigEvent::Published { entry_id, .. } => *entry_id,
        }
    }
}
