//! # Domain Entities
//!
//! Core business objects with identity.
//!
//! ## DDD Entity Principles
//!
//! - Entities have unique identity (id)
//! - Equality based on identity, not attributes
//! - Mutable state managed through domain methods

use super::value_objects::{CircuitState, LockStatus};
use std::time::SystemTime;

/// Circuit Breaker Entity
///
/// Protects downstream services from cascading failures.
/// Follows the Circuit Breaker pattern (Michael Nygard).
#[derive(Debug, Clone)]
pub struct CircuitBreaker {
    /// Unique identifier (target service name)
    pub target: String,
    /// Current state of the circuit
    pub state: CircuitState,
    /// Number of consecutive failures
    pub failures: u32,
    /// Failure threshold before opening circuit
    pub threshold: u32,
    /// Timestamp of last failure
    pub last_failure: Option<SystemTime>,
    /// Timestamp when circuit was opened
    pub opened_at: Option<SystemTime>,
}

impl CircuitBreaker {
    /// Create a new circuit breaker for a target service.
    pub fn new(target: impl Into<String>, threshold: u32) -> Self {
        Self {
            target: target.into(),
            state: CircuitState::Closed,
            failures: 0,
            threshold,
            last_failure: None,
            opened_at: None,
        }
    }

    /// Record a successful call.
    pub fn record_success(&mut self) {
        self.failures = 0;
        if matches!(self.state, CircuitState::Open) {
            self.state = CircuitState::Closed;
            self.opened_at = None;
        }
    }

    /// Record a failed call.
    pub fn record_failure(&mut self) {
        self.failures += 1;
        self.last_failure = Some(SystemTime::now());

        if self.failures >= self.threshold && matches!(self.state, CircuitState::Closed) {
            self.state = CircuitState::Open;
            self.opened_at = Some(SystemTime::now());
        }
    }

    /// Check if the circuit allows requests.
    pub fn allows_request(&self) -> bool {
        !matches!(self.state, CircuitState::Open)
    }

    /// Attempt to transition from Open to HalfOpen.
    pub fn try_reset(&mut self, timeout_secs: u64) -> bool {
        if matches!(self.state, CircuitState::Open) {
            if let Some(opened) = self.opened_at {
                if let Ok(duration) = opened.elapsed() {
                    if duration.as_secs() >= timeout_secs {
                        self.state = CircuitState::HalfOpen;
                        return true;
                    }
                }
            }
        }
        false
    }

    /// Transition to Open state from HalfOpen on failure.
    pub fn trip(&mut self) {
        self.state = CircuitState::Open;
        self.opened_at = Some(SystemTime::now());
    }
}

/// Command Lock Entity
///
/// Implements command deduplication for cmd_share functionality.
#[derive(Debug, Clone)]
pub struct CommandLock {
    /// Unique command hash
    pub cmd_hash: String,
    /// Process ID holding the lock (0 if unlocked)
    pub pid: u32,
    /// Current status of the lock
    pub status: LockStatus,
    /// Path to output file for command results
    pub output_path: Option<String>,
    /// When the lock was acquired
    pub start_time: Option<SystemTime>,
}

impl CommandLock {
    /// Create a new unlocked command lock.
    pub fn new(cmd_hash: impl Into<String>) -> Self {
        Self {
            cmd_hash: cmd_hash.into(),
            pid: 0,
            status: LockStatus::Unlocked,
            output_path: None,
            start_time: None,
        }
    }

    /// Acquire the lock for a process.
    pub fn acquire(&mut self, pid: u32, output_path: Option<String>) -> Result<(), LockError> {
        if self.pid != 0 && self.status == LockStatus::Locked {
            return Err(LockError::AlreadyLocked {
                current_pid: self.pid,
                requested_pid: pid,
            });
        }
        self.pid = pid;
        self.status = LockStatus::Locked;
        self.output_path = output_path;
        self.start_time = Some(SystemTime::now());
        Ok(())
    }

