//! Job entity - Core concept for scheduled/executable jobs.

use std::fmt;

/// Unique identifier for a job.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct JobId(String);

impl JobId {
    pub fn new(id: impl Into<String>) -> Self {
        Self(id.into())
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl fmt::Display for JobId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// Job status.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum JobStatus {
    Pending,
    Scheduled,
    Running,
    Completed,
    Failed,
    Cancelled,
}

impl Default for JobStatus {
    fn default() -> Self {
        JobStatus::Pending
    }
}

/// Job priority.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum JobPriority {
    Low = 0,
    Normal = 1,
    High = 2,
    Critical = 3,
}

impl Default for JobPriority {
    fn default() -> Self {
        JobPriority::Normal
    }
}

/// Job result.
#[derive(Debug, Clone)]
pub struct JobResult {
    pub success: bool,
    pub output: Option<String>,
    pub error: Option<String>,
    pub started_at: Option<chrono::DateTime<chrono::Utc>>,
    pub completed_at: Option<chrono::DateTime<chrono::Utc>>,
}

impl JobResult {
    pub fn success(output: String) -> Self {
        Self {
            success: true,
            output: Some(output),
            error: None,
            started_at: None,
            completed_at: Some(chrono::Utc::now()),
        }
    }

    pub fn failure(error: String) -> Self {
        Self {
            success: false,
            output: None,
            error: Some(error),
            started_at: None,
            completed_at: Some(chrono::Utc::now()),
        }
    }
}

/// Job entity.
#[derive(Debug, Clone)]
pub struct Job {
    pub id: JobId,
    pub name: String,
    pub description: String,
    pub payload: serde_json::Value,
    pub status: JobStatus,
    pub priority: JobPriority,
    pub schedule_id: Option<String>,
    pub result: Option<JobResult>,
    pub created_at: Option<chrono::DateTime<chrono::Utc>>,
    pub scheduled_at: Option<chrono::DateTime<chrono::Utc>>,
    pub started_at: Option<chrono::DateTime<chrono::Utc>>,
    pub completed_at: Option<chrono::DateTime<chrono::Utc>>,
}

impl Job {
    pub fn new(id: JobId, name: String, payload: serde_json::Value) -> Self {
        Self {
            id,
            name,
            description: String::new(),
            payload,
            status: JobStatus::Pending,
            priority: JobPriority::default(),
            schedule_id: None,
            result: None,
            created_at: Some(chrono::Utc::now()),
            scheduled_at: None,
            started_at: None,
            completed_at: None,
        }
    }

    pub fn with_priority(mut self, priority: JobPriority) -> Self {
        self.priority = priority;
        self
    }

    pub fn with_schedule(mut self, schedule_id: String) -> Self {
        self.schedule_id = Some(schedule_id);
        self
    }

    pub fn schedule(&mut self, at: chrono::DateTime<chrono::Utc>) {
        self.status = JobStatus::Scheduled;
        self.scheduled_at = Some(at);
    }

    pub fn start(&mut self) {
        self.status = JobStatus::Running;
        self.started_at = Some(chrono::Utc::now());
    }

    pub fn complete(&mut self, result: JobResult) {
        self.status = if result.success { JobStatus::Completed } else { JobStatus::Failed };
        self.result = Some(result);
        self.completed_at = Some(chrono::Utc::now());
    }

    pub fn cancel(&mut self) {
        self.status = JobStatus::Cancelled;
        self.completed_at = Some(chrono::Utc::now());
    }

    pub fn is_terminal(&self) -> bool {
        matches!(self.status, JobStatus::Completed | JobStatus::Failed | JobStatus::Cancelled)
    }
}
