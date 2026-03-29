//! Nexus - Service Registry and Discovery
//!
//! A service registry and discovery library with hash-consign based state management.

pub mod registry;
pub mod service;
pub mod discovery;
pub mod error;
pub mod health;

pub use registry::Registry;
pub use service::{Service, Endpoint};
pub use discovery::Discovery;
pub use error::NexusError;
pub use health::{HealthMonitor, HealthStatus, HealthCheckConfig, ServiceHealth};
