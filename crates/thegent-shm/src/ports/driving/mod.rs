//! # Driving Ports (Primary Ports)
//!
//! Interfaces that the application uses to interact with external actors (users, systems).

/// CLI interface for the SHM system
pub trait CliPort {
    /// Display lock status
    fn display_locks(&self, locks: Vec<crate::domain::entities::CommandLock>);

    /// Display circuit breaker status
    fn display_breakers(&self, breakers: Vec<crate::domain::entities::CircuitBreaker>);

    /// Display health status
    fn display_health(&self, health: crate::domain::entities::HealthScore);

    /// Display error
    fn display_error(&self, error: &str);
}

/// HTTP/REST interface
pub trait HttpPort {
    /// Handle acquire lock request
    fn handle_acquire_lock(&self, cmd_hash: &str, pid: u32) -> Result<(), String>;

    /// Handle release lock request
    fn handle_release_lock(&self, cmd_hash: &str, pid: u32) -> Result<(), String>;

    /// Handle get lock request
    fn handle_get_lock(&self, cmd_hash: &str) -> Option<crate::domain::entities::CommandLock>;

    /// Handle health check
    fn handle_health_check(&self) -> crate::domain::entities::HealthScore;
}
