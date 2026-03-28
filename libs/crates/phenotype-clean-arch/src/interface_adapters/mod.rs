//! Interface Adapters Layer
//! 
//! Convert data between formats convenient for entities/use cases
//! and formats convenient for external agencies.

pub mod controllers;
pub mod presenters;
pub mod gateways;

pub use controllers::*;
pub use presenters::*;
pub use gateways::*;
