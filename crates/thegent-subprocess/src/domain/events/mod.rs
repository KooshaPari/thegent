//! # Domain Events
//!
//! Immutable events representing state changes.

use std::time::SystemTime;

/// Subprocess domain events
#[derive(Debug, Clone)]
pub enum SubprocessEvent {
    /// Process was spawned
    ProcessSpawned {
        process_id: String,
        pid: u32,
        timestamp: SystemTime,
    },
    /// Process completed
    ProcessCompleted {
        process_id: String,
        exit_status: String,
        duration_ms: u64,
        timestamp: SystemTime,
    },
    /// Process was killed
    ProcessKilled {
        process_id: String,
        signal: Option<u32>,
        timestamp: SystemTime,
    },
    /// Process exceeded limits
    ProcessLimitExceeded {
        process_id: String,
        limit_type: String,
        timestamp: SystemTime,
    },
    /// Process output captured
    ProcessOutput {
        process_id: String,
        output_type: String,
        bytes: usize,
        timestamp: SystemTime,
    },
}

impl SubprocessEvent {
    /// Get the timestamp of the event
    pub fn timestamp(&self) -> SystemTime {
        match self {
            SubprocessEvent::ProcessSpawned { timestamp, .. } => *timestamp,
            SubprocessEvent::ProcessCompleted { timestamp, .. } => *timestamp,
            SubprocessEvent::ProcessKilled { timestamp, .. } => *timestamp,
            SubprocessEvent::ProcessLimitExceeded { timestamp, .. } => *timestamp,
            SubprocessEvent::ProcessOutput { timestamp, .. } => *timestamp,
        }
    }
}
