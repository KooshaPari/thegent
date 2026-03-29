//! Fast grep wrapper with ripgrep integration (safe execution)
//!
//! Routes to ripgrep for 2-10x speedup on recursive searches.
//! Detects patterns and intelligently falls back to grep when needed.
//!
//! NOTE: Uses std::process::Command which is safe from shell injection
//! (unlike shell exec, Command never invokes a shell)

use crate::utils::resolve_binary;
use std::path::PathBuf;
use std::process::{Command, ExitCode};

pub struct GrepShim {
    rg_bin: Option<PathBuf>,
    grep_bin: Option<PathBuf>,
}

impl GrepShim {
    pub fn new() -> Self {
        let rg_bin = resolve_binary("rg");
        let grep_bin = resolve_binary("grep").or_else(|| resolve_binary("ggrep"));

        Self { rg_bin, grep_bin }
    }

    /// Check if args request recursive search
    fn is_recursive(args: &[String]) -> bool {
        for arg in args {
            match arg.as_str() {
                "-r" | "-R" | "-rE" | "-ro" | "-roE" | "-rH" | "-rHo" | "-rHoE" | "-rEl"
                | "-rEh" | "-rn" => return true,
                _ => {}
            }
        }
        false
    }

    /// Check if args contain patterns that should use grep instead of rg
    fn should_use_grep(args: &[String]) -> bool {
        for arg in args {
            match arg.as_str() {
                "-P" | "--perl-regexp" => return true,
                _ if arg.starts_with("--include=") || arg.starts_with("--include-dir=") => {
                    return true;
                }
                _ => {}
            }
        }
        false
    }

    /// Convert grep args to ripgrep equivalents (safe - Command avoids shell)
    fn convert_to_rg(args: &[String]) -> Vec<String> {
        let mut rg_args = vec!["--no-config".to_string()];
        let mut i = 0;

        while i < args.len() {
            let arg = &args[i];
            match arg.as_str() {
                // Copy through relevant flags
                "-n" | "-nE" | "-En" => rg_args.push("-n".to_string()),
                "-o" | "-oE" | "-Eo" => rg_args.push("-o".to_string()),
                "-c" | "-cE" | "-Ec" => rg_args.push("-c".to_string()),
                "-q" | "-qE" | "-Eq" => rg_args.push("-q".to_string()),
                "-l" | "-lE" | "-El" => rg_args.push("-l".to_string()),
                "-L" | "-LE" | "-EL" => rg_args.push("-L".to_string()),
                "-v" | "-vE" | "-Ev" => rg_args.push("-v".to_string()),
                "-i" | "-iE" | "-Ei" => rg_args.push("-i".to_string()),
                "-E" => {
                    // Skip -E (rg is always ERE)
                }
                "-m" => {
                    // Max count
                    if i + 1 < args.len() {
                        i += 1;
                        rg_args.push("--max-count".to_string());
                        rg_args.push(args[i].clone());
                    }
                }
                "-A" | "-B" | "-C" | "--after-context" | "--before-context" | "--context" => {
                    // Context flags
                    if i + 1 < args.len() {
                        rg_args.push(arg.clone());
                        i += 1;
                        rg_args.push(args[i].clone());
                    }
                }
                "-e" | "--regexp" => {
                    // Pattern flag
                    if i + 1 < args.len() {
                        i += 1;
                        rg_args.push("-e".to_string());
                        rg_args.push(args[i].clone());
                    }
                }
                "-f" | "--file" => {
                    // Patterns from file
                    if i + 1 < args.len() {
                        i += 1;
                        rg_args.push("-f".to_string());
                        rg_args.push(args[i].clone());
                    }
                }
                // Grep recursive bundles: rg is recursive by default, so strip -r/-R and keep only meaningful suffixes.
                "-r" | "-R" | "-rE" => {}
                "-rn" => rg_args.push("-n".to_string()),
                "-ro" | "-roE" => rg_args.push("-o".to_string()),
                "-rH" => rg_args.push("-H".to_string()),
                "-rHo" | "-rHoE" => {
                    rg_args.push("-H".to_string());
                    rg_args.push("-o".to_string());
                }
                "-rEl" => rg_args.push("-l".to_string()),
                "-rEh" => rg_args.push("-h".to_string()),
                _ => {
                    // Pass through all other args (safe - Command avoids shell interpretation)
                    rg_args.push(arg.clone());
                }
            }
            i += 1;
        }

        rg_args
    }

