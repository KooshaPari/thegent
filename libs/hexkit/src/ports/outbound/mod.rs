//! Outbound Ports - Dependencies and Adapters
//!
//! Outbound ports (also called "secondary" or "driven" ports) define what your
//! application needs from external systems. These are the dependencies your
//! domain and application layers require to function.
//!
//! ## Port Types
//!
//! ### Repository Ports
//! For persisting and retrieving domain objects:
//! - `Repository<T>` - CRUD operations
//! - `AggregateRepository<T>` - Aggregate-specific operations
//! - `EventStore<T>` - Event persistence
//!
//! ### External Service Ports
//! For calling external systems:
//! - `EmailServicePort` - Send emails
//! - `PaymentServicePort` - Process payments
//! - `NotificationPort` - Send notifications
//!
//! ### Messaging Ports
//! For asynchronous communication:
//! - `MessagePublisher<T>` - Publish events/messages
//! - `MessageConsumer<T>` - Consume messages
//! - `EventBus<T>` - Publish domain events
//!
//! ## Design Principles
//!
//! 1. **Interface Segregation**: Keep ports small and focused
//! 2. **Dependency Inversion**: Application depends on abstractions
//! 3. **No Implementation**: Ports contain no business logic
//! 4. **Technology Agnostic**: Ports don't reference specific technologies
//!
//! ## Example
//!
//! ```rust,ignore
//! use hexkit::ports::outbound::OutputPort;
//! use hexkit::HexResult;
//!
//! #[async_trait]
//! pub trait UserRepositoryPort: OutputPort {
//!     async fn find_by_id(&self, id: String) -> HexResult<Option<String>>;
//!     async fn save(&self, user: String) -> HexResult<()>;
//! }
//! ```

/// Base output port trait
pub trait OutputPort: Send + Sync {}

// Marker traits for port categorization
pub trait RepositoryMarker: OutputPort {}
pub trait ServiceMarker: OutputPort {}
pub trait MessagingMarker: OutputPort {}
