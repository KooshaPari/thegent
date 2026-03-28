//! Ports layer - Interface definitions
//!
//! Ports define how the domain interacts with the outside world.
//! - Input Ports: How external systems drive the domain
//! - Output Ports: How the domain accesses external systems

pub mod input;
pub mod output;
pub mod repository;

pub use input::*;
pub use output::*;
pub use repository::*;
