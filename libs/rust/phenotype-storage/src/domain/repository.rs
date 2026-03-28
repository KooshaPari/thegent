//! Repository port - The core abstraction for data persistence.
//!
//! Following the Repository Pattern from DDD:
//! - Provides collection-like interface for accessing domain objects
//! - Abstracts the underlying persistence technology
//! - Located in domain layer (interface only, no implementation)

use async_trait::async_trait;

use crate::domain::{Entity, EntityId, RepositoryError, StorageResult};

/// Repository port - defines the contract for persisting entities.
///
/// This trait is implemented by adapters in the `adapters/` layer.
/// It follows the Collection Metaphor from Evans' DDD:
///
/// - `add()` → `insert()`
/// - `remove()` → `delete()`
/// - `getById()` → `find_by_id()`
///
/// # Type Parameters
///
/// * `E` - The entity type that this repository manages
/// * `I` - The entity ID type
#[async_trait]
pub trait Repository<E: Entity, I: EntityId>:
    Send + Sync
{
    /// The entity type managed by this repository
    type Entity = E;

    /// The ID type for entities
    type Id = I;

    // ─────────────────────────────────────────────────────────────
    // CRUD Operations
    // ─────────────────────────────────────────────────────────────

    /// Insert a new entity into the repository.
    ///
    /// # Errors
    /// Returns `RepositoryError::AlreadyExists` if an entity with
    /// the same ID already exists.
    async fn insert(&self, entity: &E) -> StorageResult<()>;

    /// Update an existing entity in the repository.
    ///
    /// # Errors
    /// Returns `RepositoryError::NotFound` if the entity doesn't exist.
    async fn update(&self, entity: &E) -> StorageResult<()>;

    /// Delete an entity from the repository.
    ///
    /// # Errors
    /// Returns `RepositoryError::NotFound` if the entity doesn't exist.
    async fn delete(&self, id: &I) -> StorageResult<()>;

    /// Check if an entity exists by ID.
    async fn exists(&self, id: &I) -> StorageResult<bool>;

    // ─────────────────────────────────────────────────────────────
    // Query Operations
    // ─────────────────────────────────────────────────────────────

    /// Find an entity by its ID.
    ///
    /// # Errors
    /// Returns `RepositoryError::NotFound` if the entity doesn't exist.
    async fn find_by_id(&self, id: &I) -> StorageResult<Option<E>>;

    /// Find all entities (use with caution on large datasets).
    async fn find_all(&self) -> StorageResult<Vec<E>>;

    /// Find entities matching a filter condition.
    async fn find_by<F>(&self, filter: F) -> StorageResult<Vec<E>>
    where
        F: Fn(&E) -> bool + Send + Sync;

    /// Find a single entity matching a filter.
    async fn find_one_by<F>(&self, filter: F) -> StorageResult<Option<E>>
    where
        F: Fn(&E) -> bool + Send + Sync;
}

// ─────────────────────────────────────────────────────────────────
// Repository extensions for common patterns
// ─────────────────────────────────────────────────────────────────

/// Extension trait providing additional query methods.
#[async_trait]
pub trait RepositoryExtensions<E: Entity, I: EntityId>:
    Repository<E, I>
{
    /// Find entities by IDs (batch operation).
    async fn find_by_ids(&self, ids: &[I]) -> StorageResult<Vec<E>> {
        let mut results = Vec::with_capacity(ids.len());
        for id in ids {
            if let Some(entity) = self.find_by_id(id).await? {
                results.push(entity);
            }
        }
        Ok(results)
    }

    /// Count entities matching a filter.
    async fn count_by<F>(&self, filter: F) -> StorageResult<usize>
    where
        F: Fn(&E) -> bool + Send + Sync,
    {
        let all = self.find_all().await?;
        Ok(all.into_iter().filter(&filter).count())
    }

    /// Check if any entity matches a filter.
    async fn exists_by<F>(&self, filter: F) -> StorageResult<bool>
    where
        F: Fn(&E) -> bool + Send + Sync,
    {
        Ok(self.find_one_by(filter).await?.is_some())
    }
}
