//! Domain layer - Pure metrics concepts with ZERO external dependencies.

pub mod metric;
pub mod metric_type;
pub mod metric_error;
pub mod label;

pub use metric::*;
pub use metric_type::*;
pub use metric_error::*;
pub use label::*;
