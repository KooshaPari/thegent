//! In-memory repository adapter - For testing and development.
//!
//! This adapter provides an in-memory implementation of the Repository trait
//! for testing purposes and development without a database.

use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

use crate::domain::{Entity, EntityId, Repository, RepositoryError, StorageResult};

/// In-memory repository implementation.
///
/// This adapter stores entities in a HashMap and is useful for:
/// - Unit testing
/// - Development without a database
/// - Caching scenarios
pub struct InMemoryRepository<E, I>
where
    E: Entity<Id = I>,
    I: EntityId,
{
    /// Storage for entities
    storage: Arc<RwLock<HashMap<I, E>>>,
    /// Storage for deleted entity IDs
    deleted: Arc<RwLock<Vec<I>>>,
}

impl<E, I> InMemoryRepository<E, I>
where
    E: Entity<Id = I>,
    I: EntityId,
{
    /// Create a new in-memory repository
    pub fn new() -> Self {
        Self {
            storage: Arc::new(RwLock::new(HashMap::new())),
            deleted: Arc::new(RwLock::new(Vec::new())),
        }
    }

    /// Create from existing data
    pub fn with_data(data: Vec<E>) -> Self {
        let storage = data.into_iter().map(|e| (e.id().clone(), e)).collect();
        Self {
            storage: Arc::new(RwLock::new(storage)),
            deleted: Arc::new(RwLock::new(Vec::new())),
        }
    }

    /// Clear all data
    pub async fn clear(&self) {
        self.storage.write().await.clear();
        self.deleted.write().await.clear();
    }

    /// Get the number of entities
    pub async fn len(&self) -> usize {
        self.storage.read().await.len()
    }

    /// Check if empty
    pub async fn is_empty(&self) -> bool {
        self.storage.read().await.is_empty()
    }
}

impl<E, I> Default for InMemoryRepository<E, I>
where
    E: Entity<Id = I>,
    I: EntityId,
{
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl<E, I> Repository<E, I> for InMemoryRepository<E, I>
where
    E: Entity<Id = I>,
    I: EntityId,
{
    async fn insert(&self, entity: &E) -> StorageResult<()> {
        let id = entity.id().clone();
        let mut storage = self.storage.write().await;

        if storage.contains_key(&id) {
            return Err(RepositoryError::already_exists::<E>(
                format!("{:?}", std::any::type_name::<E>()),
                &id.to_string(),
            ));
        }

        storage.insert(id, entity.clone());
        Ok(())
    }

    async fn update(&self, entity: &E) -> StorageResult<()> {
        let id = entity.id().clone();
        let mut storage = self.storage.write().await;

        if !storage.contains_key(&id) {
            return Err(RepositoryError::not_found::<E>(
                format!("{:?}", std::any::type_name::<E>()),
                &id.to_string(),
            ));
        }

        storage.insert(id, entity.clone());
        Ok(())
    }

    async fn delete(&self, id: &I) -> StorageResult<()> {
        let mut storage = self.storage.write().await;
        let mut deleted = self.deleted.write().await;

        if storage.remove(id).is_none() {
            return Err(RepositoryError::not_found::<E>(
                format!("{:?}", std::any::type_name::<E>()),
                &id.to_string(),
            ));
        }

        deleted.push(id.clone());
        Ok(())
    }

    async fn exists(&self, id: &I) -> StorageResult<bool> {
        Ok(self.storage.read().await.contains_key(id))
    }

    async fn find_by_id(&self, id: &I) -> StorageResult<Option<E>> {
        Ok(self.storage.read().await.get(id).cloned())
    }

    async fn find_all(&self) -> StorageResult<Vec<E>> {
        Ok(self.storage.read().await.values().cloned().collect())
    }

    async fn find_by<F>(&self, filter: F) -> StorageResult<Vec<E>>
    where
        F: Fn(&E) -> bool + Send + Sync,
    {
        let storage = self.storage.read().await;
        Ok(storage.values().filter(|e| filter(e)).cloned().collect())
    }

    async fn find_one_by<F>(&self, filter: F) -> StorageResult<Option<E>>
    where
        F: Fn(&E) -> bool + Send + Sync,
    {
        let storage = self.storage.read().await;
        Ok(storage.values().find(|e| filter(e)).cloned())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fmt::Debug;

    #[derive(Clone, Debug, PartialEq)]
    struct TestId(String);

    impl EntityId for TestId {
        fn generate() -> Self {
            TestId(uuid::Uuid::new_v4().to_string())
        }

        fn from_string(s: &str) -> Option<Self> {
            Some(TestId(s.to_string()))
        }

        fn to_string(&self) -> String {
            self.0.clone()
        }
    }

    #[derive(Clone, Debug, PartialEq)]
    struct TestEntity {
        id: TestId,
        name: String,
    }

    impl Entity for TestEntity {
        type Id = TestId;

        fn id(&self) -> &Self::Id {
            &self.id
        }
    }

    #[tokio::test]
    async fn test_insert_and_find() {
        let repo = InMemoryRepository::<TestEntity, TestId>::new();
        let entity = TestEntity {
            id: TestId::generate(),
            name: "Test".to_string(),
        };

        repo.insert(&entity).await.unwrap();
        let found = repo.find_by_id(entity.id()).await.unwrap();

        assert_eq!(found, Some(entity));
    }

    #[tokio::test]
    async fn test_duplicate_insert() {
        let repo = InMemoryRepository::<TestEntity, TestId>::new();
        let entity = TestEntity {
            id: TestId::generate(),
            name: "Test".to_string(),
        };

        repo.insert(&entity).await.unwrap();
        let result = repo.insert(&entity).await;

        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_delete() {
        let repo = InMemoryRepository::<TestEntity, TestId>::new();
        let entity = TestEntity {
            id: TestId::generate(),
            name: "Test".to_string(),
        };

        repo.insert(&entity).await.unwrap();
        repo.delete(entity.id()).await.unwrap();
        let found = repo.find_by_id(entity.id()).await.unwrap();

        assert_eq!(found, None);
    }
}