    /// Execute grep with optional ripgrep acceleration
    pub fn exec(&self, args: &[String]) -> ExitCode {
        // Use grep if no rg available
        if self.rg_bin.is_none() {
            return self.exec_grep(args);
        }

        // Use grep for patterns that don't translate well
        if Self::should_use_grep(args) {
            return self.exec_grep(args);
        }

        // For recursive searches, try ripgrep
        if Self::is_recursive(args) {
            return self.exec_rg(args);
        }

        // For simple patterns, try ripgrep
        self.exec_rg(args)
    }

    /// Execute ripgrep (fast path) - safe with Command
    fn exec_rg(&self, args: &[String]) -> ExitCode {
        match &self.rg_bin {
            Some(rg_path) => {
                let rg_args = Self::convert_to_rg(args);

                // Add default excludes if not already specified
                let mut final_args = rg_args.clone();
                let has_exclude = rg_args.iter().any(|a| a.starts_with("-g"));
                if !has_exclude {
                    let excludes = vec![
                        "!node_modules",
                        "!vendor",
                        "!.git",
                        "!target",
                        "!out",
                        "!dist",
                        "!build",
                        "!coverage",
                        "!__pycache__",
                        "!.venv",
                    ];
                    for exclude in excludes {
                        final_args.push("-g".to_string());
                        final_args.push(exclude.to_string());
                    }
                }

                // Command::new() is safe from injection
                match Command::new(rg_path).args(&final_args).status() {
                    Ok(status) => {
                        let code = status.code().unwrap_or(1);
                        ExitCode::from(code as u8)
                    }
                    Err(_) => {
                        // Fall back to grep if rg fails
                        self.exec_grep(args)
                    }
                }
            }
            None => self.exec_grep(args),
        }
    }

    /// Execute grep (fallback) - safe with Command
    fn exec_grep(&self, args: &[String]) -> ExitCode {
        match &self.grep_bin {
            Some(grep_path) => {
                // Command::new() is safe from injection
                match Command::new(grep_path).args(args).status() {
                    Ok(status) => {
                        let code = status.code().unwrap_or(1);
                        ExitCode::from(code as u8)
                    }
                    Err(e) => {
                        eprintln!("thegent-grep: failed to execute grep: {}", e);
                        ExitCode::from(127)
                    }
                }
            }
            None => {
                eprintln!("thegent-grep: grep not found in PATH");
                ExitCode::from(127)
            }
        }
    }
}

impl Default for GrepShim {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_recursive() {
        let args = vec!["-r".to_string(), "pattern".to_string()];
        assert!(GrepShim::is_recursive(&args));

        let args = vec!["-n".to_string(), "pattern".to_string(), "file".to_string()];
        assert!(!GrepShim::is_recursive(&args));
    }

    #[test]
    fn test_should_use_grep() {
        let args = vec!["-P".to_string(), "pattern".to_string()];
        assert!(GrepShim::should_use_grep(&args));

        let args = vec!["-r".to_string(), "pattern".to_string()];
        assert!(!GrepShim::should_use_grep(&args));
    }

    #[test]
    fn test_convert_to_rg() {
        let args = vec!["-rn".to_string(), "pattern".to_string(), "file".to_string()];
        let rg_args = GrepShim::convert_to_rg(&args);
        assert!(rg_args.iter().any(|a| a == "-n"));
        assert!(rg_args.iter().any(|a| a == "pattern"));
    }
}
