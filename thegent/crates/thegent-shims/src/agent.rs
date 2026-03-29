//! Agent invocation shim with fallback routing (secure execution)
//!
//! Resolves agent binaries (codex, copilot, dex, claude, cursor)
//! with configurable fallback chains.
//!
//! SECURITY: Uses std::process::Command (NOT shell exec).
//! Command never invokes a shell and is completely safe from injection.

use crate::utils::resolve_binary;
use std::path::PathBuf;
use std::process::{Command, ExitCode};

pub struct AgentShim {
    agent_map: std::collections::HashMap<String, Vec<String>>,
}

impl AgentShim {
    pub fn new() -> Self {
        let mut agent_map = std::collections::HashMap::new();

        // Define fallback chains
        agent_map.insert(
            "dex".to_string(),
            vec!["dex".to_string(), "codex".to_string()],
        );
        agent_map.insert("codex".to_string(), vec!["codex".to_string()]);
        agent_map.insert(
            "copilot".to_string(),
            vec!["copilot".to_string(), "github-copilot".to_string()],
        );
        agent_map.insert("claude".to_string(), vec!["claude".to_string()]);
        agent_map.insert("cursor".to_string(), vec!["cursor".to_string()]);

        Self { agent_map }
    }

    /// Resolve agent binary with fallback chain
    fn resolve_agent(&self, name: &str) -> Option<PathBuf> {
        // Try explicit fallback chain
        if let Some(chain) = self.agent_map.get(&name.to_lowercase()) {
            for candidate in chain {
                if let Some(path) = resolve_binary(candidate) {
                    return Some(path);
                }
            }
        }

        // Direct resolution as fallback
        resolve_binary(name)
    }

    /// Check if agent is available
    pub fn is_available(&self, name: &str) -> bool {
        self.resolve_agent(name).is_some()
    }

    /// Execute agent securely
    pub fn exec(&self, name: &str, args: &[String]) -> ExitCode {
        match self.resolve_agent(name) {
            Some(agent_path) => {
                // Command::new() is safe - never invokes shell
                let mut cmd = Command::new(&agent_path);
                cmd.args(args);

                // Preserve thegent environment
                if let Ok(project_dir) = std::env::var("PROJECT_DIR") {
                    cmd.env("PROJECT_DIR", project_dir);
                }
                if let Ok(session_id) = std::env::var("SESSION_ID") {
                    cmd.env("SESSION_ID", session_id);
                }
                if let Ok(thegent_root) = std::env::var("THEGENT_ROOT") {
                    cmd.env("THEGENT_ROOT", thegent_root);
                }

                match cmd.status() {
                    Ok(status) => {
                        let code = status.code().unwrap_or(1);
                        ExitCode::from(code as u8)
                    }
                    Err(e) => {
                        eprintln!("thegent-agent: failed to execute {}: {}", name, e);
                        ExitCode::from(127)
                    }
                }
            }
            None => {
                eprintln!("thegent-agent: '{}' not found in PATH", name);
                if let Some(chain) = self.agent_map.get(&name.to_lowercase()) {
                    eprintln!("thegent-agent: tried: {}", chain.join(", "));
                }
                ExitCode::from(127)
            }
        }
    }

    /// Get the resolved path without executing
    pub fn resolve(&self, name: &str) -> Option<PathBuf> {
        self.resolve_agent(name)
    }
}

impl Default for AgentShim {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_agent_map() {
        let shim = AgentShim::new();
        assert!(shim.agent_map.contains_key("dex"));
        assert!(shim.agent_map.contains_key("codex"));
        assert!(shim.agent_map.contains_key("claude"));
    }

    #[test]
    fn test_fallback_chain() {
        let shim = AgentShim::new();
        let chain = shim.agent_map.get("dex").unwrap();
        assert_eq!(chain[0], "dex");
        assert_eq!(chain[1], "codex");
    }
}
