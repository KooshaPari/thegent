//! Adapters layer - Infrastructure implementations.
//!
//! This layer contains adapters that implement the ports defined in domain.
//!
//! Adapters:
//!   - EnvAdapter: Environment variable adapter
//!   - FileAdapter: File-based configuration adapter

pub mod env_adapter;
pub mod file_adapter;

pub use env_adapter::*;
pub use file_adapter::*;
