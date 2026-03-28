//! Repository traits
//!
//! Repository pattern provides a collection-like interface
//! for accessing domain objects.

use async_trait::async_trait;
use crate::HexagonalResult;
use crate::domain::Entity;
use std::sync::Arc;

/// Repository trait for entity persistence.
#[async_trait]
pub trait Repository<E>: Send + Sync
where
    E: Entity + Send + Sync + Clone,
{
    async fn save(&self, entity: E) -> HexagonalResult<E>;
    async fn find_by_id(&self, id: &E::Id) -> HexagonalResult<Option<E>>;
    async fn delete(&self, id: &E::Id) -> HexagonalResult<()>;
    async fn exists(&self, id: &E::Id) -> HexagonalResult<bool>;
    async fn find_all(&self) -> HexagonalResult<Vec<E>>;
    async fn find_by_ids(&self, ids: Vec<E::Id>) -> HexagonalResult<Vec<E>>;
}

/// Async repository with pagination.
#[async_trait]
pub trait PagedRepository<E>: Repository<E>
where
    E: Entity + Send + Sync + Clone,
{
    async fn find_page(&self, page: usize, page_size: usize) -> HexagonalResult<Vec<E>>;
    async fn count_all(&self) -> HexagonalResult<u64>;
}

/// Specification-based repository.
#[async_trait]
pub trait SpecRepository<E>: Repository<E>
where
    E: Entity + Send + Sync + Clone,
{
    async fn find_by_spec(&self, spec: &dyn RepositorySpec<E>) -> HexagonalResult<Vec<E>>;
    async fn find_one_by_spec(&self, spec: &dyn RepositorySpec<E>) -> HexagonalResult<Option<E>>;
}

/// Specification trait for repository queries.
pub trait RepositorySpec<E>: Send + Sync
where
    E: Entity + Send + Sync + Clone,
{
    fn is_satisfied_by(&self, entity: &E) -> bool;
    fn to_predicate(&self) -> String;
}

/// Unit of work pattern for transactional operations.
#[async_trait]
pub trait UnitOfWork: Send + Sync {
    type Entity: Entity + Send + Sync + Clone;

    async fn begin(&mut self) -> HexagonalResult<()>;
    async fn commit(&mut self) -> HexagonalResult<()>;
    async fn rollback(&mut self) -> HexagonalResult<()>;
    async fn repository(&self) -> Arc<dyn Repository<Self::Entity>>;
}

/// Factory for creating repositories.
pub trait RepositoryFactory<E>: Send + Sync
where
    E: Entity + Send + Sync + Clone,
{
    fn create(&self) -> Arc<dyn Repository<E>>;
}

/// Mapper for converting between domain and persistence models.
pub trait RepositoryMapper<D, P>: Send + Sync {
    fn to_domain(&self, persistence: P) -> D;
    fn to_persistence(&self, domain: D) -> P;
}
