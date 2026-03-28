use super::*;
use std::sync::Mutex;

use crate::device::InMemoryDeviceStore;
use crate::domain::{Event, Snapshot, SyncMapping};
use crate::events::{EventError, SnapshotError};
use async_trait::async_trait;
use chrono::Utc;

// ── Minimal in-memory EventStore ─────────────────────────────────────────────

#[derive(Default)]
struct MemEventStore {
    events: Mutex<Vec<Event>>,
}

#[async_trait]
impl EventStore for MemEventStore {
    async fn append(&self, event: &Event) -> Result<i64, EventError> {
        let mut g = self.events.lock().unwrap();
        g.push(event.clone());
        Ok(event.sequence)
    }

    async fn get_events(
        &self,
        entity_type: &str,
        entity_id: i64,
    ) -> Result<Vec<Event>, EventError> {
        let g = self.events.lock().unwrap();
        Ok(g.iter()
            .filter(|e| e.entity_type == entity_type && e.entity_id == entity_id)
            .cloned()
            .collect())
    }

    async fn get_events_since(
        &self,
        entity_type: &str,
        entity_id: i64,
        sequence: i64,
    ) -> Result<Vec<Event>, EventError> {
        let g = self.events.lock().unwrap();
        Ok(g.iter()
            .filter(|e| {
                e.entity_type == entity_type && e.entity_id == entity_id && e.sequence > sequence
            })
            .cloned()
            .collect())
    }

    async fn get_events_by_range(
        &self,
        entity_type: &str,
        entity_id: i64,
        from: chrono::DateTime<Utc>,
        to: chrono::DateTime<Utc>,
    ) -> Result<Vec<Event>, EventError> {
        let g = self.events.lock().unwrap();
        Ok(g.iter()
            .filter(|e| {
                e.entity_type == entity_type
                    && e.entity_id == entity_id
                    && e.timestamp >= from
                    && e.timestamp <= to
            })
            .cloned()
            .collect())
    }

    async fn get_latest_sequence(
        &self,
        entity_type: &str,
        entity_id: i64,
    ) -> Result<i64, EventError> {
        let g = self.events.lock().unwrap();
        Ok(g.iter()
            .filter(|e| e.entity_type == entity_type && e.entity_id == entity_id)
            .map(|e| e.sequence)
            .max()
            .unwrap_or(0))
    }
}

// ── Minimal in-memory SnapshotStore ──────────────────────────────────────────

#[derive(Default)]
struct MemSnapshotStore {
    snapshots: Mutex<Vec<Snapshot>>,
}

#[async_trait]
impl SnapshotStore for MemSnapshotStore {
    async fn save(&self, snapshot: &Snapshot) -> Result<(), SnapshotError> {
        self.snapshots.lock().unwrap().push(snapshot.clone());
        Ok(())
    }

    async fn load(
        &self,
        entity_type: &str,
        entity_id: i64,
    ) -> Result<Option<Snapshot>, SnapshotError> {
        let g = self.snapshots.lock().unwrap();
        Ok(g.iter()
            .filter(|s| s.entity_type == entity_type && s.entity_id == entity_id)
            .max_by_key(|s| s.event_sequence)
            .cloned())
    }

    async fn delete_before(
        &self,
        _entity_type: &str,
        _entity_id: i64,
        _sequence: i64,
    ) -> Result<(), SnapshotError> {
        Ok(())
    }
}

#[tokio::test]
async fn export_creates_expected_files() {
    let tmp = tempfile::tempdir().unwrap();
    let out = tmp.path();

    let es = MemEventStore::default();
    let ss = MemSnapshotStore::default();

    // Initialize device store with a device node
    let device = crate::device::DeviceNode {
        device_id: "test-device".to_string(),
        device_name: "Test Device".to_string(),
        last_sync: None,
        sync_vector: Default::default(),
    };
    let ds = InMemoryDeviceStore::new_with_device(device);

    // Seed one event
    let mut ev = Event::new(
        "Feature",
        1,
        "created",
        serde_json::json!({"title": "T1"}),
        "test",
    );
    ev.sequence = 1;
    es.append(&ev).await.unwrap();

    // Seed one snapshot
    let snap = Snapshot::new("Feature", 1, serde_json::json!({"title": "T1"}), 1);
    ss.save(&snap).await.unwrap();

    let mappings = vec![SyncMapping::new("Feature", 1, "plane-001", 1)];
    let entities = vec![EntityRef {
        entity_type: "Feature".into(),
        entity_id: 1,
    }];

    let stats = export_state(
        &es,
        &ss,
        &ds,
        &mappings,
        serde_json::json!({}),
        &entities,
        out,
    )
    .await
    .unwrap();

    assert_eq!(stats.events_exported, 1);
    assert_eq!(stats.snapshots_exported, 1);
    assert_eq!(stats.sync_mappings_exported, 1);

    // Verify files exist
    assert!(out.join("device.json").exists());
    assert!(out.join("events/Feature/1.jsonl").exists());
    assert!(out.join("snapshots/Feature/1.json").exists());
    assert!(out.join("sync_state.json").exists());
}

#[test]
fn to_sorted_sorts_object_keys() {
    let v = serde_json::json!({"z": 1, "a": 2, "m": 3});
    let s = to_sorted_pretty(v).unwrap();
    let pos_a = s.find('"').unwrap();
    let first_key = &s[pos_a + 1..pos_a + 2];
    assert_eq!(first_key, "a");
}
