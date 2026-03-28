//! Repository factory - Creates repository instances.
//!
//! Following the Factory pattern:
//! - Abstracts the creation of repositories
//! - Supports different storage backends
//! - Dependency injection friendly

use std::sync::Arc;

use crate::domain::{Entity, EntityId, Repository, StorageResult};

/// Repository factory - Creates repository instances.
///
/// The factory abstracts the creation of repositories:
/// - Allows swapping storage backends
/// - Manages connection pooling
/// - Supports test doubles
pub trait RepositoryFactory: Send + Sync {
    /// Get a repository by type
    fn get<E, I>(&self) -> Arc<dyn Repository<E, I>>
    where
        E: Entity<Id = I>,
        I: EntityId,
        Self: Sized;
}

/// Repository registry - Type-erased repository storage.
pub struct RepositoryRegistry {
    repositories: std::collections::HashMap<String, Box<dyn std::any::Any + Send + Sync>>,
}

impl RepositoryRegistry {
    /// Create a new empty registry
    pub fn new() -> Self {
        Self {
            repositories: std::collections::HashMap::new(),
        }
    }

    /// Register a repository
    pub fn register<E, I, R>(&mut self, name: &str, repo: R)
    where
        E: Entity<Id = I>,
        I: EntityId,
        R: Repository<E, I> + 'static,
    {
        self.repositories.insert(
            name.to_string(),
            Box::new(Arc::new(repo) as Arc<dyn Repository<E, I>>),
        );
    }

    /// Get a repository by name
    pub fn get<E, I>(&self, name: &str) -> Option<Arc<dyn Repository<E, I>>>
    where
        E: Entity<Id = I>,
        I: EntityId,
    {
        self.repositories
            .get(name)
            .and_then(|any| any.downcast_ref::<Arc<dyn Repository<E, I>>>().cloned())
    }
}

impl Default for RepositoryRegistry {
    fn default() -> Self {
        Self::new()
    }
}
