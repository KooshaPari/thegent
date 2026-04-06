//! # Commands (CQRS)
//!
//! Operations that change state.

/// Command to acquire a command lock
#[derive(Debug, Clone)]
pub struct AcquireLockCommand {
    pub cmd_hash: String,
    pub pid: u32,
    pub output_path: Option<String>,
}

/// Command to release a command lock
#[derive(Debug, Clone)]
pub struct ReleaseLockCommand {
    pub cmd_hash: String,
    pub pid: u32,
}

/// Command to record a circuit breaker success
#[derive(Debug, Clone)]
pub struct RecordSuccessCommand {
    pub target: String,
}

/// Command to record a circuit breaker failure
#[derive(Debug, Clone)]
pub struct RecordFailureCommand {
    pub target: String,
}

/// Command to set component health
#[derive(Debug, Clone)]
pub struct SetHealthCommand {
    pub component: String,
    pub score: f32,
}

/// Command to record provider success
#[derive(Debug, Clone)]
pub struct RecordProviderSuccessCommand {
    pub provider: String,
    pub latency_ms: u32,
}

/// Command to record provider failure
#[derive(Debug, Clone)]
pub struct RecordProviderFailureCommand {
    pub provider: String,
}
