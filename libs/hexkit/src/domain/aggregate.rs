//! Domain Aggregate - Cluster of Related Objects
//!
//! Aggregates are clusters of domain objects that form a transactional boundary.
//! An aggregate root is the single entity that is responsible for ensuring
//! the aggregate's invariants are maintained.
//!
//! ## Key Characteristics
//!
//! - **Boundary**: Defines a cluster of related entities and value objects
//! - **Root**: The aggregate root controls access to the entire aggregate
//! - **Invariants**: The aggregate root ensures consistency within the boundary
//! - **Transaction**: Changes to an aggregate are atomic
//!
//! ## Example
//!
//! ```rust,ignore
//! use hexkit::{AggregateRoot, Entity, EntityId, ValueObject, HexResult, HexError};
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
//!     status: String,
//! }
//!
//! impl Entity for Order {
//!     type Id = OrderId;
//!     fn id(&self) -> &Self::Id { &self.id }
//! }
//!
//! impl AggregateRoot for Order {
//!     fn validate_invariants(&self) -> HexResult<()> {
//!         Ok(())
//!     }
//! }
//! ```

use crate::domain::Entity;
use crate::HexResult;
use crate::domain::DomainEvent;

/// Marker trait for aggregate roots
pub trait AggregateRoot: Entity + Send + Sync {
    /// Check if the aggregate's invariants are satisfied
    fn validate_invariants(&self) -> HexResult<()>;
}

/// Extension trait for aggregate operations
pub trait AggregateRootExt: AggregateRoot {}

impl<T: AggregateRoot> AggregateRootExt for T {}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::*;
    use crate::HexError;

    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    struct TestId(String);

    impl std::fmt::Display for TestId {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{}", self.0)
        }
    }

    impl EntityId for TestId {}

    #[derive(Debug, Clone)]
    struct TestAggregate {
        id: TestId,
        value: i32,
    }

    impl Entity for TestAggregate {
        type Id = TestId;

        fn id(&self) -> &Self::Id {
            &self.id
        }
    }

    impl TestAggregate {
        pub fn new(id: TestId, value: i32) -> Self {
            Self { id, value }
        }
    }

    impl AggregateRoot for TestAggregate {
        fn validate_invariants(&self) -> HexResult<()> {
            if self.value < 0 {
                return Err(HexError::Validation("Value cannot be negative".to_string()));
            }
            Ok(())
        }
    }

    #[test]
    fn test_aggregate_validation() {
        let agg = TestAggregate::new(TestId("1".to_string()), 100);
        assert!(agg.validate_invariants().is_ok());
    }

    #[test]
    fn test_aggregate_invariant_violation() {
        let agg = TestAggregate::new(TestId("1".to_string()), -1);
        assert!(agg.validate_invariants().is_err());
    }
}
