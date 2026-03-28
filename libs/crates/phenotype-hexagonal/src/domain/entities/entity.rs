//! Entity trait and implementation helpers
//! 
//! An Entity is a domain object with identity that persists through time.
//! Two entities are equal if and only if they have the same identity.

use crate::domain::Identifier;

/// Marker trait for entities
pub trait Entity: Sized {
    /// The identifier type for this entity
    type Id: Identifier;
    
    /// Returns the unique identifier of this entity
    fn id(&self) -> &Self::Id;
    
    /// Checks if this entity is the same as another
    fn equals(&self, other: &Self) -> bool {
        self.id() == other.id()
    }
}

/// Extension trait for entity operations
pub trait EntityExt: Entity {
    /// Returns true if this entity is transient (not yet persisted)
    fn is_transient(&self) -> bool {
        self.id().is_transient()
    }
    
    /// Returns true if this entity has been persisted
    fn is_persisted(&self) -> bool {
        !self.is_transient()
    }
}

impl<E: Entity> EntityExt for E {}
