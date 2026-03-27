//! Ports (interfaces) for configuration management

use async_trait::async_trait;
use crate::domain::entities::ConfigEntry;
use crate::domain::events::ConfigEvent;
use crate::value_objects::Namespace;

/// Port for configuration repository
#[async_trait]
pub trait ConfigRepository: Send + Sync {
    /// Get a config entry by key
    async fn get(&self, key: &str) -> Option<ConfigEntry>;

    /// Get a config entry by ID
    async fn get_by_id(&self, id: uuid::Uuid) -> Option<ConfigEntry>;

    /// Save a config entry
    async fn save(&self, entry: ConfigEntry) -> ConfigEntry;

    /// Delete a config entry
    async fn delete(&self, key: &str) -> bool;

    /// List entries in a namespace
    async fn list(&self, namespace: &Namespace) -> Vec<ConfigEntry>;

    /// List entries matching a prefix
    async fn list_by_prefix(&self, prefix: &str) -> Vec<ConfigEntry>;
}

/// Port for configuration event publishing
#[async_trait]
pub trait ConfigEventPublisher: Send + Sync {
    /// Publish a config event
    async fn publish(&self, event: ConfigEvent) -> Result<(), EventPublisherError>;
}

/// Event publisher error
#[derive(Debug, thiserror::Error)]
pub enum EventPublisherError {
    #[error("Connection error: {0}")]
    Connection(String),

    #[error("Serialization error: {0}")]
    Serialization(String),

    #[error("Rejected: {0}")]
    Rejected(String),
}

/// Port for configuration caching
#[async_trait]
pub trait ConfigCache: Send + Sync {
    /// Get a cached entry
    async fn get(&self, key: &str) -> Option<ConfigEntry>;

    /// Cache an entry
    async fn set(&self, entry: ConfigEntry);

    /// Invalidate a cached entry
    async fn invalidate(&self, key: &str);

    /// Clear the cache
    async fn clear(&self);
}
