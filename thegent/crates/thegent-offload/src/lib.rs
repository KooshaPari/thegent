use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

pub mod executor;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionRequest {
    pub id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub prompt: String,
    pub cwd: String,
    pub env_vars: HashMap<String, String>,
    pub timeout_seconds: u32,
    pub sync_state: Option<SyncState>,
    pub options: ExecutionOptions,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionOptions {
    pub dry_run: bool,
    pub isolation_level: IsolationLevel,
    pub stream_output: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IsolationLevel {
    Process,
    Worktree,
    Container,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncState {
    pub base_commit: String,
    pub patch: Option<String>, // Base64 encoded or raw patch
    pub modified_files: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionResponse {
    pub request_id: Uuid,
    pub status: ExecutionStatus,
    pub stdout: Option<String>,
    pub stderr: Option<String>,
    pub exit_code: Option<i32>,
    pub duration_ms: u64,
    pub metrics: Option<ExecutionMetrics>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExecutionStatus {
    Queued,
    Running,
    Completed,
    Failed(String),
    TimedOut,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionMetrics {
    pub cpu_usage_pct: f32,
    pub memory_mb: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkerInfo {
    pub id: String,
    pub hostname: String,
    pub os: String,
    pub arch: String,
    pub capabilities: Vec<String>,
    pub status: WorkerStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WorkerStatus {
    Idle,
    Busy(u32), // number of active tasks
    Offline,
}
