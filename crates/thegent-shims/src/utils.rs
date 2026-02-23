//! Utility functions for shims

use std::path::PathBuf;
use std::process::{Command, ExitCode};

/// Resolve a binary from PATH, preferring THEGENT_TOOL_BIN_PATH if set
pub fn resolve_binary(name: &str) -> Option<PathBuf> {
    // Check THEGENT_TOOL_BIN_PATH first (safe PATH for shims)
    if let Ok(tool_path) = std::env::var("THEGENT_TOOL_BIN_PATH") {
        let mut search_paths = tool_path.split(':').collect::<Vec<_>>();
        let path_env = std::env::var("PATH").unwrap_or_default();
        search_paths.extend(path_env.split(':'));

        for dir in search_paths {
            let candidate = std::path::Path::new(dir).join(name);
            if candidate.exists() && is_executable(&candidate) {
                return Some(candidate);
            }
        }
    }

    // Fall back to standard which() behavior
    which::which(name).ok()
}

/// Find first available tool from a list of candidates
pub fn first_available(candidates: &[&str]) -> Option<PathBuf> {
    for candidate in candidates {
        if let Ok(path) = which::which(candidate) {
            return Some(path);
        }
    }
    None
}

/// Check if a path is executable
fn is_executable(path: &std::path::Path) -> bool {
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        if let Ok(metadata) = std::fs::metadata(path) {
            let permissions = metadata.permissions();
            (permissions.mode() & 0o111) != 0
        } else {
            false
        }
    }
    #[cfg(not(unix))]
    {
        // On Windows, check if it has an executable extension
        if let Some(ext) = path.extension() {
            matches!(ext.to_str(), Some("exe" | "bat" | "cmd" | "com"))
        } else {
            false
        }
    }
}

/// Execute a command and return its exit code
pub fn exec_command(cmd: &str, args: &[String]) -> ExitCode {
    match Command::new(cmd).args(args).status() {
        Ok(status) => {
            let code = status.code().unwrap_or(1);
            ExitCode::from(code as u8)
        }
        Err(e) => {
            eprintln!("thegent-shims: failed to execute {}: {}", cmd, e);
            ExitCode::from(127)
        }
    }
}

/// Get repo root (for git operations)
pub fn get_repo_root() -> std::path::PathBuf {
    if let Some(path) = resolve_binary("git") {
        if let Ok(output) = Command::new(&path)
            .args(&["rev-parse", "--show-toplevel"])
            .output()
        {
            if output.status.success() {
                let root = String::from_utf8_lossy(&output.stdout).trim().to_string();
                if !root.is_empty() {
                    return std::path::PathBuf::from(root);
                }
            }
        }
    }
    std::path::PathBuf::from(".")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_binary() {
        // Should find common tools
        let git = resolve_binary("git");
        assert!(git.is_some() || which::which("git").is_err());
    }

    #[test]
    fn test_first_available() {
        // Should find at least one of these
        let result = first_available(&["sh", "bash", "zsh"]);
        assert!(result.is_some());
    }
}
