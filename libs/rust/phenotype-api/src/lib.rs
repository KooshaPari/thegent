//! # Phenotype API Library
//!
//! A comprehensive HTTP API library for Rust following:
//!   - Hexagonal Architecture (Ports & Adapters)
//!   - Clean Architecture principles
//!   - SOLID principles
//!   - xDD methodologies (TDD)
//!
//! # Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                         ADAPTERS                                     │
//! │  ┌─────────────────┐  ┌─────────────────┐                          │
//! │  │  ReqwestAdapter │  │  NativeAdapter  │                          │
//! │  └────────┬────────┘  └────────┬────────┘                          │
//! └───────────┼────────────────────┼──────────────────────────────────┘
//!             │                    │
//!             v                    v
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                      APPLICATION LAYER                              │
//! │  ┌─────────────────┐  ┌─────────────────┐                         │
//! │  │  ApiClient      │  │  RetryStrategy  │                         │
//! │  └────────┬────────┘  └────────┬────────┘                         │
//! └───────────┼────────────────────┼──────────────────────────────────┘
//!             │                    │
//!             v                    v
//! ┌─────────────────────────────────────────────────────────────────────┐
//! │                         DOMAIN LAYER                                │
//! │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
//! │  │  Http types     │  │  ApiError       │  │  Request/Response│  │
//! │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
//! └─────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! # Usage
//!
//! ```rust
//! use phenotype_api::{ApiClient, ApiError, Request};
//!
//! let client = ApiClient::new();
//! let response = client.send(Request::get("https://api.example.com/users")).await?;
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
