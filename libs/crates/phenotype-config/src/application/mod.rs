//! Application layer - Use cases and orchestration

use crate::domain::entities::ConfigEntry;
use crate::domain::events::ConfigEvent;
use crate::ports::{ConfigRepository, ConfigEventPublisher, ConfigCache};
use crate::value_objects::{ConfigValue, Namespace};
use crate::ConfigError;
use std::sync::Arc;

/// Use case for creating a config entry
pub struct CreateConfigUseCase<R, E, C>
where
    R: ConfigRepository,
    E: ConfigEventPublisher,
    C: ConfigCache,
{
    repository: Arc<R>,
    event_publisher: Arc<E>,
    cache: Arc<C>,
}

impl<R, E, C> CreateConfigUseCase<R, E, C>
where
    R: ConfigRepository,
    E: ConfigEventPublisher,
    C: ConfigCache,
{
    /// Create a new use case instance
    pub fn new(repository: Arc<R>, event_publisher: Arc<E>, cache: Arc<C>) -> Self {
        Self {
            repository,
            event_publisher,
            cache,
        }
    }

    /// Execute the use case
    pub async fn execute(
        &self,
        key: String,
        value: ConfigValue,
        namespace: Namespace,
        created_by: Option<String>,
    ) -> Result<ConfigEntry, ConfigError> {
        // Check if already exists
        if self.repository.get(&key).await.is_some() {
            return Err(ConfigError::AlreadyExists(key));
        }

        // Create the entry
        let entry = ConfigEntry::new(key, value, namespace, created_by.clone())?;

        // Save to repository
        let saved = self.repository.save(entry.clone()).await;

        // Publish event
        let event = ConfigEvent::Created {
            entry_id: saved.id(),
            key: saved.key().to_string(),
            namespace: saved.namespace().path().to_string(),
            created_by,
            timestamp: saved.created_at(),
        };
        let _ = self.event_publisher.publish(event).await;

        // Invalidate cache
        self.cache.invalidate(saved.key()).await;

        Ok(saved)
    }
}

/// Use case for updating a config entry
pub struct UpdateConfigUseCase<R, E, C>
where
    R: ConfigRepository,
    E: ConfigEventPublisher,
    C: ConfigCache,
{
    repository: Arc<R>,
    event_publisher: Arc<E>,
    cache: Arc<C>,
}

impl<R, E, C> UpdateConfigUseCase<R, E, C>
where
    R: ConfigRepository,
    E: ConfigEventPublisher,
    C: ConfigCache,
{
    /// Create a new use case instance
    pub fn new(repository: Arc<R>, event_publisher: Arc<E>, cache: Arc<C>) -> Self {
        Self {
            repository,
            event_publisher,
            cache,
        }
    }

    /// Execute the use case
    pub async fn execute(
        &self,
        key: String,
        new_value: ConfigValue,
        updated_by: Option<String>,
    ) -> Result<ConfigEntry, ConfigError> {
        // Get existing entry
        let existing = self.repository.get(&key).await
            .ok_or_else(|| ConfigError::NotFound(key.clone()))?;

        // Create new version
        let updated = existing.update_value(new_value, updated_by.clone());

        // Save to repository
        let saved = self.repository.save(updated.clone()).await;

        // Publish event
        let event = ConfigEvent::Updated {
            entry_id: saved.id(),
            key: saved.key().to_string(),
            old_version: existing.version(),
            new_version: saved.version(),
            updated_by,
            timestamp: saved.updated_at(),
        };
        let _ = self.event_publisher.publish(event).await;

        // Invalidate cache
        self.cache.invalidate(saved.key()).await;

        Ok(saved)
    }
}

/// Use case for getting a config entry
pub struct GetConfigUseCase<R, C>
where
    R: ConfigRepository,
    C: ConfigCache,
{
    repository: Arc<R>,
    cache: Arc<C>,
}

impl<R, C> GetConfigUseCase<R, C>
where
    R: ConfigRepository,
    C: ConfigCache,
{
    /// Create a new use case instance
    pub fn new(repository: Arc<R>, cache: Arc<C>) -> Self {
        Self { repository, cache }
    }

    /// Execute the use case
    pub async fn execute(&self, key: &str) -> Result<ConfigEntry, ConfigError> {
        // Try cache first
        if let Some(entry) = self.cache.get(key).await {
            return Ok(entry);
        }

        // Get from repository
        let entry = self.repository.get(key).await
            .ok_or_else(|| ConfigError::NotFound(key.to_string()))?;

        // Cache the entry
        self.cache.set(entry.clone()).await;

        Ok(entry)
    }
}

/// Use case for deleting a config entry
pub struct DeleteConfigUseCase<R, E, C>
where
    R: ConfigRepository,
    E: ConfigEventPublisher,
    C: ConfigCache,
{
    repository: Arc<R>,
    event_publisher: Arc<E>,
    cache: Arc<C>,
}

impl<R, E, C> DeleteConfigUseCase<R, E, C>
where
    R: ConfigRepository,
    E: ConfigEventPublisher,
    C: ConfigCache,
{
    /// Create a new use case instance
    pub fn new(repository: Arc<R>, event_publisher: Arc<E>, cache: Arc<C>) -> Self {
        Self {
            repository,
            event_publisher,
            cache,
        }
    }

    /// Execute the use case
    pub async fn execute(
        &self,
        key: &str,
        deleted_by: Option<String>,
    ) -> Result<bool, ConfigError> {
        // Get existing entry
        let existing = self.repository.get(key).await
            .ok_or_else(|| ConfigError::NotFound(key.to_string()))?;

        // Delete from repository
        let deleted = self.repository.delete(key).await;

        if deleted {
            // Publish event
            let event = ConfigEvent::Deleted {
                entry_id: existing.id(),
                key: key.to_string(),
                deleted_by,
                timestamp: chrono::Utc::now(),
            };
            let _ = self.event_publisher.publish(event).await;

            // Invalidate cache
            self.cache.invalidate(key).await;
        }

        Ok(deleted)
    }
}
