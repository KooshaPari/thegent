//! Hook utility functions migrated from hooks/lib/common.sh
//! Provides binary resolution, PATH handling, and tool detection

use std::path::PathBuf;
use std::process::Command;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum UtilsError {
    #[error("Binary not found: {0}")]
    NotFound(String),
    #[error("Binary is a shim: {0}")]
    IsShim(String),
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}

/// Resolve real binary from safe PATH, skipping shims in ~/.local/bin
/// Equivalent to resolve_real_binary() in common.sh
pub fn resolve_real_binary(binary: &str) -> Result<PathBuf, UtilsError> {
    let safe_path = std::env::var("THEGENT_TOOL_BIN_PATH")
        .unwrap_or_else(|_| "/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin".to_string());

    // Try to find binary in safe PATH
    let output = Command::new("command")
        .arg("-v")
        .arg(binary)
        .env("PATH", &safe_path)
        .output()?;

    if !output.status.success() {
        return Err(UtilsError::NotFound(binary.to_string()));
    }

    let candidate = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let candidate_path = PathBuf::from(&candidate);

    // Check if it's a shim in ~/.local/bin
    if let Some(file_name) = candidate_path.file_name() {
        let file_name_str = file_name.to_string_lossy();
        if (file_name_str == binary || file_name_str == format!("{}.exe", binary))
            && candidate.contains("/.local/bin/")
        {
            return Err(UtilsError::IsShim(candidate));
        }
    }

    // Verify it's executable
    if !candidate_path.is_file() {
        return Err(UtilsError::NotFound(binary.to_string()));
    }

    Ok(candidate_path)
}

/// Resolve git binary, caching result
pub fn resolve_git_binary() -> Option<PathBuf> {
    // Check environment variable first
    if let Ok(git_bin) = std::env::var("THEGENT_GIT_BIN") {
        let path = PathBuf::from(git_bin);
        if path.is_file() {
            return Some(path);
        }
    }

    // Try to resolve
    resolve_real_binary("git").ok()
}

/// Check if a command exists in PATH
pub fn command_exists(cmd: &str) -> bool {
    Command::new("command")
        .arg("-v")
        .arg(cmd)
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

/// Get safe PATH for tool resolution
pub fn get_safe_path() -> String {
    std::env::var("THEGENT_TOOL_BIN_PATH")
        .unwrap_or_else(|_| "/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_git_binary() {
        // Should find git if it exists
        if command_exists("git") {
            assert!(resolve_git_binary().is_some());
        }
    }

    #[test]
    fn test_command_exists() {
        // Should find common commands
        assert!(command_exists("ls") || command_exists("dir"));
    }
}
