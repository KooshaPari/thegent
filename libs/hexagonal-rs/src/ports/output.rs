//! Output Ports - How the domain accesses external systems
//!
//! Output ports define the interfaces that the domain uses to interact
//! with external systems (databases, message queues, etc.)

use crate::HexagonalResult;
use async_trait::async_trait;

/// Marker trait for output ports (driven ports)
pub trait OutputPort: Send + Sync {}

/// Async output port marker
#[async_trait]
pub trait AsyncOutputPort: Send + Sync {}

/// Repository port for persistence
#[async_trait]
pub trait RepositoryPort<T>: OutputPort {
    async fn save(&self, entity: T) -> HexagonalResult<T>;
    async fn find_by_id(&self, id: &str) -> HexagonalResult<Option<T>>;
    async fn delete(&self, id: &str) -> HexagonalResult<()>;
    async fn find_all(&self) -> HexagonalResult<Vec<T>>;
}

/// Query repository for read operations
#[async_trait]
pub trait QueryRepositoryPort<T>: OutputPort {
    async fn find_by_filter(&self, filter: Filter) -> HexagonalResult<Vec<T>>;
    async fn count(&self, filter: Filter) -> HexagonalResult<u64>;
}

/// Event store port for event sourcing
#[async_trait]
pub trait EventStorePort<E>: OutputPort {
    async fn append(&self, aggregate_id: &str, events: Vec<E>, expected_version: u64) -> HexagonalResult<()>;
    async fn get_events(&self, aggregate_id: &str) -> HexagonalResult<Vec<E>>;
    async fn get_all_events(&self, from_version: u64) -> HexagonalResult<Vec<(String, Vec<E>)>>;
}

/// Message bus port for publishing events
#[async_trait]
pub trait MessageBusPort<E>: OutputPort {
    async fn publish(&self, topic: &str, event: E) -> HexagonalResult<()>;
    async fn publish_batch(&self, topic: &str, events: Vec<E>) -> HexagonalResult<()>;
}

/// External service port
#[async_trait]
pub trait ExternalServicePort<T, R>: OutputPort {
    async fn call(&self, request: T) -> HexagonalResult<R>;
}

/// Filter for query operations
#[derive(Debug, Clone, Default)]
pub struct Filter {
    pub conditions: Vec<Condition>,
    pub limit: Option<usize>,
    pub offset: Option<usize>,
}

impl Filter {
    pub fn new() -> Self {
        Self::default()
    }
    
    pub fn add_condition(mut self, condition: Condition) -> Self {
        self.conditions.push(condition);
        self
    }
    
    pub fn with_limit(mut self, limit: usize) -> Self {
        self.limit = Some(limit);
        self
    }
    
    pub fn with_offset(mut self, offset: usize) -> Self {
        self.offset = Some(offset);
        self
    }
}

#[derive(Debug, Clone)]
pub enum Condition {
    Eq(String, String),
    Ne(String, String),
    Gt(String, String),
    Lt(String, String),
    Gte(String, String),
    Lte(String, String),
    Contains(String, String),
    StartsWith(String, String),
}
