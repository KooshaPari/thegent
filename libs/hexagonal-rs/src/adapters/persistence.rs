//! Persistence Adapter
//!
//! This adapter provides database persistence implementations.

use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use crate::HexagonalResult;
use crate::domain::Entity;
use crate::ports::repository::Repository;

/// In-memory repository implementation.
pub struct InMemoryRepository<E>
where
    E: Entity + Send + Sync + Clone,
{
    entities: RwLock<HashMap<String, E>>,
}

impl<E> InMemoryRepository<E>
where
    E: Entity + Send + Sync + Clone,
{
    pub fn new() -> Self {
        Self {
            entities: RwLock::new(HashMap::new()),
        }
    }
}

impl<E> Default for InMemoryRepository<E>
where
    E: Entity + Send + Sync + Clone,
{
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl<E> Repository<E> for InMemoryRepository<E>
where
    E: Entity + Send + Sync + Clone,
{
    async fn save(&self, entity: E) -> HexagonalResult<E> {
        let id = entity.id().to_string();
        let mut entities = self
            .entities
            .write()
            .map_err(|_| crate::HexagonalError::Adapter("repository lock poisoned".to_string()))?;
        entities.insert(id, entity.clone());
        Ok(entity)
    }

    async fn find_by_id(&self, id: &E::Id) -> HexagonalResult<Option<E>> {
        let entities = self
            .entities
            .read()
            .map_err(|_| crate::HexagonalError::Adapter("repository lock poisoned".to_string()))?;
        Ok(entities.get(&id.to_string()).cloned())
    }

    async fn delete(&self, id: &E::Id) -> HexagonalResult<()> {
        let mut entities = self
            .entities
            .write()
            .map_err(|_| crate::HexagonalError::Adapter("repository lock poisoned".to_string()))?;
        entities.remove(&id.to_string());
        Ok(())
    }

    async fn exists(&self, id: &E::Id) -> HexagonalResult<bool> {
        let entities = self
            .entities
            .read()
            .map_err(|_| crate::HexagonalError::Adapter("repository lock poisoned".to_string()))?;
        Ok(entities.contains_key(&id.to_string()))
    }

    async fn find_all(&self) -> HexagonalResult<Vec<E>> {
        let entities = self
            .entities
            .read()
            .map_err(|_| crate::HexagonalError::Adapter("repository lock poisoned".to_string()))?;
        Ok(entities.values().cloned().collect())
    }

    async fn find_by_ids(&self, ids: Vec<E::Id>) -> HexagonalResult<Vec<E>> {
        let entities = self
            .entities
            .read()
            .map_err(|_| crate::HexagonalError::Adapter("repository lock poisoned".to_string()))?;
        Ok(ids
            .into_iter()
            .filter_map(|id| entities.get(&id.to_string()).cloned())
            .collect())
    }
}

/// Repository that wraps another with caching.
pub struct CachedRepository<R, E>
where
    R: Repository<E>,
    E: Entity + Send + Sync + Clone,
{
    inner: Arc<R>,
    cache: Arc<InMemoryRepository<E>>,
}

impl<R, E> CachedRepository<R, E>
where
    R: Repository<E>,
    E: Entity + Send + Sync + Clone,
{
    pub fn new(inner: Arc<R>) -> Self {
        Self {
            inner,
            cache: Arc::new(InMemoryRepository::new()),
        }
    }
}

#[async_trait]
impl<R, E> Repository<E> for CachedRepository<R, E>
where
    R: Repository<E>,
    E: Entity + Send + Sync + Clone,
{
    async fn save(&self, entity: E) -> HexagonalResult<E> {
        let result = self.inner.save(entity).await?;
        self.cache.save(result.clone()).await?;
        Ok(result)
    }

    async fn find_by_id(&self, id: &E::Id) -> HexagonalResult<Option<E>> {
        if let Some(cached) = self.cache.find_by_id(id).await? {
            return Ok(Some(cached));
        }

        let result = self.inner.find_by_id(id).await?;
        if let Some(ref entity) = result {
            self.cache.save(entity.clone()).await?;
        }
        Ok(result)
    }

    async fn delete(&self, id: &E::Id) -> HexagonalResult<()> {
        self.inner.delete(id).await?;
        self.cache.delete(id).await?;
        Ok(())
    }

    async fn exists(&self, id: &E::Id) -> HexagonalResult<bool> {
        self.inner.exists(id).await
    }

    async fn find_all(&self) -> HexagonalResult<Vec<E>> {
        self.inner.find_all().await
    }

    async fn find_by_ids(&self, ids: Vec<E::Id>) -> HexagonalResult<Vec<E>> {
        self.inner.find_by_ids(ids).await
    }
}
