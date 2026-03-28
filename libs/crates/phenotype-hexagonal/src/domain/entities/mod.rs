//! Entities - Domain objects with identity
//! 
//! Entities are domain objects that have a distinct identity that runs
//! through time and different representations of the same conceptual
//! entity.
//!
//! ## Key Characteristics
//! 
//! - **Identity**: Each entity has a unique identifier
//! - **Lifecycle**: Entities evolve through state changes
//! - **Equality**: Two entities are equal if they have the same ID
//!
//! ## Example
//! 
//! ```rust,ignore
//! pub struct Order {
//!     id: OrderId,
//!     customer_id: CustomerId,
//!     items: Vec<OrderItem>,
//!     status: OrderStatus,
//!     created_at: DateTime,
//! }
//! ```

pub mod entity;
pub mod aggregate;
pub mod identifier;

pub use entity::Entity;
pub use aggregate::AggregateRoot;
pub use identifier::Identifier;
