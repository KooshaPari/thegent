//! Domain layer - Pure HTTP/API concepts with ZERO external dependencies.
//!
//! Following ADR-001 dependency rule:
//! - domain/ contains ZERO external dependencies

pub mod http;
pub mod error;
pub mod request;
pub mod response;

pub use http::*;
pub use error::*;
pub use request::*;
pub use response::*;
