//! File discovery utilities migrated from hooks/lib/fd-wrapper.sh
//! Provides fast file discovery using fd when available, with fallback to find

use std::path::PathBuf;
use std::process::{Command, Stdio};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum FileDiscoveryError {
    #[error("Command execution failed: {0}")]
    CommandFailed(String),
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}

/// Find files using fd when available, fallback to find
/// Equivalent to fd_find() in fd-wrapper.sh
pub fn find_files(
    pattern: Option<&str>,
    max_depth: Option<usize>,
    file_type: Option<FileType>,
    dir: Option<&str>,
) -> Result<Vec<PathBuf>, FileDiscoveryError> {
    let dir = dir.unwrap_or(".");

    // Try fd first if available
    if command_exists("fd") {
        if let Ok(files) = find_with_fd(pattern, max_depth, file_type, dir) {
            return Ok(files);
        }
    }

    // Fallback to find
    find_with_find(pattern, max_depth, file_type, dir)
}

#[derive(Debug, Clone, Copy)]
pub enum FileType {
    File,
    Directory,
}

fn command_exists(cmd: &str) -> bool {
    crate::utils::command_exists(cmd)
}

fn find_with_fd(
    pattern: Option<&str>,
    max_depth: Option<usize>,
    file_type: Option<FileType>,
    dir: &str,
) -> Result<Vec<PathBuf>, FileDiscoveryError> {
    let mut cmd = Command::new("fd");

    if let Some(pattern) = pattern {
        cmd.arg(pattern);
    } else {
        cmd.arg(".");
    }

    if let Some(depth) = max_depth {
        cmd.arg("--max-depth").arg(depth.to_string());
    }

    if let Some(ft) = file_type {
        match ft {
            FileType::File => cmd.arg("--type").arg("f"),
            FileType::Directory => cmd.arg("--type").arg("d"),
        };
    }

    cmd.arg(dir);

    let output = cmd.stdout(Stdio::piped()).stderr(Stdio::null()).output()?;

    if !output.status.success() {
        return Err(FileDiscoveryError::CommandFailed(
            "fd command failed".to_string(),
        ));
    }

    let files: Vec<PathBuf> = String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(|line| PathBuf::from(line.trim()))
        .collect();

    Ok(files)
}

fn find_with_find(
    pattern: Option<&str>,
    max_depth: Option<usize>,
    file_type: Option<FileType>,
    dir: &str,
) -> Result<Vec<PathBuf>, FileDiscoveryError> {
    let mut cmd = Command::new("find");
    cmd.arg(dir);

    if let Some(depth) = max_depth {
        cmd.arg("-maxdepth").arg(depth.to_string());
    }

    if let Some(ft) = file_type {
        match ft {
            FileType::File => cmd.arg("-type").arg("f"),
            FileType::Directory => cmd.arg("-type").arg("d"),
        };
    }

    if let Some(pattern) = pattern {
        // Remove quotes if present
        let pattern = pattern.trim_matches('"').trim_matches('\'');
        cmd.arg("-name").arg(pattern);
    }

    let output = cmd.stdout(Stdio::piped()).stderr(Stdio::null()).output()?;

    if !output.status.success() {
        return Err(FileDiscoveryError::CommandFailed(
            "find command failed".to_string(),
        ));
    }

    let files: Vec<PathBuf> = String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(|line| PathBuf::from(line.trim()))
        .collect();

    Ok(files)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_find_files() {
        if !command_exists("fd") && (!command_exists("find") || cfg!(windows)) {
            return;
        }

        let temp = tempfile::TempDir::new().unwrap();
        std::fs::write(temp.path().join("sample.txt"), "sample").unwrap();

        let dir = temp.path().to_string_lossy();
        let result = find_files(
            Some("sample.txt"),
            Some(1),
            Some(FileType::File),
            Some(&dir),
        );
        assert!(result.is_ok());
        assert!(!result.unwrap().is_empty());
    }
}
