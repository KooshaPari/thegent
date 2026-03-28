//! Repository Pattern Implementation

use crate::ports::outbound::OutputPort;

/// Repository port marker
pub trait Repository<T>: OutputPort {}
