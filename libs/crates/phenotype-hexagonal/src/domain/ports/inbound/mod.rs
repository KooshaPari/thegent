//! Inbound Ports - Use cases that drive the domain
//! 
//! Inbound ports are the entry points into the domain. They represent
//! the actions that external actors (users, other systems) can perform.
//!
//! ## Naming Convention
//! 
//! - Commands: Actions that change state (Create, Update, Delete)
//! - Queries: Actions that read state without modification
//! - Processes: Long-running operations that may involve multiple steps
//!
//! ## Example
//! 
//! ```rust,ignore
//! #[async_trait]
//! pub trait CreateOrderPort {
//!     async fn create_order(&self, command: CreateOrderCommand) 
//!         -> Result<Order, CreateOrderError>;
//! }
//! ```

/// Marker trait for command handlers
pub trait CommandHandler<C, R>: Send + Sync {
    // Marker trait - implementations provide the handle method
}

/// Marker trait for query handlers
pub trait QueryHandler<Q, R>: Send + Sync {
    // Marker trait - implementations provide the handle method
}

/// Marker trait for process handlers
pub trait ProcessHandler<P, R>: Send + Sync {
    // Marker trait - implementations provide the handle method
}
