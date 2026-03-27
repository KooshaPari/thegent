//! Outbound ports - Secondary/driven ports (repositories, external services)

#[cfg(feature = "async")]
use async_trait::async_trait;

/// Marker trait for outbound ports
pub trait OutboundPort: Send + Sync {}

/// Repository port - basic CRUD operations
#[cfg(feature = "async")]
#[async_trait]
pub trait Repository<E, Id>: OutboundPort
where
    E: Send + Sync,
    Id: Send + Sync,
{
    /// Find an entity by ID
    async fn find_by_id(&self, id: Id) -> Option<E>;

    /// Find all entities matching a filter
    async fn find_all(&self) -> Vec<E>;

    /// Save an entity
    async fn save(&self, entity: E) -> Result<E, RepositoryError>;

    /// Delete an entity by ID
    async fn delete(&self, id: Id) -> Result<bool, RepositoryError>;
}

/// Query repository port - read operations
#[cfg(feature = "async")]
#[async_trait]
pub trait QueryRepository<E>: OutboundPort
where
    E: Send + Sync,
{
    /// Find entities matching a query
    async fn find(&self, query: impl Query) -> Vec<E>;

    /// Find a single entity matching a query
    async fn find_one(&self, query: impl Query) -> Option<E>;

    /// Count entities matching a query
    async fn count(&self, query: impl Query) -> usize;
}

/// Query trait for filtering
pub trait Query: Send + Sync {
    /// Check if an entity matches the query
    fn matches<E>(&self, entity: &E) -> bool;

    /// Get the SQL filter string (for SQL-based implementations)
    fn to_sql(&self) -> Option<String> {
        None
    }
}

/// Unit query - matches everything
pub struct UnitQuery;

impl Query for UnitQuery {
    fn matches<E>(&self, _entity: &E) -> bool {
        true
    }
}

/// Repository error types
#[derive(Debug, thiserror::Error)]
pub enum RepositoryError {
    /// Entity was not found in the repository
    #[error("Entity not found")]
    NotFound,

    /// Entity already exists - duplicate key
    #[error("Duplicate entity: {0}")]
    Duplicate(String),

    /// Connection error to the data store
    #[error("Connection error: {0}")]
    Connection(String),

    /// Transaction error
    #[error("Transaction error: {0}")]
    Transaction(String),

    /// Validation error
    #[error("Validation error: {0}")]
    Validation(String),

    /// Unknown repository error
    #[error("Unknown error: {0}")]
    Unknown(String),
}

/// Event publisher port
#[cfg(feature = "async")]
#[async_trait]
pub trait EventPublisher<E>: OutboundPort
where
    E: Send + Sync,
{
    /// Publish an event
    async fn publish(&self, event: E) -> Result<(), PublisherError>;

    /// Publish multiple events
    async fn publish_batch(&self, events: Vec<E>) -> Result<(), PublisherError>;
}

/// Publisher error types
#[derive(Debug, thiserror::Error)]
pub enum PublisherError {
    /// Connection error to the message broker
    #[error("Connection error: {0}")]
    Connection(String),

    /// Error serializing the event
    #[error("Serialization error: {0}")]
    Serialization(String),

    /// Event was rejected by the publisher
    #[error("Rejected: {0}")]
    Rejected(String),

    /// Unknown publisher error
    #[error("Unknown error: {0}")]
    Unknown(String),
}

/// External client port
#[cfg(feature = "async")]
#[async_trait]
pub trait ExternalClient<Request, Response>: OutboundPort
where
    Request: Send + Sync,
    Response: Send + Sync,
{
    /// Call the external service
    async fn call(&self, request: Request) -> Result<Response, ClientError>;
}

/// Client error types
#[derive(Debug, thiserror::Error)]
pub enum ClientError {
    /// Network error when calling the external service
    #[error("Network error: {0}")]
    Network(String),

    /// Request timeout
    #[error("Timeout")]
    Timeout,

    /// Authentication error
    #[error("Authentication error")]
    Authentication,

    /// Authorization error
    #[error("Authorization error")]
    Authorization,

    /// Rate limited by the external service
    #[error("Rate limited")]
    RateLimited,

    /// Server error from the external service
    #[error("Server error: {0}")]
    Server(String),

    /// Invalid response from the external service
    #[error("Invalid response: {0}")]
    InvalidResponse(String),

    /// Unknown client error
    #[error("Unknown error: {0}")]
    Unknown(String),
}

/// Cache port
#[cfg(feature = "async")]
#[async_trait]
pub trait Cache<K, V>: OutboundPort
where
    K: Send + Sync,
    V: Send + Sync,
{
    /// Get a value from cache
    async fn get(&self, key: &K) -> Option<V>;

    /// Set a value in cache
    async fn set(&self, key: K, value: V) -> Result<(), CacheError>;

    /// Delete a value from cache
    async fn delete(&self, key: &K) -> Result<bool, CacheError>;

    /// Clear the cache
    async fn clear(&self) -> Result<(), CacheError>;
}

/// Cache error types
#[derive(Debug, thiserror::Error)]
pub enum CacheError {
    /// Connection error to the cache store
    #[error("Connection error: {0}")]
    Connection(String),

    /// Serialization error
    #[error("Serialization error: {0}")]
    Serialization(String),

    /// Key not found in the cache
    #[error("Key not found")]
    NotFound,

    /// Unknown cache error
    #[error("Unknown error: {0}")]
    Unknown(String),
}
