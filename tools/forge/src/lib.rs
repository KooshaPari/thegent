//! Forge - CLI Task Runner with Parallel Execution and Hot Reload
//!
//! A task runner that executes tasks in parallel with automatic dependency
//! resolution, file watching, and hot reload capabilities.

use std::collections::{HashMap, HashSet};
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Duration;

use parking_lot::RwLock;
use thiserror::Error;
use tokio::sync::mpsc;

pub mod config;
pub mod executor;
pub mod graph;
pub mod watcher;

pub use config::{ForgeConfig, TaskConfig};
pub use executor::Executor;
pub use graph::{Task, TaskGraph, TaskId};
pub use watcher::Watcher;

/// Errors that can occur during Forge operations
#[derive(Error, Debug)]
pub enum ForgeError {
    #[error("Task '{0}' not found")]
    TaskNotFound(String),

    #[error("Circular dependency detected involving task '{0}'")]
    CircularDependency(String),

    #[error("Task '{0}' failed: {1}")]
    TaskFailed(String, String),

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("Watcher error: {0}")]
    WatcherError(String),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}

/// Result type for Forge operations
pub type Result<T> = std::result::Result<T, ForgeError>;

/// Task event for real-time updates
#[derive(Debug, Clone)]
pub enum TaskEvent {
    Started(TaskId),
    Completed(TaskId, Duration),
    Failed(TaskId, String),
    Skipped(TaskId),
    Watching(Vec<PathBuf>),
}

/// Shared state for task execution
pub struct ForgeState {
    running: Arc<RwLock<HashSet<TaskId>>>,
    completed: Arc<RwLock<HashSet<TaskId>>>,
    failed: Arc<RwLock<HashSet<TaskId>>>,
    results: Arc<RwLock<HashMap<TaskId, TaskResult>>>,
}

impl ForgeState {
    pub fn new() -> Self {
        Self {
            running: Arc::new(RwLock::new(HashSet::new())),
            completed: Arc::new(RwLock::new(HashSet::new())),
            failed: Arc::new(RwLock::new(HashSet::new())),
            results: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn mark_running(&self, id: &TaskId) {
        self.running.write().insert(id.clone());
    }

    pub fn mark_completed(&self, id: &TaskId, result: TaskResult) {
        self.running.write().remove(id);
        self.completed.write().insert(id.clone());
        self.results.write().insert(id.clone(), result);
    }

    pub fn mark_failed(&self, id: &TaskId, result: TaskResult) {
        self.running.write().remove(id);
        self.failed.write().insert(id.clone());
        self.results.write().insert(id.clone(), result);
    }

    pub fn is_completed(&self, id: &TaskId) -> bool {
        self.completed.read().contains(id)
    }

    pub fn is_failed(&self, id: &TaskId) -> bool {
        self.failed.read().contains(id)
    }

    pub fn is_running(&self, id: &TaskId) -> bool {
        self.running.read().contains(id)
    }

    pub fn get_result(&self, id: &TaskId) -> Option<TaskResult> {
        self.results.read().get(id).cloned()
    }

    pub fn reset(&self) {
        self.running.write().clear();
        self.completed.write().clear();
        self.failed.write().clear();
        self.results.write().clear();
    }

    pub fn status(&self) -> ForgeStatus {
        ForgeStatus {
            running: self.running.read().len(),
            completed: self.completed.read().len(),
            failed: self.failed.read().len(),
        }
    }
}

impl Default for ForgeState {
    fn default() -> Self {
        Self::new()
    }
}

/// Status snapshot of the forge state
#[derive(Debug, Clone)]
pub struct ForgeStatus {
    pub running: usize,
    pub completed: usize,
    pub failed: usize,
}

/// Result of a task execution
#[derive(Debug, Clone)]
pub struct TaskResult {
    pub success: bool,
    pub duration: Duration,
    pub stdout: String,
    pub stderr: String,
}

/// Builder for configuring and running Forge
pub struct ForgeBuilder {
    config: ForgeConfig,
    watch: bool,
    watch_paths: Vec<PathBuf>,
}

impl ForgeBuilder {
    pub fn new(config: ForgeConfig) -> Self {
        Self {
            config,
            watch: false,
            watch_paths: vec![PathBuf::from(".")],
        }
    }

    pub fn watch(mut self, enabled: bool) -> Self {
        self.watch = enabled;
        self
    }

    pub fn watch_paths(mut self, paths: Vec<PathBuf>) -> Self {
        self.watch_paths = paths;
        self
    }

    pub async fn run(self, task_names: Vec<String>) -> Result<ForgeStatus> {
        let graph = TaskGraph::from_config(&self.config)?;
        let executor = Executor::new(self.config.workers.unwrap_or(num_cpus::get()));

        let (tx, _rx) = mpsc::channel::<TaskEvent>(100);
        executor.execute(&graph, task_names, tx).await
    }
}

impl Forge {
    pub fn builder(config: ForgeConfig) -> ForgeBuilder {
        ForgeBuilder::new(config)
    }

    pub fn load_config(path: Option<PathBuf>) -> Result<ForgeConfig> {
        let config_path = path.unwrap_or_else(|| PathBuf::from("forge.toml"));

        if !config_path.exists() {
            return Err(ForgeError::ConfigError(format!(
                "Configuration file not found: {}",
                config_path.display()
            )));
        }

        let content = std::fs::read_to_string(&config_path)?;
        let config: ForgeConfig = toml::from_str(&content)
            .map_err(|e| ForgeError::ConfigError(e.to_string()))?;

        Ok(config)
    }
}

/// Main Forge orchestrator
pub struct Forge;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_task_id_ordering() {
        let id1 = TaskId::new("build");
        let id2 = TaskId::new("test");
        let id3 = TaskId::new("build");

        assert_eq!(id1, id3);
        assert_ne!(id1, id2);
        assert!(id1 < id2);
    }

    #[test]
    fn test_forge_state_tracking() {
        let state = ForgeState::new();
        let id = TaskId::new("test");

        assert!(!state.is_completed(&id));
        assert!(!state.is_running(&id));
        assert!(!state.is_failed(&id));

        state.mark_running(&id);
        assert!(state.is_running(&id));

        state.mark_completed(&id, TaskResult {
            success: true,
            duration: Duration::from_secs(1),
            stdout: String::new(),
            stderr: String::new(),
        });

        assert!(state.is_completed(&id));
        assert!(!state.is_running(&id));
    }
}
