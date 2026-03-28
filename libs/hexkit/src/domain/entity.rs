//! Domain Entity - Objects with Identity
//!
//! Entities are domain objects that have a distinct identity that persists
//! through their lifetime. Unlike value objects, two entities with the same
//! attributes but different IDs are considered different.
//!
//! ## Key Characteristics
//!
//! - **Identity**: Entities have a unique identifier
//! - **Equality**: Two entities are equal if their IDs are equal
//! - **Mutability**: Entities can change their state
//! - **Lifecycle**: Entities have a meaningful identity from creation to deletion
//!
//! ## Example
//!
//! ```rust,ignore
//! use hexkit::{Entity, EntityId, ValueObject};
//!
//! #[derive(Debug, Clone, PartialEq, Eq, Hash)]
//! pub struct OrderId(String);
//!
//! impl ValueObject for OrderId {
//!     fn validate(&self) -> Result<(), String> { Ok(()) }
//! }
//! impl EntityId for OrderId {}
//!
//! #[derive(Debug, Clone)]
//! pub struct Order {
//!     id: OrderId,
//! }
//!
//! impl Entity for Order {
//!     type Id = OrderId;
//!     fn id(&self) -> &Self::Id { &self.id }
//! }
//! ```

use std::hash::Hash;
use std::fmt::Debug;

/// Marker trait for entity IDs
pub trait EntityId: Send + Sync + Clone + PartialEq + Eq + Hash + Debug + 'static {}

/// Trait for domain entities with identity
pub trait Entity: Send + Sync {
    /// The type of entity ID
    type Id: EntityId;

    /// Get the entity's ID
    fn id(&self) -> &Self::Id;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    struct TestId(String);

    impl EntityId for TestId {}

    #[derive(Debug, Clone)]
    struct TestEntity {
        id: TestId,
    }

    impl Entity for TestEntity {
        type Id = TestId;

        fn id(&self) -> &Self::Id {
            &self.id
        }
    }

    #[test]
    fn test_entity_identity() {
        let entity1 = TestEntity {
            id: TestId("123".to_string()),
        };
        let entity2 = TestEntity {
            id: TestId("123".to_string()),
        };
        let entity3 = TestEntity {
            id: TestId("456".to_string()),
        };

        // Same ID = same entity
        assert_eq!(entity1.id(), entity2.id());
        // Different ID = different entity
        assert_ne!(entity1.id(), entity3.id());
    }
}
