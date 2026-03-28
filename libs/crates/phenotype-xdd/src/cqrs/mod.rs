//! Command Query Responsibility Segregation (CQRS)
//! 
//! CQRS separates read and write operations into different models.
//! 
//! ## Benefits
//! 
//! - Independent scaling of reads and writes
//! - Optimized read models for different use cases
//! - Clear separation of concerns
//! - Better performance for read-heavy workloads
//! 
//! ## CQRS Pattern
//! 
//! ```text
//! Commands (Write)           Queries (Read)
//!      │                         │
//!      ▼                         ▼
//! ┌─────────┐              ┌─────────┐
//! │ Command │              │  Query  │
//! │ Handler │              │ Handler │
//! └────┬────┘              └────┬────┘
//!      │                         │
//!      ▼                         ▼
//! ┌─────────┐              ┌─────────┐
//! │ Domain  │              │  Read   │
//! │ Model   │              │  Model  │
//! └────┬────┘              └────┬────┘
//!      │                         │
//!      ▼                         ▼
//! ┌─────────┐              ┌─────────┐
//! │ Write   │              │  Read   │
//! │ Database│              │ Database│
//! └─────────┘              └─────────┘
//! ```

/// Command - write operation that modifies state
#[derive(Debug, Clone)]
pub struct Command {
    pub id: String,
    pub command_type: String,
    pub payload: serde_json::Value,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

impl Command {
    pub fn new(command_type: impl Into<String>, payload: serde_json::Value) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            command_type: command_type.into(),
            payload,
            timestamp: chrono::Utc::now(),
        }
    }
}

/// Query - read operation that doesn't modify state
#[derive(Debug, Clone)]
pub struct Query {
    pub id: String,
    pub query_type: String,
    pub parameters: serde_json::Value,
}

impl Query {
    pub fn new(query_type: impl Into<String>, parameters: serde_json::Value) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            query_type: query_type.into(),
            parameters,
        }
    }
}

/// Command handler trait
#[async_trait::async_trait]
pub trait CommandHandler<C: Send + Sync>: Send + Sync {
    type Result: Send + Sync;
    type Error: std::error::Error + Send + Sync + 'static;
    
    async fn handle(&self, command: C) -> Result<Self::Result, Self::Error>;
}

/// Query handler trait
#[async_trait::async_trait]
pub trait QueryHandler<Q: Send + Sync, R: Send + Sync>: Send + Sync {
    type Error: std::error::Error + Send + Sync + 'static;
    
    async fn handle(&self, query: Q) -> Result<R, Self::Error>;
}

/// Read model projection
#[async_trait::async_trait]
pub trait Projection<E: Send + Sync>: Send + Sync {
    type ReadModel: Send + Sync + Clone;
    
    async fn project(&self, events: &[E]) -> Result<Self::ReadModel, ProjectionError>;
}

/// Projection error
#[derive(Debug)]
pub struct ProjectionError {
    pub message: String,
}

impl std::fmt::Display for ProjectionError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Projection error: {}", self.message)
    }
}

impl std::error::Error for ProjectionError {}
