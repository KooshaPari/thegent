//! # In-Memory Adapters
//!
//! Pure in-memory implementations for testing.
//!
//! ## Usage
//!
//! ```rust
//! use thegent_shm::adapters::inmemory::InMemoryCommandCache;
//! use thegent_shm::ports::driven::CommandCachePort;
//!
//! let mut cache = InMemoryCommandCache::new();
//! cache.acquire_lock("test", 1234).unwrap();
//! ```

use std::collections::HashMap;
use crate::domain::entities::{CircuitBreaker, CommandLock};
use crate::domain::value_objects::LockStatus;
use crate::domain::events::ShmEvent;
use crate::ports::driven::{CircuitBreakerPort, CommandCachePort, EventPort};

/// In-memory command cache implementation
pub struct InMemoryCommandCache {
    locks: HashMap<String, CommandLock>,
}

impl InMemoryCommandCache {
    pub fn new() -> Self {
        Self { locks: HashMap::new() }
    }
}

impl Default for InMemoryCommandCache {
    fn default() -> Self {
        Self::new()
    }
}

impl CommandCachePort for InMemoryCommandCache {
    fn acquire_lock(&mut self, cmd_hash: &str, pid: u32) -> Result<(), String> {
        if let Some(lock) = self.locks.get_mut(cmd_hash) {
            if lock.is_locked() && lock.pid != pid {
                return Err(format!("Lock held by PID {}", lock.pid));
            }
            lock.pid = pid;
            lock.status = LockStatus::Locked;
        } else {
            let mut lock = CommandLock::new(cmd_hash);
            let _ = lock.acquire(pid, None);
            self.locks.insert(cmd_hash.to_string(), lock);
        }
        Ok(())
    }

    fn release_lock(&mut self, cmd_hash: &str, pid: u32) -> Result<(), String> {
        if let Some(lock) = self.locks.get_mut(cmd_hash) {
            if lock.pid != pid {
                return Err(format!("Lock held by PID {}", lock.pid));
            }
            lock.pid = 0;
            lock.status = LockStatus::Unlocked;
        }
        Ok(())
    }

    fn get_lock(&self, cmd_hash: &str) -> Option<CommandLock> {
        self.locks.get(cmd_hash).cloned()
    }

    fn list_locks(&self) -> Vec<CommandLock> {
        self.locks.values().cloned().collect()
    }
}

/// In-memory circuit breaker implementation
pub struct InMemoryCircuitBreaker {
    breakers: HashMap<String, CircuitBreaker>,
}

impl InMemoryCircuitBreaker {
    pub fn new() -> Self {
        Self { breakers: HashMap::new() }
    }
}

impl Default for InMemoryCircuitBreaker {
    fn default() -> Self {
        Self::new()
    }
}

impl CircuitBreakerPort for InMemoryCircuitBreaker {
    fn record_success(&mut self, target: &str) -> Result<(), String> {
        let cb = self.breakers.entry(target.to_string()).or_insert_with(|| {
            CircuitBreaker::new(target, 5)
        });
        cb.record_success();
        Ok(())
    }

    fn record_failure(&mut self, target: &str) -> Result<(), String> {
        let cb = self.breakers.entry(target.to_string()).or_insert_with(|| {
            CircuitBreaker::new(target, 5)
        });
        cb.record_failure();
        Ok(())
    }

    fn get_breaker(&self, target: &str) -> Option<CircuitBreaker> {
        self.breakers.get(target).cloned()
    }

    fn list_breakers(&self) -> Vec<CircuitBreaker> {
        self.breakers.values().cloned().collect()
    }
}

/// In-memory event store
pub struct InMemoryEventStore {
    events: Vec<ShmEvent>,
}

impl InMemoryEventStore {
    pub fn new() -> Self {
        Self { events: Vec::new() }
    }
}

impl Default for InMemoryEventStore {
    fn default() -> Self {
        Self::new()
    }
}

impl EventPort for InMemoryEventStore {
    fn publish(&mut self, event: ShmEvent) -> Result<(), String> {
        self.events.push(event);
        Ok(())
    }

    fn get_events_since(&self, timestamp: std::time::SystemTime) -> Vec<ShmEvent> {
        self.events.iter()
            .filter(|e| e.timestamp() > timestamp)
            .cloned()
            .collect()
    }
}
