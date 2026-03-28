//! Device node management for P2P synchronization.

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

/// A device node representing a peer in the P2P network.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeviceNode {
    /// Unique device identifier
    pub device_id: String,
    /// Device name or label
    pub device_name: String,
    /// Last sync timestamp
    pub last_sync: Option<chrono::DateTime<chrono::Utc>>,
    /// Sync vector clock mapping entity types to max sequences
    pub sync_vector: BTreeMap<String, i64>,
}

/// Error type for device store operations.
#[derive(Debug, thiserror::Error)]
pub enum DeviceError {
    #[error("Device not found: {0}")]
    NotFound(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
}

/// Trait for accessing device node information.
#[async_trait]
pub trait DeviceStore: Send + Sync {
    /// Get the local device node.
    async fn get_device(&self) -> Result<DeviceNode, DeviceError>;

    /// Update the device node.
    async fn update_device(&self, device: DeviceNode) -> Result<(), DeviceError>;
}

/// In-memory device store for testing.
#[derive(Default)]
pub struct InMemoryDeviceStore {
    device: std::sync::Mutex<Option<DeviceNode>>,
}

impl InMemoryDeviceStore {
    /// Create a new in-memory device store with a default device.
    pub fn new_with_device(device: DeviceNode) -> Self {
        Self {
            device: std::sync::Mutex::new(Some(device)),
        }
    }
}

#[async_trait]
impl DeviceStore for InMemoryDeviceStore {
    async fn get_device(&self) -> Result<DeviceNode, DeviceError> {
        self.device
            .lock()
            .unwrap()
            .clone()
            .ok_or_else(|| DeviceError::NotFound("device not initialized".to_string()))
    }

    async fn update_device(&self, device: DeviceNode) -> Result<(), DeviceError> {
        *self.device.lock().unwrap() = Some(device);
        Ok(())
    }
}
