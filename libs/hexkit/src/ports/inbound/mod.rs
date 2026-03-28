//! Inbound Ports - Use Cases and Commands
//!
//! Inbound ports (also called "primary" or "driving" ports) define the entry points
//! into your application's domain logic. These are the operations that can be
//! triggered by external actors (users, systems, UI, etc.).
//!
//! ## Port Types
//!
//! ### Commands
//! Operations that change state. Commands are named in imperative mood:
//! - `CreateOrderCommand`
//! - `UpdateCustomerCommand`
//! - `CancelReservationCommand`
//!
//! ### Queries
//! Operations that read state without modification. Queries are named as questions:
//! - `GetOrderQuery`
//! - `ListProductsQuery`
//! - `SearchCustomersQuery`
//!
//! ## Implementation Pattern
//! ## Example
//!
//! ```rust,ignore
//! use hexkit::ports::inbound::{CommandHandler, Command, InputPort};
//! use hexkit::HexResult;
//!
//! #[derive(Debug)]
//! pub struct CreateOrderCommand;
//!
//! impl Command for CreateOrderCommand {}
//!
//! #[derive(Debug)]
//! pub struct CreateOrderUseCase;
//!
//! #[async_trait]
//! impl CommandHandler<CreateOrderCommand> for CreateOrderUseCase {
//!     type Output = String;
//!
//!     async fn handle(&self, _cmd: CreateOrderCommand) -> HexResult<Self::Output> {
//!         Ok("Order created".to_string())
//!     }
//! }
//! ```
use crate::HexResult;

// Marker traits for command/query categorization
pub trait CommandMarker: Send + Sync {}
pub trait QueryMarker: Send + Sync {}
pub trait InputPortMarker: Send + Sync {}

/// Base input port trait
pub trait InputPort: Send + Sync {
    type Marker: InputPortMarker;
}

/// Command handler trait
#[async_trait::async_trait]
pub trait CommandHandler<C: Command>: Send + Sync {
    type Output;
    async fn handle(&self, cmd: C) -> HexResult<Self::Output>;
}

/// Query handler trait
#[async_trait::async_trait]
pub trait QueryHandler<Q: Query>: Send + Sync {
    type Output;
    async fn handle(&self, query: Q) -> HexResult<Self::Output>;
}

// Base command/query interfaces
pub trait Command: Send + Sync + Sized {
    type Output;
}

pub trait Query: Send + Sync + Sized {
    type Output;
}
