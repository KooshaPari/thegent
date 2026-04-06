//! # Use Cases
//!
//! Application services that orchestrate domain logic.
//!
//! ## CQRS Pattern
//!
//! - **Commands**: Operations that change state
//! - **Queries**: Operations that read state without side effects

use crate::ports::driven::{CircuitBreakerPort, CommandCachePort, EventPort};
use crate::domain::events::ShmEvent;
use std::time::SystemTime;

/// Use case for acquiring a command lock
pub struct AcquireLockUseCase<T: CommandCachePort, E: EventPort> {
    cache: T,
    events: E,
}

impl<T: CommandCachePort, E: EventPort> AcquireLockUseCase<T, E> {
    pub fn new(cache: T, events: E) -> Self {
        Self { cache, events }
    }

    pub fn execute(&mut self, cmd_hash: String, pid: u32) -> Result<(), String> {
        self.cache.acquire_lock(&cmd_hash, pid)?;
        self.events.publish(ShmEvent::CommandLockAcquired {
            cmd_hash,
            pid,
            timestamp: SystemTime::now(),
        })?;
        Ok(())
    }
}

/// Use case for releasing a command lock
pub struct ReleaseLockUseCase<T: CommandCachePort, E: EventPort> {
    cache: T,
    events: E,
}

impl<T: CommandCachePort, E: EventPort> ReleaseLockUseCase<T, E> {
    pub fn new(cache: T, events: E) -> Self {
        Self { cache, events }
    }

    pub fn execute(&mut self, cmd_hash: String, pid: u32) -> Result<(), String> {
        self.cache.release_lock(&cmd_hash, pid)?;
        self.events.publish(ShmEvent::CommandLockReleased {
            cmd_hash,
            pid,
            timestamp: SystemTime::now(),
        })?;
        Ok(())
    }
}

/// Use case for circuit breaker operations
pub struct CircuitBreakerUseCase<T: CircuitBreakerPort, E: EventPort> {
    breakers: T,
    events: E,
}

impl<T: CircuitBreakerPort, E: EventPort> CircuitBreakerUseCase<T, E> {
    pub fn new(breakers: T, events: E) -> Self {
        Self { breakers, events }
    }

    pub fn record_success(&mut self, target: String) -> Result<(), String> {
        self.breakers.record_success(&target)?;
        self.events.publish(ShmEvent::CircuitBreakerClosed {
            target,
            timestamp: SystemTime::now(),
        })?;
        Ok(())
    }

    pub fn record_failure(&mut self, target: String) -> Result<(), String> {
        self.breakers.record_failure(&target)?;
        // Check if breaker opened
        if let Some(breaker) = self.breakers.get_breaker(&target) {
            if breaker.state == crate::domain::value_objects::CircuitState::Open {
                self.events.publish(ShmEvent::CircuitBreakerOpened {
                    target,
                    failures: breaker.failures,
                    timestamp: SystemTime::now(),
                })?;
            }
        }
        Ok(())
    }
}
