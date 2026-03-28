//! Outbound Ports - Interfaces for external dependencies
//! 
//! Outbound ports define what the domain needs from external systems.
//! These are implemented by secondary adapters.
//!
//! ## Port Categories
//! 
//! - **Repository Ports**: Persistence (CRUD operations)
//! - **Service Ports**: External service calls
//! - **Event Ports**: Event publishing
//! - **Cache Ports**: Caching operations
//!
//! ## Example
//! 
//! ```rust,ignore
//! #[async_trait]
//! pub trait OrderRepositoryPort: Send + Sync {
//!     async fn save(&self, order: Order) -> Result<(), RepositoryError>;
//!     async fn find_by_id(&self, id: OrderId) -> Result<Option<Order>, RepositoryError>;
//!     async fn find_by_customer(&self, customer_id: CustomerId) -> Result<Vec<Order>, RepositoryError>;
//! }
//! ```

use async_trait::async_trait;
use std::error::Error;

/// Generic repository port
#[async_trait]
pub trait RepositoryPort<E, Id>: Send + Sync {
    /// Error type for repository operations
    type Error: Error + Send + Sync + 'static;
    
    /// Save an entity
    async fn save(&self, entity: E) -> Result<(), Self::Error>;
    
    /// Find an entity by ID
    async fn find_by_id(&self, id: Id) -> Result<Option<E>, Self::Error>;
    
    /// Delete an entity by ID
    async fn delete(&self, id: Id) -> Result<(), Self::Error>;
}

/// Query repository port for read operations
#[async_trait]
pub trait QueryRepositoryPort<E, Id>: Send + Sync {
    /// Error type for repository operations
    type Error: Error + Send + Sync + 'static;
    
    /// Find an entity by ID
    async fn find_by_id(&self, id: Id) -> Result<Option<E>, Self::Error>;
    
    /// Find all entities
    async fn find_all(&self) -> Result<Vec<E>, Self::Error>;
}

/// Command repository port for write operations
#[async_trait]
pub trait CommandRepositoryPort<E>: Send + Sync {
    /// Error type for repository operations
    type Error: Error + Send + Sync + 'static;
    
    /// Save an entity
    async fn save(&self, entity: E) -> Result<(), Self::Error>;
    
    /// Delete an entity
    async fn delete(&self, entity: &E) -> Result<(), Self::Error>;
}
