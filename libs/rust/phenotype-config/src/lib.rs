//! # Phenotype Config Library
//!
//! A comprehensive configuration library for Rust following:
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
//! │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
//! │  │  Env Adapter     │  │  File Adapter    │  │  CLI Adapter    │    │
//! │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘    │
//! └───────────┼────────────────────┼───────────────────┼───────────────┘
//!             │                    │                   │
//!             v                    v                   v
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                      APPLICATION LAYER                              │
//! │  ┌─────────────────┐  ┌─────────────────┐                         │
//! │  │  ConfigLoader   │  │  ConfigBuilder  │                         │
//! │  └────────┬────────┘  └────────┬────────┘                         │
//! └───────────┼────────────────────┼───────────────────────────────────┘
//!             │                    │
//!             v                    v
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                         DOMAIN LAYER                                │
//! │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
//! │  │  ConfigValue    │  │  ConfigError    │  │  ConfigSource   │    │
//! │  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
//! └─────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! # Dependency Rule
//!
//! - `domain/` - ZERO external dependencies
//! - `application/` - Depends on domain only
//! - `adapters/` - Implement ports (env, file, cli)
//!
//! # Usage
//!
//! ```rust
//! use phenotype_config::{Config, ConfigBuilder, EnvConfigSource};
//!
//! let config = ConfigBuilder::new()
//!     .with_source(EnvConfigSource::with_prefix("APP"))
//!     .with_default("port", 8080)
//!     .build()?;
//!
//! let port: i64 = config.get("port")?;
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

/// Prelude module for convenient imports
pub mod prelude {
    pub use crate::domain::*;
    pub use crate::application::*;
}