    /// Release the lock.
    pub fn release(&mut self, pid: u32) -> Result<(), LockError> {
        if self.pid != pid {
            return Err(LockError::NotOwner {
                lock_holder: self.pid,
                requestor: pid,
            });
        }
        self.pid = 0;
        self.status = LockStatus::Unlocked;
        self.start_time = None;
        Ok(())
    }

    /// Check if lock is held.
    pub fn is_locked(&self) -> bool {
        self.pid != 0 && self.status == LockStatus::Locked
    }
}

/// Errors for lock operations
#[derive(Debug, Clone, thiserror::Error)]
pub enum LockError {
    #[error("Lock already held by PID {current_pid}, requested by PID {requested_pid}")]
    AlreadyLocked { current_pid: u32, requested_pid: u32 },

    #[error("Lock held by PID {lock_holder}, cannot release by PID {requestor}")]
    NotOwner { lock_holder: u32, requestor: u32 },
}

/// Health Score Entity
#[derive(Debug, Clone, Default)]
pub struct HealthScore {
    pub components: std::collections::HashMap<String, f32>,
    _private: (),
}

impl HealthScore {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn set_component(&mut self, name: impl Into<String>, score: f32) {
        let name = name.into();
        self.components.insert(name, score.clamp(0.0, 1.0));
    }

    pub fn overall(&self) -> f32 {
        if self.components.is_empty() {
            return 1.0;
        }
        let sum: f32 = self.components.values().sum();
        sum / self.components.len() as f32
    }

    pub fn is_healthy(&self) -> bool {
        self.overall() >= 0.8
    }

    pub fn is_degraded(&self) -> bool {
        let overall = self.overall();
        (0.5..0.8).contains(&overall)
    }

    pub fn is_unhealthy(&self) -> bool {
        self.overall() < 0.5
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_circuit_breaker_creation() {
        let cb = CircuitBreaker::new("api.example.com", 5);
        assert_eq!(cb.target, "api.example.com");
        assert_eq!(cb.state, CircuitState::Closed);
        assert_eq!(cb.failures, 0);
    }

    #[test]
    fn test_circuit_breaker_opens_after_threshold() {
        let mut cb = CircuitBreaker::new("api.example.com", 3);
        cb.record_failure();
        cb.record_failure();
        assert_eq!(cb.state, CircuitState::Closed);
        cb.record_failure();
        assert_eq!(cb.state, CircuitState::Open);
    }

    #[test]
    fn test_circuit_breaker_resets_on_success() {
        let mut cb = CircuitBreaker::new("api.example.com", 3);
        cb.record_failure();
        cb.record_failure();
        cb.record_failure();
        assert_eq!(cb.state, CircuitState::Open);
        cb.record_success();
        assert_eq!(cb.state, CircuitState::Closed);
        assert_eq!(cb.failures, 0);
    }

    #[test]
    fn test_command_lock_acquire_release() {
        let mut lock = CommandLock::new("test_cmd_hash");
        assert!(!lock.is_locked());
        lock.acquire(1234, Some("/tmp/output.txt".into())).unwrap();
        assert!(lock.is_locked());
        assert_eq!(lock.pid, 1234);
        lock.release(1234).unwrap();
        assert!(!lock.is_locked());
    }

    #[test]
    fn test_command_lock_cannot_acquire_twice() {
        let mut lock = CommandLock::new("test_cmd_hash");
        lock.acquire(1234, None).unwrap();
        let result = lock.acquire(5678, None);
        assert!(result.is_err());
    }

    #[test]
    fn test_health_score_calculation() {
        let mut hs = HealthScore::new();
        hs.set_component("cpu", 0.9);
        hs.set_component("memory", 0.7);
        hs.set_component("disk", 1.0);
        assert!((hs.overall() - 0.866).abs() < 0.01);
        assert!(hs.is_healthy());
    }
}
