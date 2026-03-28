//! Git-backed state export — serialize SQLite state to deterministic files.
//!
//! Writes to `.agileplus/sync/` with the layout:
//!   events/{entity_type}/{id}.jsonl  — one JSON per line, ordered by sequence
//!   snapshots/{entity_type}/{id}.json — latest snapshot, pretty-printed sorted keys
//!   sync_state.json                  — SyncMapping entries and device sync vectors
//!   device.json                      — local DeviceNode info
//!
//! All JSON uses sorted keys, 2-space indent, UTF-8.
//!
//! Traceability: WP17 / T101

mod serialization;
mod writers;

#[cfg(test)]
mod tests;

use std::path::Path;
use std::time::Instant;

use serde_json::Value;

use crate::device::DeviceStore;
use crate::domain::SyncMapping;
use crate::error::ConnectionError;
use crate::events::{EventStore, SnapshotStore};

pub use serialization::{to_sorted, to_sorted_line, to_sorted_pretty};
pub use writers::EntityRef;

// ── Error ─────────────────────────────────────────────────────────────────────

#[derive(Debug, thiserror::Error)]
pub enum ExportError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("Event store error: {0}")]
    EventStore(String),

    #[error("Snapshot store error: {0}")]
    SnapshotStore(String),

    #[error("Device store error: {0}")]
    DeviceStore(#[from] ConnectionError),

    #[error("Sync store error: {0}")]
    SyncStore(String),
}

// ── Stats ─────────────────────────────────────────────────────────────────────

/// Statistics returned after a successful export.
#[derive(Debug, Default, Clone)]
pub struct ExportStats {
    pub events_exported: usize,
    pub snapshots_exported: usize,
    pub sync_mappings_exported: usize,
    pub duration_ms: u64,
}

/// Export all state to `output_dir` in a deterministic, git-friendly format.
///
/// Parameters:
/// - `entities` — the set of (entity_type, entity_id) pairs to export. In a
///   production system this would be retrieved from a catalog; here callers
///   supply it to keep the function generic over `EventStore` implementations.
/// - `sync_mappings` — pre-fetched list of `SyncMapping` rows.
/// - `sync_vector_json` — the current device sync vector serialized to JSON.
pub async fn export_state<ES, SS>(
    event_store: &ES,
    snapshot_store: &SS,
    device_store: &dyn DeviceStore,
    sync_mappings: &[SyncMapping],
    sync_vector_json: Value,
    entities: &[EntityRef],
    output_dir: &Path,
) -> Result<ExportStats, ExportError>
where
    ES: EventStore,
    SS: SnapshotStore,
{
    let started = Instant::now();
    let mut stats = ExportStats::default();

    writers::write_device_file(device_store, output_dir).await?;

    for entity in entities {
        let (events_exported, snapshots_exported) =
            writers::write_entity_files(event_store, snapshot_store, entity, output_dir).await?;
        stats.events_exported += events_exported;
        stats.snapshots_exported += snapshots_exported;
    }

    stats.sync_mappings_exported =
        writers::write_sync_state(output_dir, sync_mappings, sync_vector_json)?;

    stats.duration_ms = started.elapsed().as_millis() as u64;
    Ok(stats)
}
