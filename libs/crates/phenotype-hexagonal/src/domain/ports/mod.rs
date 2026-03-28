//! Ports - Interface definitions for hexagonal architecture
//! 
//! Ports are the boundaries of the domain. They define what the domain
//! needs from the outside world (outbound) and what the outside world
//! can do with the domain (inbound).
//!
//! ## Port Types
//!
//! - **Inbound Ports**: Use cases and commands that drive the domain
//! - **Outbound Ports**: Interfaces for external dependencies
//!
//! ## Dependency Rule
//! 
//! Ports are defined in the domain layer but implemented in adapters.
//! The domain depends only on abstractions (traits).

pub mod inbound;
pub mod outbound;

pub use inbound::*;
pub use outbound::*;
