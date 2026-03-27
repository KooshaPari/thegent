//! Domain layer - Pure business logic with no external dependencies

pub mod entities;
pub mod value_objects;
pub mod services;
pub mod events;

pub use entities::*;
pub use value_objects::*;
pub use services::*;
pub use events::*;
