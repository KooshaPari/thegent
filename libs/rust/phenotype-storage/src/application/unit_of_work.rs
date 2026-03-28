//! Unit of Work - Manages transactional boundaries.
//!
//! Following the Unit of Work pattern from PoEAA:
//! - Maintains a list of objects affected by a business transaction
//! - Coordinates the writing out of changes
//! - Coordinates the resolution of concurrency problems

use async_trait::async_trait;

use crate::domain::{Entity, EntityId, Repository, RepositoryError, StorageResult};

/// Unit of Work - Coordinates database operations within a transaction.
///
/// The Unit of Work pattern ensures:
/// - All changes are held in memory until commit
/// - Changes are applied atomically
/// - Optimistic locking prevents lost updates
pub trait UnitOfWork: Send + Sync {
    /// The repositories accessed in this unit of work
    fn repositories(&self) -> Vec<&str>;

    /// Commit all changes
    async fn commit(&mut self) -> StorageResult<()>;

    /// Rollback all changes
    async fn rollback(&mut self) -> StorageResult<()>;

    /// Start a new transaction
    async fn begin(&mut self) -> StorageResult<()>;

    /// Check if a transaction is active
    fn is_active(&self) -> bool;
}

/// Unit of Work for a single aggregate type.
#[async_trait]
pub trait UnitOfWorkFor<E, I>: UnitOfWork
where
    E: Entity<Id = I>,
    I: EntityId,
{
    /// Get the repository for this aggregate
    fn repo(&self) -> &dyn Repository<E, I>;

    /// Get a mutable reference to the repository
    fn repo_mut(&mut self) -> &mut dyn Repository<E, I>;
}

/// Extension for UnitOfWork to add repository operations.
#[async_trait]
pub trait UnitOfWorkExtensions {
    /// Execute operations within a unit of work.
    async fn execute<F, T>(&mut self, f: F) -> StorageResult<T>
    where
        F: FnOnce(&mut dyn UnitOfWork) -> StorageResult<T>;

    /// Execute operations with automatic rollback on error.
    async fn execute_with_rollback<F, T>(&mut self, f: F) -> StorageResult<T>
    where
        F: FnOnce(&mut dyn UnitOfWork) -> StorageResult<T>;
}

/// Macro to implement UnitOfWork for a struct with repositories.
#[macro_export]
macro_rules! impl_unit_of_work {
    ($name:ident { $($repo_name:ident: $repo_type:ty),* $(,)? }) => {
        impl UnitOfWork for $name {
            fn repositories(&self) -> Vec<&str> {
                vec![$(stringify!($repo_name)),*]
            }

            async fn commit(&mut self) -> StorageResult<()> {
                $(self.$repo_name.commit().await?;)*
                Ok(())
            }

            async fn rollback(&mut self) -> StorageResult<()> {
                $(self.$repo_name.rollback().await?;)*
                Ok(())
            }

            async fn begin(&mut self) -> StorageResult<()> {
                $(self.$repo_name.begin().await?;)*
                self.is_transaction_active = true;
                Ok(())
            }

            fn is_active(&self) -> bool {
                self.is_transaction_active
            }
        }
    };
}
