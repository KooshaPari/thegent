//! Ports Layer - Abstract Interfaces
//!
//! Ports define the contracts between your application and the outside world.

pub mod inbound;
pub mod outbound;

// Re-exports
pub use inbound::{Command, CommandHandler, InputPort, Query, QueryHandler};
pub use outbound::OutputPort;
