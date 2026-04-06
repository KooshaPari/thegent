//! # Driven Ports (Secondary Ports)
//!
//! Interfaces that the domain defines and infrastructure must implement.

use crate::domain::entities::{Process, ProcessPool};
use crate::domain::value_objects::{ExitStatus, ResourceUsage};
use crate::domain::events::SubprocessEvent;

/// Port for process execution (DRIVEN)
pub trait ProcessExecutorPort {
    /// Execute a process
    fn execute(&mut self, process: &Process) -> Result<u32, String>;

    /// Execute a process and capture output
    fn execute_with_output(&mut self, process: &Process) -> Result<ExitStatus, String>;

    /// Wait for a process to complete
    fn wait(&mut self, pid: u32) -> Result<ExitStatus, String>;

    /// Kill a process
    fn kill(&mut self, pid: u32) -> Result<(), String>;

    /// List running process IDs
    fn list_running(&self) -> Result<Vec<u32>, String>;
}

/// Port for process registry (DRIVEN)
pub trait ProcessRegistryPort {
    /// Register a new process
    fn register_process(&mut self, process: &Process) -> Result<(), String>;

    /// Unregister a process
    fn unregister_process(&mut self, pid: u32) -> Result<(), String>;

    /// Get a process by PID
    fn get_process(&self, pid: u32) -> Option<Process>;

    /// List all registered processes
    fn list_processes(&self) -> Vec<Process>;
}

/// Port for process scheduling (DRIVEN)
pub trait ProcessSchedulerPort {
    /// Create a new process pool
    fn create_pool(&mut self, pool_id: &str, size: usize) -> Result<(), String>;

    /// Schedule a process in a pool
    fn schedule(&mut self, pool_id: &str) -> Result<(), String>;

    /// Get pool status
    fn get_pool(&self, pool_id: &str) -> Option<ProcessPool>;

    /// Shutdown a pool
    fn shutdown_pool(&mut self, pool_id: &str) -> Result<(), String>;
}

/// Port for resource monitoring (DRIVEN)
pub trait ResourceMonitorPort {
    /// Get resource usage for a process
    fn get_usage(&self, pid: u32) -> Result<ResourceUsage, String>;

    /// Check if process is alive
    fn is_alive(&self, pid: u32) -> bool;
}

/// Port for event publishing (DRIVEN)
pub trait EventPublisherPort {
    /// Publish a subprocess event
    fn publish(&mut self, event: SubprocessEvent) -> Result<(), String>;
}
