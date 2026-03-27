//! # Helix Errors
//!
//! Comprehensive error handling primitives following hexagonal architecture principles.
//!
//! ## Features
//!
//! - **Context-aware errors**: Attach structured context to errors
//! - **Result type compatibility**: Seamless integration with `Result<T, E>`
//! - **Tracing support**: Optional integration with `tracing` crate
//! - **No_std support**: Core error types work without standard library
//! - **Serde support**: Optional serialization for error types
//!
//! ## Quick Start
//!
//! ```rust
//! use helix_errors::{Error, Context, Result};
//!
//! fn divide(a: i32, b: i32) -> Result<i32> {
//!     if b == 0 {
//!         Err(Error::invalid_input("division by zero"))
//!     } else {
//!         Ok(a / b)
//!     }
//! }
//! ```
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                      APPLICATION LAYER                       │
//! │  Error Context, Error Chain, Error Recovery Strategies     │
//! └─────────────────────────────────────────────────────────────┘
//!                              │
//!                              ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │                        DOMAIN LAYER                         │
//! │  Error Types, Error Traits, Error Codes, Error Categories   │
//! └─────────────────────────────────────────────────────────────┘
//!                              │
//!                              ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │                      INFRASTRUCTURE LAYER                    │
//! │  Tracing Integration, Serialization, Logging Adapters       │
//! └─────────────────────────────────────────────────────────────┘
//! ```

#![cfg_attr(not(feature = "std"), no_std)]
#![cfg_attr(not(feature = "std"), feature(alloc))]
#![forbid(unsafe_code)]
#![deny(missing_docs, clippy::all)]

#[cfg(not(feature = "std"))]
extern crate alloc;

mod domain;
mod application;
mod infrastructure;

pub use domain::*;
pub use application::*;
pub use infrastructure::*;

/// Re-export error kind for convenience
pub use ErrorKind;

/// Alias for Result with helix_errors::Error
pub type Result<T, E = Error> = core::result::Result<T, E>;
