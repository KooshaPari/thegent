//! # Domain Entities
//!
//! Core business objects with identity.

use super::value_objects::{ExitStatus, ProcessLimits, ProcessState};
use std::collections::HashMap;

/// Process entity representing a running or completed subprocess
#[derive(Debug, Clone)]
pub struct Process {
    /// Unique process ID (assigned by OS)
    pub pid: Option<u32>,
    /// Command being executed
    pub command: String,
    /// Arguments
    pub args: Vec<String>,
    /// Process state
    pub state: ProcessState,
    /// Exit status (if terminated)
    pub exit_status: Option<ExitStatus>,
    /// Working directory
    pub cwd: Option<String>,
    /// Environment variables
    pub env: HashMap<String, String>,
    /// Start time
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// End time (if terminated)
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// Stdin path (if redirected)
    pub stdin: Option<String>,
    /// Stdout path (if redirected)
    pub stdout: Option<String>,
    /// Stderr path (if redirected)
    pub stderr: Option<String>,
    /// Nice value for process priority (-20 to 20, higher = lower priority)
    pub nice: Option<i32>,
    /// Resource limits to enforce on the spawned process
    pub limits: Option<ProcessLimits>,
    /// Run under macOS background QoS (taskpolicy -b -c background)
    pub background_qos: bool,
    /// Throttle disk I/O (taskpolicy -d throttle)
    pub throttle_io: bool,
}

impl Process {
    /// Create a new process with the given command
    pub fn new(command: String, args: Vec<String>) -> Self {
        Self {
            pid: None,
            command,
            args,
            state: ProcessState::Created,
            exit_status: None,
            cwd: None,
            env: std::env::vars().collect(),
            start_time: None,
            end_time: None,
            stdin: None,
            stdout: None,
            stderr: None,
            nice: None,
            limits: None,
            background_qos: false,
            throttle_io: false,
        }
    }

    /// Set the process ID
    pub fn with_pid(mut self, pid: u32) -> Self {
        self.pid = Some(pid);
        self
    }

    /// Set working directory
    pub fn with_cwd(mut self, cwd: String) -> Self {
        self.cwd = Some(cwd);
        self
    }

    /// Set stdin
    pub fn with_stdin(mut self, stdin: String) -> Self {
        self.stdin = Some(stdin);
        self
    }

    /// Set stdout
    pub fn with_stdout(mut self, stdout: String) -> Self {
        self.stdout = Some(stdout);
        self
    }

    /// Set stderr
    pub fn with_stderr(mut self, stderr: String) -> Self {
        self.stderr = Some(stderr);
        self
    }

    /// Start the process
    pub fn start(&mut self) {
        self.state = ProcessState::Running;
        self.start_time = Some(chrono::Utc::now());
    }

    /// Complete the process with exit status
    pub fn complete(&mut self, exit_status: ExitStatus) {
        self.state = ProcessState::Completed;
        self.exit_status = Some(exit_status);
        self.end_time = Some(chrono::Utc::now());
    }

    /// Pause the process
    pub fn pause(&mut self) {
        if matches!(self.state, ProcessState::Running) {
            self.state = ProcessState::Paused;
        }
    }

    /// Resume the process
    pub fn resume(&mut self) {
        if matches!(self.state, ProcessState::Paused) {
            self.state = ProcessState::Running;
        }
    }
}

/// Builder for creating processes
#[derive(Debug, Clone, Default)]
pub struct ProcessBuilder {
    command: Option<String>,
    args: Vec<String>,
    cwd: Option<String>,
    env: HashMap<String, String>,
    stdin: Option<String>,
    stdout: Option<String>,
    stderr: Option<String>,
    nice: Option<i32>,
    limits: Option<ProcessLimits>,
    background_qos: bool,
    throttle_io: bool,
}

