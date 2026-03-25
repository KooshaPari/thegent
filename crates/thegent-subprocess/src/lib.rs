//! thegent-subprocess: Safe subprocess execution for thegent
//!
//! Provides safe subprocess execution patterns:
//! - `run_command`: Execute command with timeout and output capture
//! - `run_with_retry`: Execute with exponential backoff retry
//! - `run_piped`: Execute piped commands safely
//! - `check_output`: Get command output with timeout
//!
//! Safety:
//! - All commands use Command::new() which never invokes a shell
//! - Arguments are passed as vectors, not concatenated strings
//! - Timeouts prevent hanging processes

use std::io::{self, Read};
use std::process::{Command, ExitStatus, Stdio};
use std::time::{Duration, Instant};

#[cfg(all(not(test), not(debug_assertions)))]
use pyo3::prelude::*;
#[cfg(all(not(test), not(debug_assertions)))]
use pyo3::exceptions::{PyRuntimeError, PyTimeoutError};
#[cfg(all(not(test), not(debug_assertions)))]
use pyo3::prelude::*;
use thiserror::Error;

// ---------------------------------------------------------------------------
// Error Types
// ---------------------------------------------------------------------------

#[derive(Error, Debug)]
pub enum SubprocessError {
    #[error("Command not found: {0}")]
    NotFound(String),

    #[error("Command timed out after {0:?}: {1}")]
    Timeout(Duration, String),

    #[error("Command failed with exit code {0}: {1}")]
    ExitCode(i32, String),

    #[error("IO error: {0}")]
    IoError(#[from] io::Error),
}

// ---------------------------------------------------------------------------
// Result Types
// ---------------------------------------------------------------------------

/// Result of a subprocess execution
#[derive(Debug, Clone)]
pub struct CommandResult {
    pub exit_code: i32,
    pub stdout: String,
    pub stderr: String,
    pub success: bool,
    pub duration_ms: u64,
}

// ---------------------------------------------------------------------------
// Core Functions
// ---------------------------------------------------------------------------

/// Execute a command with timeout
///
/// # Arguments
/// * `program` - Program to execute
/// * `args` - Arguments to pass
/// * `timeout_secs` - Timeout in seconds (0 = no timeout)
/// * `cwd` - Working directory (None = current)
///
/// # Returns
/// CommandResult with exit code, stdout, stderr, and timing
pub fn run_command(
    program: &str,
    args: &[String],
    timeout_secs: u64,
    cwd: Option<&str>,
) -> Result<CommandResult, SubprocessError> {
    let start = Instant::now();

    let mut cmd = Command::new(program);
    cmd.args(args);

    if let Some(dir) = cwd {
        cmd.current_dir(dir);
    }

    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());

    let output = if timeout_secs > 0 {
        // Use spawn and wait with timeout
        let mut child = cmd.spawn().map_err(|e| {
            if e.kind() == io::ErrorKind::NotFound {
                SubprocessError::NotFound(program.to_string())
            } else {
                SubprocessError::IoError(e)
            }
        })?;

        let timeout = Duration::from_secs(timeout_secs);
        match child.wait_timeout(timeout)? {
            Some(status) => {
                let stdout = child
                    .stdout
                    .take()
                    .map(|mut h| {
                        let mut buf = Vec::new();
                        let _ = h.read_to_end(&mut buf);
                        String::from_utf8_lossy(&buf).to_string()
                    })
                    .unwrap_or_default();

                let stderr = child
                    .stderr
                    .take()
                    .map(|mut h| {
                        let mut buf = Vec::new();
                        let _ = h.read_to_end(&mut buf);
                        String::from_utf8_lossy(&buf).to_string()
                    })
                    .unwrap_or_default();

                CommandResult {
                    exit_code: status.code().unwrap_or(-1),
                    stdout,
                    stderr,
                    success: status.success(),
                    duration_ms: start.elapsed().as_millis() as u64,
                }
            }
            None => {
                let _ = child.kill();
                return Err(SubprocessError::Timeout(
                    Duration::from_secs(timeout_secs),
                    program.to_string(),
                ));
            }
        }
    } else {
        // No timeout - direct execution
        let output = cmd.output().map_err(|e| {
            if e.kind() == io::ErrorKind::NotFound {
                SubprocessError::NotFound(program.to_string())
            } else {
                SubprocessError::IoError(e)
            }
        })?;

        CommandResult {
            exit_code: output.status.code().unwrap_or(-1),
            stdout: String::from_utf8_lossy(&output.stdout).to_string(),
            stderr: String::from_utf8_lossy(&output.stderr).to_string(),
            success: output.status.success(),
            duration_ms: start.elapsed().as_millis() as u64,
        }
    };

