//! Domain layer - Core business logic with zero external dependencies
//! 
//! This module contains:
//! - Entities: Domain objects with identity
//! - Value Objects: Immutable objects without identity
//! - Services: Domain operations
//! - Events: Domain events
//! - Ports: Interface definitions (inbound and outbound)
//!
//! ## Dependency Rule
//! 
//! The domain layer has ZERO external dependencies. All external concerns
//! are handled through ports (interfaces).
//!
//! ## Architecture
//! 
//! ```text
//! ┌─────────────────────────────────────┐
//! │           Domain Core               │
//! │  ┌─────────────────────────────┐   │
//! │  │         Entities           │   │
//! │  │    (Identity + State)     │   │
//! │  └─────────────────────────────┘   │
//! │  ┌─────────────────────────────┐   │
//! │  │      Value Objects         │   │
//! │  │   (Immutable, Composed)    │   │
//! │  └─────────────────────────────┘   │
//! │  ┌─────────────────────────────┐   │
//! │  │        Services             │   │
//! │  │   (Business Operations)     │   │
//! │  └─────────────────────────────┘   │
//! │  ┌─────────────────────────────┐   │
//! │  │        Events              │   │
//! │  │    (Domain Events)         │   │
//! │  └─────────────────────────────┘   │
//! │  ┌─────────────────────────────┐   │
//! │  │         Ports              │   │
//! │  │  (Inbound + Outbound)      │   │
//! │  └─────────────────────────────┘   │
//! └─────────────────────────────────────┘
//! ```

pub mod entities;
pub mod value_objects;
pub mod services;
pub mod events;
pub mod ports;

pub use entities::*;
pub use value_objects::*;
pub use services::*;
pub use events::*;
pub use ports::*;
