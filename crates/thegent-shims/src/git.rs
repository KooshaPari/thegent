//! Git wrapper with thegent integration (safe execution)
//!
//! Handles:
//! - TTL caching for read-only operations (status, diff, log)
//! - Index lock contention (multi-tenant environments)
//! - Agent passthrough (codex, copilot, dex, claude, cursor)
//! - Cache invalidation on write operations
//!
//! NOTE: Uses std::process::Command which is safe from shell injection
//! (unlike shell exec, Command never invokes a shell)

use std::process::{Command, ExitCode};
use std::path::PathBuf;
use crate::utils::{resolve_binary, exec_command};
use crate::lock;

const READ_ONLY_CMDS: &[&str] = &[
    "diff", "status", "ls-files", "rev-parse", "log", "show",
    "name-rev", "symbolic-ref", "branch", "tag", "remote",
    "config", "ls-tree", "cat-file", "describe",
];

const WRITE_CMDS: &[&str] = &[
    "add", "commit", "checkout", "reset", "rm", "mv",
    "pull", "push", "merge", "rebase", "fetch", "stash",
    "am", "apply",
];

const AGENT_CMDS: &[&str] = &[
    "codex", "copilot", "dex", "claude", "cursor",
];

pub struct GitShim {
    git_bin: Option<PathBuf>,
}

impl GitShim {
    pub fn new() -> Self {
        let git_bin = resolve_binary("git");
        Self { git_bin }
    }

    /// Check if command is read-only
    fn is_read_only(&self, cmd: &str) -> bool {
        READ_ONLY_CMDS.contains(&cmd)
    }

    /// Check if command is write
    fn is_write(&self, cmd: &str) -> bool {
        WRITE_CMDS.contains(&cmd)
    }

    /// Check if this is an agent command (should be passed through)
    fn is_agent(&self, cmd: &str) -> bool {
        AGENT_CMDS.contains(&cmd)
    }

    /// Resolve agent binary (safe - no shell escaping needed)
    fn resolve_agent(&self, name: &str) -> Option<PathBuf> {
        // Direct resolution first
        if let Some(path) = resolve_binary(name) {
            return Some(path);
        }

        // Fallback mappings
        let fallback = match name.to_lowercase().as_str() {
            "dex" => Some("codex"),
            "claude" => Some("claude"),
            "cursor" => Some("cursor"),
            "copilot" => Some("copilot"),
            _ => None,
        };

        if let Some(fb) = fallback {
            return resolve_binary(fb);
        }

        None
    }

    /// Execute git command (safe - Command never invokes shell)
    pub fn exec(&self, args: &[String]) -> ExitCode {
        let git_bin = match &self.git_bin {
            Some(path) => path.clone(),
            None => {
                eprintln!("thegent-git: unable to resolve git executable");
                return ExitCode::from(127);
            }
        };

        // No subcommand - just run git
        if args.is_empty() {
            return exec_command(git_bin.to_str().unwrap_or("git"), args);
        }

        let cmd = &args[0];
        let cmd_args = &args[1..];

        // Handle agent passthrough
        if self.is_agent(cmd) {
            return self.exec_agent(cmd, cmd_args);
        }

        // Handle write operations - acquire lock first
        if self.is_write(cmd) {
            let repo_root = crate::utils::get_repo_root();
            if !lock::acquire_lock(&repo_root) {
                return ExitCode::from(128);
            }
            lock::invalidate_cache();
        }

        // Execute git with all original args (safe - Command avoids shell)
        let mut git_args = vec![cmd.to_string()];
        git_args.extend_from_slice(cmd_args);

        exec_command(git_bin.to_str().unwrap_or("git"), &git_args)
    }

    /// Execute agent command (safe - Command avoids shell)
    fn exec_agent(&self, name: &str, args: &[String]) -> ExitCode {
        match self.resolve_agent(name) {
            Some(path) => {
                // Command::new() is safe from injection - never invokes shell
                let mut cmd = Command::new(&path);
                cmd.args(args);

                // Preserve environment variables
                if let Ok(project_dir) = std::env::var("PROJECT_DIR") {
                    cmd.env("PROJECT_DIR", project_dir);
                }
                if let Ok(session_id) = std::env::var("SESSION_ID") {
                    cmd.env("SESSION_ID", session_id);
                }

                match cmd.status() {
                    Ok(status) => {
                        let code = status.code().unwrap_or(1);
                        ExitCode::from(code as u8)
                    }
                    Err(e) => {
                        eprintln!("thegent-git: failed to execute {}: {}", name, e);
                        ExitCode::from(127)
                    }
                }
            }
            None => {
                eprintln!("thegent-git: {} not found in PATH", name);
                ExitCode::from(127)
            }
        }
    }
}

impl Default for GitShim {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_read_only() {
        let shim = GitShim::new();
        assert!(shim.is_read_only("status"));
        assert!(shim.is_read_only("diff"));
        assert!(shim.is_read_only("log"));
    }

    #[test]
    fn test_is_write() {
        let shim = GitShim::new();
        assert!(shim.is_write("commit"));
        assert!(shim.is_write("add"));
        assert!(!shim.is_write("status"));
    }

    #[test]
    fn test_is_agent() {
        let shim = GitShim::new();
        assert!(shim.is_agent("codex"));
        assert!(shim.is_agent("copilot"));
        assert!(!shim.is_agent("status"));
    }
}
