//! # Value Objects
//!
//! Immutable objects defined by their attributes.

/// Process state
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProcessState {
    /// Process is created but not started
    Created,
    /// Process is running
    Running,
    /// Process is paused
    Paused,
    /// Process has completed
    Completed,
    /// Process was killed
    Killed,
    /// Process failed to start
    Failed,
}

impl std::fmt::Display for ProcessState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ProcessState::Created => write!(f, "created"),
            ProcessState::Running => write!(f, "running"),
            ProcessState::Paused => write!(f, "paused"),
            ProcessState::Completed => write!(f, "completed"),
            ProcessState::Killed => write!(f, "killed"),
            ProcessState::Failed => write!(f, "failed"),
        }
    }
}

/// Exit status (simplified struct for compatibility)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExitStatus {
    /// Exit code
    pub code: i32,
}

impl ExitStatus {
    /// Create a new exit status with code
    pub fn new(code: i32) -> Self {
        Self { code }
    }

    /// Check if exit was successful (exit code 0)
    pub fn is_success(&self) -> bool {
        self.code == 0
    }

    /// Get the exit code
    pub fn code(&self) -> i32 {
        self.code
    }
}

impl std::fmt::Display for ExitStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "exited with code {}", self.code)
    }
}

/// Process limits
#[derive(Debug, Clone)]
pub struct ProcessLimits {
    /// Maximum CPU time in seconds
    pub max_cpu_seconds: Option<u64>,
    /// Maximum memory in bytes
    pub max_memory_bytes: Option<u64>,
    /// Maximum number of processes
    pub max_processes: Option<u32>,
    /// Maximum file size in bytes
    pub max_file_size: Option<u64>,
    /// Maximum number of open files
    pub max_open_files: Option<u32>,
}

impl Default for ProcessLimits {
    fn default() -> Self {
        Self {
            max_cpu_seconds: None,
            max_memory_bytes: None,
            max_processes: None,
            max_file_size: None,
            max_open_files: None,
        }
    }
}

impl ProcessLimits {
    /// Create a new limits builder
    pub fn builder() -> ProcessLimitsBuilder {
        ProcessLimitsBuilder::new()
    }

    /// Create limits for sandboxed execution
    pub fn sandbox() -> Self {
        Self {
            max_cpu_seconds: Some(60),
            max_memory_bytes: Some(512 * 1024 * 1024), // 512 MB
            max_processes: Some(4),
            max_file_size: Some(100 * 1024 * 1024), // 100 MB
            max_open_files: Some(64),
        }
    }
}

/// Builder for process limits
pub struct ProcessLimitsBuilder {
    max_cpu_seconds: Option<u64>,
    max_memory_bytes: Option<u64>,
    max_processes: Option<u32>,
    max_file_size: Option<u64>,
    max_open_files: Option<u32>,
}

impl ProcessLimitsBuilder {
    pub fn new() -> Self {
        Self {
            max_cpu_seconds: None,
            max_memory_bytes: None,
            max_processes: None,
            max_file_size: None,
            max_open_files: None,
        }
    }

    pub fn max_cpu_seconds(mut self, seconds: u64) -> Self {
        self.max_cpu_seconds = Some(seconds);
        self
    }

    pub fn max_memory_bytes(mut self, bytes: u64) -> Self {
        self.max_memory_bytes = Some(bytes);
        self
    }

    pub fn max_processes(mut self, count: u32) -> Self {
        self.max_processes = Some(count);
        self
    }

    pub fn max_file_size(mut self, bytes: u64) -> Self {
        self.max_file_size = Some(bytes);
        self
    }

    pub fn max_open_files(mut self, count: u32) -> Self {
        self.max_open_files = Some(count);
        self
    }

    pub fn build(self) -> ProcessLimits {
        ProcessLimits {
            max_cpu_seconds: self.max_cpu_seconds,
            max_memory_bytes: self.max_memory_bytes,
            max_processes: self.max_processes,
            max_file_size: self.max_file_size,
            max_open_files: self.max_open_files,
        }
    }
}

impl Default for ProcessLimitsBuilder {
    fn default() -> Self {
        Self::new()
    }
}

/// Environment variable
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EnvVar {
    pub key: String,
    pub value: String,
}

impl EnvVar {
    pub fn new(key: impl Into<String>, value: impl Into<String>) -> Self {
        Self {
            key: key.into(),
            value: value.into(),
        }
    }
}

/// Process output
#[derive(Debug, Clone)]
pub struct ProcessOutput {
    /// Exit status
    pub exit_status: ExitStatus,
    /// Standard output
    pub stdout: Vec<u8>,
    /// Standard error
    pub stderr: Vec<u8>,
    /// Duration
    pub duration: chrono::Duration,
    /// Resource usage
    pub resource_usage: ResourceUsage,
}

/// Process status
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProcessStatus {
    /// Process is pending
    Pending,
    /// Process is running
    Running,
    /// Process completed successfully
    Completed,
    /// Process failed
    Failed,
    /// Process was killed
    Killed,
    /// Process timed out
    Timeout,
}

impl std::fmt::Display for ProcessStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ProcessStatus::Pending => write!(f, "pending"),
            ProcessStatus::Running => write!(f, "running"),
            ProcessStatus::Completed => write!(f, "completed"),
            ProcessStatus::Failed => write!(f, "failed"),
            ProcessStatus::Killed => write!(f, "killed"),
            ProcessStatus::Timeout => write!(f, "timeout"),
        }
    }
}

impl Default for ProcessStatus {
    fn default() -> Self {
        ProcessStatus::Pending
    }
}

impl ProcessStatus {
    pub fn is_terminal(&self) -> bool {
        matches!(
            self,
            ProcessStatus::Completed | ProcessStatus::Failed | ProcessStatus::Killed | ProcessStatus::Timeout
        )
    }
}

/// Resource usage statistics
#[derive(Debug, Clone, Default)]
pub struct ResourceUsage {
    /// CPU time used
    pub cpu_time_seconds: f64,
    /// Memory used (bytes)
    pub memory_bytes: u64,
    /// Block I/O read (bytes)
    pub io_read_bytes: u64,
    /// Block I/O write (bytes)
    pub io_write_bytes: u64,
}

impl ResourceUsage {
    pub fn new() -> Self {
        Self::default()
    }
}
