//! # Driven Ports (Secondary Ports)
//!
//! Interfaces that the domain defines and infrastructure must implement.
//!
//! These ports are consumed by the domain and implemented by adapters.

use crate::domain::entities::{CircuitBreaker, CommandLock, HealthScore};
use crate::domain::events::ShmEvent;
use crate::domain::value_objects::ProviderMetrics;

/// Port for command lock operations (DRIVEN)
///
/// ## CQRS: Commands
pub trait CommandCachePort {
    /// Acquire a command lock
    fn acquire_lock(&mut self, cmd_hash: &str, pid: u32) -> Result<(), String>;

    /// Release a command lock
    fn release_lock(&mut self, cmd_hash: &str, pid: u32) -> Result<(), String>;

    /// Get lock status
    fn get_lock(&self, cmd_hash: &str) -> Option<CommandLock>;

    /// List all locks
    fn list_locks(&self) -> Vec<CommandLock>;
}

/// Port for circuit breaker operations (DRIVEN)
pub trait CircuitBreakerPort {
    /// Record a success for a target
    fn record_success(&mut self, target: &str) -> Result<(), String>;

    /// Record a failure for a target
    fn record_failure(&mut self, target: &str) -> Result<(), String>;

    /// Get circuit breaker state
    fn get_breaker(&self, target: &str) -> Option<CircuitBreaker>;

    /// List all circuit breakers
    fn list_breakers(&self) -> Vec<CircuitBreaker>;
}

/// Port for health monitoring (DRIVEN)
pub trait HealthPort {
    /// Get overall health score
    fn get_health(&self) -> HealthScore;

    /// Set component health
    fn set_component_health(&mut self, name: &str, score: f32) -> Result<(), String>;

    /// Check if system is healthy
    fn is_healthy(&self) -> bool;
}

/// Port for provider metrics (DRIVEN)
pub trait MetricsPort {
    /// Record a provider success
    fn record_provider_success(&mut self, provider: &str, latency_ms: u32) -> Result<(), String>;

    /// Record a provider failure
    fn record_provider_failure(&mut self, provider: &str) -> Result<(), String>;

    /// Get provider metrics
    fn get_provider_metrics(&self, provider: &str) -> Option<ProviderMetrics>;

    /// List all provider metrics
    fn list_providers(&self) -> Vec<ProviderMetrics>;
}

/// Port for event publishing (DRIVEN)
pub trait EventPort {
    /// Publish a domain event
    fn publish(&mut self, event: ShmEvent) -> Result<(), String>;

    /// Get all events since a timestamp
    fn get_events_since(&self, timestamp: std::time::SystemTime) -> Vec<ShmEvent>;
}
