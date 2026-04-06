//! # Domain Events
//!
//! Immutable events representing state changes.
//!
//! ## Event Sourcing Principles
//!
//! - Events are immutable facts
//! - Append-only log
//! - Reconstruct state by replaying events

use std::time::SystemTime;

/// Domain events for the SHM bounded context
#[derive(Debug, Clone)]
pub enum ShmEvent {
    /// Command lock was acquired
    CommandLockAcquired {
        cmd_hash: String,
        pid: u32,
        timestamp: SystemTime,
    },
    /// Command lock was released
    CommandLockReleased {
        cmd_hash: String,
        pid: u32,
        timestamp: SystemTime,
    },
    /// Circuit breaker opened
    CircuitBreakerOpened {
        target: String,
        failures: u32,
        timestamp: SystemTime,
    },
    /// Circuit breaker closed
    CircuitBreakerClosed {
        target: String,
        timestamp: SystemTime,
    },
    /// Circuit breaker half-opened
    CircuitBreakerHalfOpened {
        target: String,
        timestamp: SystemTime,
    },
    /// Provider metrics updated
    ProviderMetricsUpdated {
        provider: String,
        success_rate: f32,
        timestamp: SystemTime,
    },
    /// XP earned
    XpEarned {
        agent_id: String,
        amount: u64,
        new_level: u32,
        timestamp: SystemTime,
    },
}

impl ShmEvent {
    /// Get the timestamp of the event
    pub fn timestamp(&self) -> SystemTime {
        match self {
            ShmEvent::CommandLockAcquired { timestamp, .. } => *timestamp,
            ShmEvent::CommandLockReleased { timestamp, .. } => *timestamp,
            ShmEvent::CircuitBreakerOpened { timestamp, .. } => *timestamp,
            ShmEvent::CircuitBreakerClosed { timestamp, .. } => *timestamp,
            ShmEvent::CircuitBreakerHalfOpened { timestamp, .. } => *timestamp,
            ShmEvent::ProviderMetricsUpdated { timestamp, .. } => *timestamp,
            ShmEvent::XpEarned { timestamp, .. } => *timestamp,
        }
    }
}
