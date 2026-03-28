//! # Phenotype CLI Library
//!
//! A comprehensive CLI framework library for Rust following:
//!   - Hexagonal Architecture (Ports & Adapters)
//!   - Clean Architecture principles
//!   - SOLID principles
//!   - xDD methodologies (TDD, DDD)
//!
//! # Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                         ADAPTERS                                     │
//! │  ┌─────────────────┐  ┌─────────────────┐                          │
//! │  │  ClapAdapter     │  │  ColorAdapter   │                          │
//! │  └────────┬────────┘  └────────┬────────┘                          │
//! └───────────┼────────────────────┼───────────────────────────────────┘
//!             │                    │
//!             v                    v
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                      APPLICATION LAYER                              │
//! │  ┌─────────────────┐  ┌─────────────────┐                         │
//! │  │  CommandRunner  │  │  HelpFormatter  │                         │
//! │  └────────┬────────┘  └────────┬────────┘                         │
//! └───────────┼────────────────────┼───────────────────────────────────┘
//!             │                    │
//!             v                    v
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                         DOMAIN LAYER                                │
//! │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
//! │  │  Command        │  │  Argument       │  │  CliError       │   │
//! │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
//! └─────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! # Usage
//!
//! ```rust
//! use phenotype_cli::{Command, Argument, CliError};
//!
//! let cmd = Command::new("greet")
//!     .about("Greet someone")
//!     .arg(Argument::new("name").required(true))
//!     .run(|ctx| {
//!         println!("Hello, {}!", ctx.get::<String>("name"));
//!     });
//! ```
//!
//! # License
//! MIT

#![forbid(unsafe_code)]
#![warn(missing_docs, missing_debug_implementations)]

pub mod domain;
pub mod application;
pub mod adapters;

pub use domain::*;
pub use application::*;
pub use adapters::*;

/// Prelude for convenient imports
pub mod prelude {
    pub use crate::domain::*;
}