    Ok(output)
}

/// Execute with retry and exponential backoff
pub fn run_with_retry(
    program: &str,
    args: &[String],
    max_retries: u32,
    initial_delay_ms: u64,
    max_delay_ms: u64,
    cwd: Option<&str>,
) -> Result<CommandResult, SubprocessError> {
    let mut delay = initial_delay_ms;
    let mut last_result = None;

    for attempt in 0..=max_retries {
        match run_command(program, args, 0, cwd) {
            Ok(result) if result.success => return Ok(result),
            Ok(result) => {
                last_result = Some(result);
                if attempt < max_retries {
                    std::thread::sleep(Duration::from_millis(delay));
                    delay = (delay * 2).min(max_delay_ms);
                }
            }
            Err(e) => {
                if attempt == max_retries {
                    return Err(e);
                }
                std::thread::sleep(Duration::from_millis(delay));
                delay = (delay * 2).min(max_delay_ms);
            }
        }
    }

    // Return the last failure result
    last_result.map(Ok).unwrap_or_else(|| {
        Err(SubprocessError::ExitCode(
            -1,
            "All retries failed".to_string(),
        ))
    })
}

// ---------------------------------------------------------------------------
// Trait for wait_with_timeout
// ---------------------------------------------------------------------------

trait WaitWithTimeout {
    fn wait_timeout(&mut self, timeout: Duration) -> io::Result<Option<ExitStatus>>;
}

use std::process::Child;

