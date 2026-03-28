//! Aggregate implementation
//!
//! Aggregates are clusters of related entities and value objects
//! that are treated as a single unit for data changes.

use super::entity::Entity;
use super::event::DomainEvent;
use chrono::{DateTime, Utc};

/// Aggregate root - the main entity that external code references
pub trait AggregateRoot: Entity + Send + Sync {
    type Event: DomainEvent;
    
    /// Get pending domain events
    fn pull_events(&mut self) -> Vec<Self::Event>;
}

/// Base aggregate root implementation
pub struct BaseAggregate<Id, E> {
    entity_id: Id,
    version: u64,
    pending_events: Vec<E>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

impl<Id, E> BaseAggregate<Id, E>
where
    Id: Send + Sync + Clone + PartialEq + std::fmt::Debug + std::fmt::Display,
    E: Clone + Send + Sync,
{
    pub fn new(id: Id) -> Self {
        let now = Utc::now();
        Self {
            entity_id: id,
            version: 1,
            pending_events: Vec::new(),
            created_at: now,
            updated_at: now,
        }
    }
    
    pub fn version(&self) -> u64 {
        self.version
    }
    
    pub fn increment_version(&mut self) {
        self.version += 1;
        self.updated_at = Utc::now();
    }
    
    pub fn add_event(&mut self, event: E) {
        self.pending_events.push(event);
        self.increment_version();
    }
    
    pub fn pull_events(&mut self) -> Vec<E> {
        std::mem::take(&mut self.pending_events)
    }
}

impl<Id, E> Entity for BaseAggregate<Id, E>
where
    Id: Send + Sync + Clone + PartialEq + std::fmt::Debug + std::fmt::Display,
    E: Clone + Send + Sync,
{
    type Id = Id;
    
    fn id(&self) -> &Self::Id {
        &self.entity_id
    }
}

/// Command for aggregate operations
pub trait AggregateCommand<A: AggregateRoot> {
    type Output;
    
    fn execute(&self, aggregate: &mut A) -> Self::Output;
}

/// Query for aggregate state
pub trait AggregateQuery<A: AggregateRoot> {
    type Output;
    
    fn execute(&self, aggregate: &A) -> Self::Output;
}
