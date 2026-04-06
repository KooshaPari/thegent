//! # Queries (CQRS)
//!
//! Operations that read state without side effects.

/// Query to get a specific process
#[derive(Debug, Clone)]
pub struct GetProcessQuery {
    pub process_id: String,
}

/// Query to list all processes
#[derive(Debug, Clone)]
pub struct ListProcessesQuery {
    pub filter: Option<String>,
}

/// Query to get process output
#[derive(Debug, Clone)]
pub struct GetOutputQuery {
    pub process_id: String,
}

/// Query to get process statistics
#[derive(Debug, Clone)]
pub struct GetStatsQuery {
    pub process_id: String,
}

/// Query to wait for process completion
#[derive(Debug, Clone)]
pub struct WaitProcessQuery {
    pub process_id: String,
    pub timeout_secs: Option<u64>,
}

/// Query to check if process is running
#[derive(Debug, Clone)]
pub struct IsRunningQuery {
    pub process_id: String,
}