impl ProcessBuilder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn command(mut self, cmd: String) -> Self {
        self.command = Some(cmd);
        self
    }

    pub fn arg(mut self, arg: String) -> Self {
        self.args.push(arg);
        self
    }

    pub fn args(mut self, args: Vec<String>) -> Self {
        self.args.extend(args);
        self
    }

    pub fn cwd(mut self, cwd: String) -> Self {
        self.cwd = Some(cwd);
        self
    }

    pub fn stdin(mut self, stdin: String) -> Self {
        self.stdin = Some(stdin);
        self
    }

    pub fn stdout(mut self, stdout: String) -> Self {
        self.stdout = Some(stdout);
        self
    }

    pub fn stderr(mut self, stderr: String) -> Self {
        self.stderr = Some(stderr);
        self
    }

    pub fn env(mut self, key: String, value: String) -> Self {
        self.env.insert(key, value);
        self
    }

    /// Set nice priority (-20 highest .. 20 lowest)
    pub fn nice(mut self, nice: i32) -> Self {
        self.nice = Some(nice);
        self
    }

    /// Set resource limits
    pub fn limits(mut self, limits: ProcessLimits) -> Self {
        self.limits = Some(limits);
        self
    }

    /// Enable macOS background QoS (taskpolicy -b -c background)
    pub fn background_qos(mut self, enabled: bool) -> Self {
        self.background_qos = enabled;
        self
    }

    /// Enable macOS disk I/O throttling (taskpolicy -d throttle)
    pub fn throttle_io(mut self, enabled: bool) -> Self {
        self.throttle_io = enabled;
        self
    }

    pub fn build(self) -> Result<Process, String> {
        let command = self.command.ok_or("Command is required")?;
        Ok(Process {
            pid: None,
            command,
            args: self.args,
            state: ProcessState::Created,
            exit_status: None,
            cwd: self.cwd,
            env: self.env,
            start_time: None,
            end_time: None,
            stdin: self.stdin,
            stdout: self.stdout,
            stderr: self.stderr,
            nice: self.nice,
            limits: self.limits,
            background_qos: self.background_qos,
            throttle_io: self.throttle_io,
        })
    }
}

/// Process pool entity
#[derive(Debug, Clone)]
pub struct ProcessPool {
    /// Pool identifier
    pub id: String,
    /// Pool name
    pub name: String,
    /// Maximum processes in pool
    pub max_processes: usize,
    /// Current process count
    pub current_processes: usize,
    /// Pool state
    pub state: PoolState,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PoolState {
    Active,
    Paused,
    Shutdown,
}

impl ProcessPool {
    pub fn new(id: String, name: String, max_processes: usize) -> Self {
        Self {
            id,
            name,
            max_processes,
            current_processes: 0,
            state: PoolState::Active,
        }
    }

    pub fn can_spawn(&self) -> bool {
        self.state == PoolState::Active && self.current_processes < self.max_processes
    }

    pub fn increment(&mut self) {
        self.current_processes += 1;
    }

    pub fn decrement(&mut self) {
        self.current_processes = self.current_processes.saturating_sub(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_process_creation() {
        let process = Process::new("echo".to_string(), vec!["hello".to_string()]);
        assert_eq!(process.state, ProcessState::Created);
        assert!(process.pid.is_none());
    }

    #[test]
    fn test_process_builder() {
        let process = ProcessBuilder::new()
            .command("ls".to_string())
            .arg("-la".to_string())
            .cwd("/tmp".to_string())
            .build()
            .unwrap();

        assert_eq!(process.command, "ls");
        assert_eq!(process.args, vec!["-la"]);
        assert_eq!(process.cwd, Some("/tmp".to_string()));
    }

    #[test]
    fn test_process_pool() {
        let mut pool = ProcessPool::new("pool1".to_string(), "Test Pool".to_string(), 5);
        assert!(pool.can_spawn());

        pool.increment();
        assert_eq!(pool.current_processes, 1);

        pool.decrement();
        assert_eq!(pool.current_processes, 0);
    }
}
