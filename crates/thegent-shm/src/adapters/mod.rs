//! # Adapters Layer
//!
//! Infrastructure implementations of ports.
//!
//! ## Adapter Types
//!
//! - **In-Memory**: For testing and development
//! - **Shared Memory**: Production implementation
//! - **File System**: Persistence adapter

pub mod inmemory;
pub mod sharedmemory;
