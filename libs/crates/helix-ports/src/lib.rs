//! # Helix Ports
//!
//! Hexagonal architecture port interfaces - the foundation for clean, testable architectures.
//!
//! ## Overview
//!
//! This crate provides the foundational port interfaces for hexagonal/clean architecture:
//! - **Inbound Ports**: Primary/driving ports (use cases)
//! - **Outbound Ports**: Secondary/driven ports (repositories, external services)
//! - **Adapter Traits**: Standard implementations for common patterns
//!
//! ## Architecture
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                    PRIMARY ADAPTERS                          │
//! │            HTTP Controllers, CLI, GraphQL                    │
//! └─────────────────────────┬───────────────────────────────────┘
//!                           │
//!                           ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │                   INBOUND PORTS                              │
//! │        Use Cases, Commands, Queries, Handlers                 │
//! └─────────────────────────┬───────────────────────────────────┘
//!                           │
//!                           ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │                      DOMAIN                                 │
//! │     Entities, Value Objects, Domain Services, Events         │
//! └─────────────────────────┬───────────────────────────────────┘
//!                           │
//!                           ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │                  OUTBOUND PORTS                             │
//! │      Repository, Publisher, Client, External Service          │
//! └─────────────────────────┬───────────────────────────────────┘
//!                           │
//!                           ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │                  SECONDARY ADAPTERS                          │
//! │       Postgres, Redis, Kafka, HTTP, gRPC, Filesystem         │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Key Concepts
//!
//! ### Ports
//!
//! Ports are interfaces defined by the domain. They come in two flavors:
//!
//! - **Inbound Ports**: Define what the application can do (use cases)
//! - **Outbound Ports**: Define what the application needs from infrastructure
//!
//! ### Adapters
//!
//! Adapters are implementations of ports. They also come in two flavors:
//!
//! - **Primary/Inbound Adapters**: Drive the application (HTTP, CLI)
//! - **Secondary/Outbound Adapters**: Are driven by the application (DB, Cache)
//!
//! ## Example
//!
//! ```rust
//! use helix_ports::{InboundPort, OutboundPort, UseCase};
//! use async_trait::async_trait;
//!
//! // Define an outbound port (repository)
//! #[async_trait]
//! pub trait UserRepository: Send + Sync {
//!     async fn find_by_id(&self, id: Uuid) -> Option<User>;
//!     async fn save(&self, user: User) -> Result<User>;
//! }
//!
//! // Define an inbound port (use case)
//! #[async_trait]
//! pub trait GetUserUseCase: Send + Sync {
//!     async fn execute(&self, id: Uuid) -> Option<User>;
//! }
//!
//! // Implement the use case
//! pub struct GetUserService<R: UserRepository> {
//!     repository: Arc<R>,
//! }
//!
//! #[async_trait]
//! impl<R: UserRepository> GetUserUseCase for GetUserService<R> {
//!     async fn execute(&self, id: Uuid) -> Option<User> {
//!         self.repository.find_by_id(id).await
//!     }
//! }
//! ```

#![forbid(unsafe_code)]
#![deny(missing_docs, clippy::all)]

#[cfg(feature = "async")]
pub mod inbound;
pub mod outbound;
pub mod error;
pub mod result;

pub mod prelude;

pub use inbound::*;
pub use outbound::*;
pub use error::*;
pub use result::*;
