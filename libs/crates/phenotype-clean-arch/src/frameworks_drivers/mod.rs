//! Frameworks & Drivers Layer
//! 
//! The outermost layer - contains tools like databases, web frameworks.
//! This layer generally contains code that deals with I/O.

pub mod database;
pub mod web;
pub mod external;

pub use database::*;
pub use web::*;
pub use external::*;
