//! Configuration Module
//!
//! Handles TOML configuration file parsing and validation.

use std::collections::HashMap;
use std::path::PathBuf;

use serde::{Deserialize, Serialize};

/// Main Forge configuration
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ForgeConfig {
    /// Task definitions
    #[serde(default)]
    pub tasks: HashMap<String, TaskConfig>,

    /// Maximum number of parallel workers (default: number of CPUs)
    pub workers: Option<usize>,

    /// Default watch paths for all tasks
    #[serde(default)]
    pub watch: Vec<String>,

    /// Environment variables
    #[serde(default)]
    pub env: HashMap<String, String>,

    /// Global ignore patterns
    #[serde(default)]
    pub ignore: Vec<String>,
}

impl Default for ForgeConfig {
    fn default() -> Self {
        Self {
            tasks: HashMap::new(),
            workers: None,
            watch: vec![".".to_string()],
            env: HashMap::new(),
            ignore: vec![
                ".git".to_string(),
                "target".to_string(),
                "node_modules".to_string(),
            ],
        }
    }
}

impl ForgeConfig {
    /// Load configuration from a TOML file
    pub fn from_file(path: &PathBuf) -> crate::Result<Self> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| crate::ForgeError::ConfigError(format!(
                "Failed to read config file: {}",
                e
            )))?;

        Self::from_str(&content)
    }

    /// Parse configuration from a string
    pub fn from_str(content: &str) -> crate::Result<Self> {
        toml::from_str(content)
            .map_err(|e| crate::ForgeError::ConfigError(format!("Failed to parse TOML: {}", e)))
    }

    /// Add a task to the configuration
    pub fn add_task(&mut self, name: impl Into<String>, config: TaskConfig) {
        self.tasks.insert(name.into(), config);
    }

    /// Get a task by name
    pub fn get_task(&self, name: &str) -> Option<&TaskConfig> {
        self.tasks.get(name)
    }

    /// Get a mutable task by name
    pub fn get_task_mut(&mut self, name: &str) -> Option<&mut TaskConfig> {
        self.tasks.get_mut(name)
    }

    /// Remove a task by name
    pub fn remove_task(&mut self, name: &str) -> Option<TaskConfig> {
        self.tasks.remove(name)
    }

    /// List all task names
    pub fn task_names(&self) -> Vec<&String> {
        self.tasks.keys().collect()
    }

    /// Validate the configuration
    pub fn validate(&self) -> crate::Result<()> {
        for name in self.tasks.keys() {
            if name.is_empty() {
                return Err(crate::ForgeError::ConfigError(
                    "Task name cannot be empty".to_string(),
                ));
            }
        }

        for (name, task) in &self.tasks {
            let mut seen = std::collections::HashSet::new();
            for dep in &task.dependencies {
                if !seen.insert(dep) {
                    return Err(crate::ForgeError::ConfigError(format!(
                        "Task '{}' has duplicate dependency: {}",
                        name, dep
                    )));
                }
            }
        }

        Ok(())
    }
}

/// Configuration for a single task
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct TaskConfig {
    /// The command to execute
    pub command: String,

    /// Human-readable description
    pub description: Option<String>,

    /// Tasks that must complete before this one
    #[serde(default)]
    pub dependencies: Vec<String>,

    /// Paths to watch for changes
    pub watch: Option<Vec<String>>,

    /// Environment variables for this task
    #[serde(default)]
    pub env: HashMap<String, String>,

    /// Timeout in seconds (0 = no timeout)
    #[serde(default)]
    pub timeout: u64,
}

impl TaskConfig {
    pub fn new(command: impl Into<String>) -> Self {
        Self {
            command: command.into(),
            description: None,
            dependencies: Vec::new(),
            watch: None,
            env: HashMap::new(),
            timeout: 0,
        }
    }

    pub fn description(mut self, desc: impl Into<String>) -> Self {
        self.description = Some(desc.into());
        self
    }

    pub fn dependencies(mut self, deps: Vec<String>) -> Self {
        self.dependencies = deps;
        self
    }

    pub fn dependency(mut self, dep: impl Into<String>) -> Self {
        self.dependencies.push(dep.into());
        self
    }

    pub fn watch(mut self, paths: Vec<String>) -> Self {
        self.watch = Some(paths);
        self
    }

    pub fn timeout(mut self, seconds: u64) -> Self {
        self.timeout = seconds;
        self
    }

    pub fn env(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.env.insert(key.into(), value.into());
        self
    }
}

pub const EXAMPLE_CONFIG: &str = r#"
[env]
RUST_BACKTRACE = "1"

workers = 4
watch = ["src", "tests"]
ignore = [".git", "target", "node_modules"]

[tasks.build]
command = "cargo build --release"
description = "Build the project in release mode"
watch = ["src", "Cargo.toml"]
timeout = 300

[tasks.test]
command = "cargo test"
description = "Run all tests"
dependencies = ["build"]
timeout = 180

[tasks.lint]
command = "cargo clippy"
description = "Run linter"
timeout = 120

[tasks.all]
command = "echo 'Running all checks'"
description = "Run build, test, and lint"
dependencies = ["build", "test", "lint"]
"#;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_config() {
        let config = ForgeConfig::from_str(EXAMPLE_CONFIG).unwrap();
        assert_eq!(config.tasks.len(), 5);
        assert_eq!(config.workers, Some(4));

        let build = config.get_task("build").unwrap();
        assert_eq!(build.command, "cargo build --release");
        assert!(build.watch.is_some());
    }

    #[test]
    fn test_task_builder() {
        let task = TaskConfig::new("echo hello")
            .description("Print greeting")
            .dependency("setup")
            .timeout(60);

        assert_eq!(task.command, "echo hello");
        assert_eq!(task.description, Some("Print greeting".to_string()));
        assert_eq!(task.dependencies, vec!["setup"]);
        assert_eq!(task.timeout, 60);
    }

    #[test]
    fn test_config_validation() {
        let mut config = ForgeConfig::default();
        config.add_task("test", TaskConfig::new("echo test"));
        config.add_task("build", TaskConfig::new("echo build"));

        assert!(config.validate().is_ok());

        config.add_task("check", TaskConfig {
            command: "echo check".to_string(),
            dependencies: vec!["test".to_string(), "test".to_string()],
            description: None,
            watch: None,
            env: HashMap::new(),
            timeout: 0,
        });

        assert!(config.validate().is_err());
    }
}
