//! # Commands (CQRS)
//!
//! Operations that change state.

/// Command to spawn a new process
#[derive(Debug, Clone)]
pub struct SpawnCommand {
    pub command: Vec<String>,
    pub cwd: Option<String>,
    pub env: Option<Vec<(String, String)>>,
    pub timeout_secs: Option<u64>,
    pub user: Option<String>,
}

/// Command to kill a process
#[derive(Debug, Clone)]
pub struct KillCommand {
    pub process_id: String,
    pub signal: Option<i32>,
}

/// Command to send a signal to a process
#[derive(Debug, Clone)]
pub struct SignalCommand {
    pub process_id: String,
    pub signal: i32,
}

/// Command to update process priority
#[derive(Debug, Clone)]
pub struct SetPriorityCommand {
    pub process_id: String,
    pub nice: i32,
}

/// Command to set process resource limits
#[derive(Debug, Clone)]
pub struct SetLimitsCommand {
    pub process_id: String,
    pub max_memory_bytes: Option<u64>,
    pub max_cpu_percent: Option<f32>,
    pub max_time_secs: Option<u64>,
}
