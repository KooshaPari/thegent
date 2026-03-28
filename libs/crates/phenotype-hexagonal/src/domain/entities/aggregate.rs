//! Aggregate Root - Encapsulates entities and value objects
//! 
//! Aggregates are clusters of associated entities and value objects
//! that form a transactional consistency boundary. The Aggregate Root
//! is the single entity that external objects interact with.
//!
//! ## Key Characteristics
//! 
//! - **Boundary**: Defines the consistency boundary
//! - **Root**: Single entry point for the aggregate
//! - **Invariant**: Ensures internal consistency
//!
//! ## Rules
//! 
//! 1. External objects hold references only to the Aggregate Root
//! 2. Changes within the aggregate are atomic
//! 3. The Aggregate Root enforces invariants

use crate::domain::{Entity, DomainEvent};
use std::fmt::Debug;

/// Aggregate root trait
pub trait AggregateRoot: Entity + Debug {
    /// The pending events that have occurred
    fn pending_events(&self) -> &[Box<dyn DomainEvent>];
    
    /// Clear pending events after they've been applied
    fn clear_pending_events(&mut self);
}

/// Extension trait for aggregate operations
pub trait AggregateExt: AggregateRoot {
    /// Check if there are pending uncommitted events
    fn has_pending_events(&self) -> bool {
        !self.pending_events().is_empty()
    }
    
    /// Take and consume all pending events
    fn take_pending_events(&mut self) -> Vec<Box<dyn DomainEvent>>
    where
        Self: Sized
    {
        let events = self.pending_events().iter().cloned().collect();
        self.clear_pending_events();
        events
    }
}

impl<A: AggregateRoot> AggregateExt for A {}
