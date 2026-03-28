use std::io::Write as _;
use std::path::Path;

use serde_json::Value;
use tracing::debug;

use crate::device::DeviceStore;
use crate::domain::{Event, Snapshot, SyncMapping};
use crate::events::{EventStore, SnapshotStore};

use super::{to_sorted_line, to_sorted_pretty, ExportError};

/// Describes a single (entity_type, entity_id) pair to export.
#[derive(Debug, Clone)]
pub struct EntityRef {
    pub entity_type: String,
    pub entity_id: i64,
}

pub async fn write_device_file(
    device_store: &dyn DeviceStore,
    output_dir: &Path,
) -> Result<(), ExportError> {
    let device_path = output_dir.join("device.json");
    if let Some(parent) = device_path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let device = device_store.get_device().await.map_err(|e| {
        ExportError::DeviceStore(crate::error::ConnectionError::ConnectionFailed(
            e.to_string(),
        ))
    })?;
    let device_json = serde_json::to_value(&device)?;
    std::fs::write(&device_path, to_sorted_pretty(device_json)?.as_bytes())?;
    debug!("Wrote device.json");
    Ok(())
}

pub async fn write_entity_files<ES, SS>(
    event_store: &ES,
    snapshot_store: &SS,
    entity: &EntityRef,
    output_dir: &Path,
) -> Result<(usize, usize), ExportError>
where
    ES: EventStore,
    SS: SnapshotStore,
{
    let mut events_exported = 0;
    let mut snapshots_exported = 0;

    let events: Vec<Event> = event_store
        .get_events(&entity.entity_type, entity.entity_id)
        .await
        .map_err(|e| ExportError::EventStore(e.to_string()))?;

    if !events.is_empty() {
        let events_dir = output_dir.join("events").join(&entity.entity_type);
        std::fs::create_dir_all(&events_dir)?;
        let file_path = events_dir.join(format!("{}.jsonl", entity.entity_id));
        let mut file = std::fs::File::create(&file_path)?;

        for event in &events {
            let line = to_sorted_line(serde_json::to_value(event)?)?;
            file.write_all(line.as_bytes())?;
            file.write_all(b"\n")?;
        }
        events_exported += events.len();
        debug!(
            "Wrote {} events for {}/{}",
            events.len(),
            entity.entity_type,
            entity.entity_id
        );
    }

    let snapshot: Option<Snapshot> = snapshot_store
        .load(&entity.entity_type, entity.entity_id)
        .await
        .map_err(|e| ExportError::SnapshotStore(e.to_string()))?;

    if let Some(snap) = snapshot {
        let snap_dir = output_dir.join("snapshots").join(&entity.entity_type);
        std::fs::create_dir_all(&snap_dir)?;
        let file_path = snap_dir.join(format!("{}.json", entity.entity_id));
        let snap_json = serde_json::to_value(&snap)?;
        std::fs::write(&file_path, to_sorted_pretty(snap_json)?.as_bytes())?;
        snapshots_exported += 1;
        debug!(
            "Wrote snapshot for {}/{}",
            entity.entity_type, entity.entity_id
        );
    }

    Ok((events_exported, snapshots_exported))
}

pub fn write_sync_state(
    output_dir: &Path,
    sync_mappings: &[SyncMapping],
    sync_vector_json: Value,
) -> Result<usize, ExportError> {
    let sync_state = serde_json::json!({
        "sync_mappings": sync_mappings,
        "sync_vector": sync_vector_json,
    });
    let sync_state_path = output_dir.join("sync_state.json");
    std::fs::write(&sync_state_path, to_sorted_pretty(sync_state)?.as_bytes())?;
    debug!(
        "Wrote sync_state.json with {} mappings",
        sync_mappings.len()
    );
    Ok(sync_mappings.len())
}
