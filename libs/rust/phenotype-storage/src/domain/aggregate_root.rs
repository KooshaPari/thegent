//! Aggregate root - Domain concept for consistency boundaries.
//!
//! Following DDD aggregate pattern:
//! - Root entity that enforces invariants
//! - All changes go through the aggregate
//! - Guarantees consistency within the boundary

use std::fmt::Debug;

use crate::domain::{EntityId, RepositoryError, StorageResult};

/// Aggregate root - the entry point for a consistency boundary.
///
/// An aggregate is a cluster of associated entities and value objects
/// that are treated as a single unit for data changes.
///
/// Rules (from Evans' DDD):
/// 1. Aggregate root is the only member of the aggregate that
///    outside objects are allowed to hold references to
/// 2. Changes to objects within the aggregate boundary can only
///    be performed through the aggregate root
/// 3. The aggregate root can delegate changes to its parts
pub trait AggregateRoot: Send + Sync {
    /// The ID type for this aggregate
    type Id: EntityId;

    /// Get the ID of this aggregate
    fn id(&self) -> &Self::Id;

    /// Get the version for optimistic locking
    fn version(&self) -> u64;

    /// Increment the version (called internally)
    fn increment_version(&mut self);

    /// Mark the aggregate as deleted
    fn mark_deleted(&mut self);

    /// Check if the aggregate is deleted
    fn is_deleted(&self) -> bool;
}

/// Command to create a new aggregate.
pub struct CreateAggregate<C> {
    /// Command data
    pub command: C,
}

/// Command to update an existing aggregate.
pub struct UpdateAggregate<C> {
    /// Aggregate ID
    pub id: <Self::Aggregate as AggregateRoot>::Id,
    /// Command data
    pub command: C,
    /// Expected version for optimistic locking
    pub expected_version: u64,
}

pub trait Aggregate: AggregateRoot {
    /// Associated command types
    type CreateCommand;
    type UpdateCommand;
    type DeleteCommand;

    /// Apply a create command
    fn apply_create(cmd: Self::CreateCommand) -> Result<Self, RepositoryError>
    where
        Self: Sized;

    /// Apply an update command
    fn apply_update(&mut self, cmd: Self::UpdateCommand) -> Result<(), RepositoryError>;

    /// Apply a delete command
    fn apply_delete(&mut self, _cmd: Self::DeleteCommand) -> Result<(), RepositoryError> {
        self.mark_deleted();
        Ok(())
    }
}
