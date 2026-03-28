//! Domain layer - Pure CLI concepts with ZERO external dependencies.

pub mod command;
pub mod argument;
pub mod error;
pub mod context;

pub use command::*;
pub use argument::*;
pub use error::*;
pub use context::*;
