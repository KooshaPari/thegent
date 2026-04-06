//! # Value Objects
//!
//! Immutable objects defined by their attributes.
//!
//! ## Value Object Principles
//!
//! - Immutable (no setters, create new instances)
//! - No identity (two VOs with same values are equal)
//! - Self-validating

/// Circuit breaker state
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CircuitState {
    /// Circuit is closed, requests flow through
    Closed,
    /// Circuit is open, requests are rejected
    Open,
    /// Circuit is half-open, testing if service recovered
    HalfOpen,
}

/// Lock status for command locks
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LockStatus {
    /// Lock is not held
    Unlocked,
    /// Lock is held by a process
    Locked,
    /// Lock is held and output is being written
    Completed,
    /// Lock timed out
    TimedOut,
}

/// Provider metrics for AI routing
#[derive(Debug, Clone)]
pub struct ProviderMetrics {
    pub name: String,
    pub request_count: u64,
    pub success_count: u64,
    pub failure_count: u64,
    pub latency_p50_ms: u32,
    pub success_rate: f32,
}

impl ProviderMetrics {
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            request_count: 0,
            success_count: 0,
            failure_count: 0,
            latency_p50_ms: 0,
            success_rate: 0.0,
        }
    }

    pub fn record_success(&mut self, latency_ms: u32) {
        self.request_count += 1;
        self.success_count += 1;
        self.latency_p50_ms = latency_ms;
        self.update_success_rate();
    }

    pub fn record_failure(&mut self) {
        self.request_count += 1;
        self.failure_count += 1;
        self.update_success_rate();
    }

    fn update_success_rate(&mut self) {
        if self.request_count > 0 {
            self.success_rate = self.success_count as f32 / self.request_count as f32;
        }
    }
}

/// XP/Level for gamification
#[derive(Debug, Clone, Copy)]
pub struct XpLevel {
    pub total_xp: u64,
    pub level: u32,
}

impl XpLevel {
    pub const XP_PER_LEVEL: u64 = 1000;

    pub fn new() -> Self {
        Self { total_xp: 0, level: 1 }
    }

    pub fn add_xp(&mut self, xp: u64) {
        self.total_xp += xp;
        self.level = (self.total_xp / Self::XP_PER_LEVEL) as u32 + 1;
    }

    pub fn xp_to_next_level(&self) -> u64 {
        let current_level_xp = (self.level as u64 - 1) * Self::XP_PER_LEVEL;
        let xp_into_level = self.total_xp - current_level_xp;
        // If at exact threshold, return 0 (no XP needed for next level)
        Self::XP_PER_LEVEL.saturating_sub(xp_into_level)
    }
}

impl Default for XpLevel {
    fn default() -> Self {
        Self::new()
    }
}
