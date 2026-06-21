// SPDX-License-Identifier: MIT OR Apache-2.0
//! Hook utility functions migrated from hooks/lib/common.sh
//! Provides binary resolution, PATH handling, and tool detection

use std::path::{Path, PathBuf};
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

    let candidate_path =
        find_in_path(binary, &safe_path).ok_or_else(|| UtilsError::NotFound(binary.to_string()))?;

    // Check if it's a shim in ~/.local/bin
    if let Some(file_name) = candidate_path.file_name() {
        let file_name_str = file_name.to_string_lossy();
        if (file_name_str == binary || file_name_str == format!("{}.exe", binary))
            && candidate_path.to_string_lossy().contains("/.local/bin/")
        {
            return Err(UtilsError::IsShim(candidate_path.display().to_string()));
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
    std::env::var_os("PATH")
        .and_then(|path| find_in_path_os(cmd, path))
        .is_some()
}

/// Get safe PATH for tool resolution
pub fn get_safe_path() -> String {
    std::env::var("THEGENT_TOOL_BIN_PATH")
        .unwrap_or_else(|_| "/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin".to_string())
}

fn find_in_path(binary: &str, path: &str) -> Option<PathBuf> {
    find_in_path_os(binary, path)
}

fn find_in_path_os(binary: &str, path: impl AsRef<std::ffi::OsStr>) -> Option<PathBuf> {
    std::env::split_paths(path.as_ref()).find_map(|dir| find_in_dir(&dir, binary))
}

fn find_in_dir(dir: &Path, binary: &str) -> Option<PathBuf> {
    candidate_names(binary)
        .into_iter()
        .map(|name| dir.join(name))
        .find(|candidate| is_executable(candidate))
}

#[cfg(unix)]
fn is_executable(path: &Path) -> bool {
    use std::os::unix::fs::PermissionsExt;

    path.metadata()
        .map(|metadata| metadata.is_file() && metadata.permissions().mode() & 0o111 != 0)
        .unwrap_or(false)
}

#[cfg(not(unix))]
fn is_executable(path: &Path) -> bool {
    path.is_file()
}

fn candidate_names(binary: &str) -> Vec<String> {
    #[cfg(windows)]
    {
        if Path::new(binary).extension().is_some() {
            return vec![binary.to_string()];
        }

        let pathext =
            std::env::var("PATHEXT").unwrap_or_else(|_| ".COM;.EXE;.BAT;.CMD".to_string());
        let mut names = vec![binary.to_string()];
        names.extend(
            pathext
                .split(';')
                .filter(|ext| !ext.is_empty())
                .map(|ext| format!("{binary}{ext}")),
        );
        names
    }

    #[cfg(not(windows))]
    {
        vec![binary.to_string()]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_git_binary() {
        let temp = tempfile::NamedTempFile::new().unwrap();
        let orig_git_bin = std::env::var("THEGENT_GIT_BIN").ok();

        std::env::set_var("THEGENT_GIT_BIN", temp.path());
        assert_eq!(resolve_git_binary(), Some(temp.path().to_path_buf()));

        if let Some(value) = orig_git_bin {
            std::env::set_var("THEGENT_GIT_BIN", value);
        } else {
            std::env::remove_var("THEGENT_GIT_BIN");
        }
    }

    #[test]
    fn test_command_exists() {
        // Should find common commands
        assert!(command_exists("ls") || command_exists("dir"));
    }
}