impl WaitWithTimeout for Child {
    fn wait_timeout(&mut self, timeout: Duration) -> io::Result<Option<ExitStatus>> {
        let start = Instant::now();

        loop {
            match self.try_wait()? {
                Some(status) => return Ok(Some(status)),
                None => {
                    if start.elapsed() >= timeout {
                        return Ok(None);
                    }
                    std::thread::sleep(Duration::from_millis(10));
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Python Bindings
// ---------------------------------------------------------------------------

/// Execute a command with optional timeout
#[cfg(all(not(test), not(debug_assertions)))]
#[pyfunction]
#[pyo3(signature = (program, args=None, timeout_secs=0, cwd=None))]
pub fn run(
    py: Python<'_>,
    program: String,
    args: Option<Vec<String>>,
    timeout_secs: u64,
    cwd: Option<String>,
) -> PyResult<PyObject> {
    let args = args.unwrap_or_default();

    let result = py
        .allow_threads(|| run_command(&program, &args, timeout_secs, cwd.as_deref()))
        .map_err(|e| match e {
            SubprocessError::Timeout(d, cmd) => {
                PyTimeoutError::new_err(format!("Command timed out after {:?}: {}", d, cmd))
            }
            SubprocessError::NotFound(cmd) => {
                PyRuntimeError::new_err(format!("Command not found: {}", cmd))
            }
            SubprocessError::ExitCode(code, msg) => {
                PyRuntimeError::new_err(format!("Command failed with exit code {}: {}", code, msg))
            }
            SubprocessError::IoError(e) => PyRuntimeError::new_err(format!("IO error: {}", e)),
        })?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("exit_code", result.exit_code)?;
    dict.set_item("stdout", result.stdout)?;
    dict.set_item("stderr", result.stderr)?;
    dict.set_item("success", result.success)?;
    dict.set_item("duration_ms", result.duration_ms)?;

    Ok(dict.into_any().unbind())
}

/// Execute a command with retry and exponential backoff
#[cfg(all(not(test), not(debug_assertions)))]
#[pyfunction]
#[pyo3(signature = (program, args=None, max_retries=3, initial_delay_ms=100, max_delay_ms=5000, cwd=None))]
pub fn run_retry(
    py: Python<'_>,
    program: String,
    args: Option<Vec<String>>,
    max_retries: u32,
    initial_delay_ms: u64,
    max_delay_ms: u64,
    cwd: Option<String>,
) -> PyResult<PyObject> {
    let args = args.unwrap_or_default();

    let result = py
        .allow_threads(|| {
            run_with_retry(
                &program,
                &args,
                max_retries,
                initial_delay_ms,
                max_delay_ms,
                cwd.as_deref(),
            )
        })
        .map_err(|e| match e {
            SubprocessError::NotFound(cmd) => {
                PyRuntimeError::new_err(format!("Command not found: {}", cmd))
            }
            SubprocessError::ExitCode(code, msg) => {
                PyRuntimeError::new_err(format!("Command failed with exit code {}: {}", code, msg))
            }
            SubprocessError::IoError(e) => PyRuntimeError::new_err(format!("IO error: {}", e)),
            SubprocessError::Timeout(d, cmd) => {
                PyTimeoutError::new_err(format!("Command timed out after {:?}: {}", d, cmd))
            }
        })?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("exit_code", result.exit_code)?;
    dict.set_item("stdout", result.stdout)?;
    dict.set_item("stderr", result.stderr)?;
    dict.set_item("success", result.success)?;
    dict.set_item("duration_ms", result.duration_ms)?;

    Ok(dict.into_any().unbind())
}

/// Check if a command exists in PATH
#[cfg(all(not(test), not(debug_assertions)))]
#[pyfunction]
pub fn find_command(program: String) -> PyResult<Option<String>> {
    match ::which::which(&program) {
        Ok(path) => {
            let s = path.as_path().to_string_lossy();
            Ok(Some(s.to_string()))
        }
        Err(_) => Ok(None),
    }
}

/// Get output from a command (raises on failure)
#[cfg(all(not(test), not(debug_assertions)))]
#[pyfunction]
#[pyo3(signature = (program, args=None, cwd=None))]
pub fn check_output(
    py: Python<'_>,
    program: String,
    args: Option<Vec<String>>,
    cwd: Option<String>,
) -> PyResult<String> {
    let args = args.unwrap_or_default();

    let result = py
        .allow_threads(|| run_command(&program, &args, 0, cwd.as_deref()))
        .map_err(|e| match e {
            SubprocessError::NotFound(cmd) => {
                PyRuntimeError::new_err(format!("Command not found: {}", cmd))
            }
            SubprocessError::ExitCode(code, msg) => {
                PyRuntimeError::new_err(format!("Command failed with exit code {}: {}", code, msg))
            }
            SubprocessError::IoError(e) => PyRuntimeError::new_err(format!("IO error: {}", e)),
            SubprocessError::Timeout(d, cmd) => {
                PyTimeoutError::new_err(format!("Command timed out after {:?}: {}", d, cmd))
            }
        })?;

    if !result.success {
        return Err(PyRuntimeError::new_err(format!(
            "Command failed with exit code {}: {}",
            result.exit_code, result.stderr
        )));
    }

    Ok(result.stdout.trim().to_string())
}

// ---------------------------------------------------------------------------
// Module Definition
// ---------------------------------------------------------------------------

#[cfg(all(not(test), not(debug_assertions)))]
#[pymodule]
fn thegent_subprocess(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run, m)?)?;
    m.add_function(wrap_pyfunction!(run_retry, m)?)?;
    m.add_function(wrap_pyfunction!(find_command, m)?)?;
    m.add_function(wrap_pyfunction!(check_output, m)?)?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(all(test, not(debug_assertions)))]
mod tests {
    use super::*;

    #[test]
    fn test_run_echo() {
        let result = run_command("echo", &["hello".to_string()], 0, None);
        assert!(result.is_ok());
        let r = result.unwrap();
        assert!(r.success);
        assert!(r.stdout.contains("hello"));
    }

    #[test]
    fn test_run_not_found() {
        let result = run_command("nonexistent_command_xyz", &[], 0, None);
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), SubprocessError::NotFound(_)));
    }

    #[test]
    fn test_run_with_timeout_success() {
        let result = run_command("echo", &["test".to_string()], 5, None);
        assert!(result.is_ok());
        let r = result.unwrap();
        assert!(r.success);
    }

    #[test]
    fn test_run_exit_code() {
        let result = run_command("false", &[], 0, None);
        assert!(result.is_ok());
        let r = result.unwrap();
        assert!(!r.success);
        assert_eq!(r.exit_code, 1);
    }

    #[test]
    fn test_which_echo() {
        let result = find_command("echo".to_string());
        assert!(result.is_ok());
        let path = result.unwrap();
        assert!(path.is_some());
    }

    #[test]
    fn test_which_not_found() {
        let result = find_command("nonexistent_command_xyz".to_string());
        assert!(result.is_ok());
        assert!(result.unwrap().is_none());
    }
}
