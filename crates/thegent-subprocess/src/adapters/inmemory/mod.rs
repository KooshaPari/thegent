//! # In-Memory Adapters
//!
//! Pure in-memory implementations for testing and development.

use std::collections::HashMap;
use crate::domain::entities::Process;
use crate::domain::value_objects::ProcessState;
use crate::ports::driven::{ProcessExecutorPort, ProcessRegistryPort};

/// In-memory process executor for testing
pub struct InMemoryProcessExecutor {
    /// Currently running processes
    processes: HashMap<u32, Process>,
    next_pid: u32,
}

impl InMemoryProcessExecutor {
    pub fn new() -> Self {
        Self {
            processes: HashMap::new(),
            next_pid: 1,
        }
    }
}

impl Default for InMemoryProcessExecutor {
    fn default() -> Self {
        Self::new()
    }
}

impl ProcessExecutorPort for InMemoryProcessExecutor {
    fn execute(&mut self, process: &Process) -> Result<u32, String> {
        let pid = self.next_pid;
        self.next_pid += 1;
        
        let mut p = process.clone();
        p.pid = Some(pid);
        p.state = ProcessState::Running;
        
        self.processes.insert(pid, p);
        Ok(pid)
    }

    fn execute_with_output(&mut self, process: &Process) -> Result<crate::domain::value_objects::ExitStatus, String> {
        let pid = self.execute(process)?;
        Ok(crate::domain::value_objects::ExitStatus::new(pid as i32))
    }

    fn wait(&mut self, pid: u32) -> Result<crate::domain::value_objects::ExitStatus, String> {
        if let Some(mut p) = self.processes.remove(&pid) {
            p.state = ProcessState::Completed;
            Ok(crate::domain::value_objects::ExitStatus::new(0))
        } else {
            Err(format!("Process {} not found", pid))
        }
    }

    fn kill(&mut self, pid: u32) -> Result<(), String> {
        if self.processes.remove(&pid).is_some() {
            Ok(())
        } else {
            Err(format!("Process {} not found", pid))
        }
    }

    fn list_running(&self) -> Result<Vec<u32>, String> {
        Ok(self.processes.keys().cloned().collect())
    }
}

/// In-memory process registry for testing
pub struct InMemoryProcessRegistry {
    /// Registered processes
    processes: HashMap<u32, Process>,
}

impl InMemoryProcessRegistry {
    pub fn new() -> Self {
        Self {
            processes: HashMap::new(),
        }
    }
}

impl Default for InMemoryProcessRegistry {
    fn default() -> Self {
        Self::new()
    }
}

impl ProcessRegistryPort for InMemoryProcessRegistry {
    fn register_process(&mut self, process: &Process) -> Result<(), String> {
        if let Some(pid) = process.pid {
            self.processes.insert(pid, process.clone());
            Ok(())
        } else {
            Err("Process must have a PID to register".into())
        }
    }

    fn unregister_process(&mut self, pid: u32) -> Result<(), String> {
        if self.processes.remove(&pid).is_some() {
            Ok(())
        } else {
            Err(format!("Process {} not found", pid))
        }
    }

    fn get_process(&self, pid: u32) -> Option<Process> {
        self.processes.get(&pid).cloned()
    }

    fn list_processes(&self) -> Vec<Process> {
        self.processes.values().cloned().collect()
    }
}
