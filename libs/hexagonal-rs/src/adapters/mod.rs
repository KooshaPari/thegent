//! Adapters layer - Infrastructure implementations
//!
//! Adapters implement the output ports and expose input ports.
//! Examples: REST API, gRPC, CLI, Database persistence, etc.

pub mod rest;
pub mod persistence;
pub mod messaging;

pub use rest::*;
pub use persistence::*;
pub use messaging::*;
