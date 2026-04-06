//! # Use Cases
//!
//! Application services that orchestrate domain logic.

use crate::domain::entities::Process;
use crate::ports::driven::{ProcessExecutorPort, ProcessRegistryPort, ProcessSchedulerPort};

/// Use case for spawning a new process
pub struct SpawnProcessUseCase<E: ProcessExecutorPort, R: ProcessRegistryPort> {
    executor: E,
    registry: R,
}

impl<E: ProcessExecutorPort, R: ProcessRegistryPort> SpawnProcessUseCase<E, R> {
    pub fn new(executor: E, registry: R) -> Self {
        Self { executor, registry }
    }

    pub fn execute(&mut self, process: &Process) -> Result<u32, String> {
        self.executor.execute(process)?;
        let pid = process.pid.unwrap_or(0);
        self.registry.register_process(process)?;
        Ok(pid)
    }
}

/// Use case for terminating a process
pub struct TerminateProcessUseCase<R: ProcessRegistryPort> {
    registry: R,
}

impl<R: ProcessRegistryPort> TerminateProcessUseCase<R> {
    pub fn new(registry: R) -> Self {
        Self { registry }
    }

    pub fn execute(&mut self, pid: u32) -> Result<(), String> {
        self.registry.unregister_process(pid)
    }
}

/// Use case for scheduling processes
pub struct ScheduleProcessUseCase<S: ProcessSchedulerPort> {
    scheduler: S,
}

impl<S: ProcessSchedulerPort> ScheduleProcessUseCase<S> {
    pub fn new(scheduler: S) -> Self {
        Self { scheduler }
    }

    pub fn execute(&mut self, pool_id: &str) -> Result<(), String> {
        self.scheduler.schedule(pool_id)
    }
}
