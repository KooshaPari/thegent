//! Entity - Base trait for domain entities.
//!
//! Following DDD entity pattern:
//! - Objects with a distinct identity
//! - Equality based on ID, not attributes
//! - Can change over time but maintain identity

use std::fmt::Debug;

use async_trait::async_trait;

/// Entity ID - Value object for entity identity.
pub trait EntityId: Clone + Debug + PartialEq + Send + Sync {
    /// Generate a new unique ID
    fn generate() -> Self;

    /// Parse from string representation
    fn from_string(s: &str) -> Option<Self>;

    /// Convert to string representation
    fn to_string(&self) -> String;
}

/// Entity - A domain object with identity.
///
/// Entities have the following characteristics:
/// - They are defined by their identity, not their attributes
/// - Two entities with the same ID are considered equal
/// - They can change over time (unlike Value Objects)
pub trait Entity: Send + Sync {
    /// The ID type for this entity
    type Id: EntityId;

    /// Get the unique identifier for this entity
    fn id(&self) -> &Self::Id;

    /// Check if this entity is the same as another (by ID)
    fn is_same(&self, other: &Self) -> bool {
        self.id() == other.id()
    }
}

/// Marker trait for entities that can be persisted.
#[async_trait]
pub trait Persistable: Entity {
    /// The entity type for database mapping
    type PersistenceDto: Send + Sync;

    /// Convert to persistence DTO
    fn to_dto(&self) -> Self::PersistenceDto;

    /// Create from persistence DTO
    fn from_dto(dto: Self::PersistenceDto) -> Result<Self, RepositoryError>
    where
        Self: Sized;
}
