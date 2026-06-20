// SPDX-License-Identifier: MIT OR Apache-2.0
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::process::Command;

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
use pyo3::prelude::*;
#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
use pyo3::types::PyModule;

#[derive(Debug, Serialize, Deserialize, Clone)]
#[cfg_attr(all(feature = "python", not(test), not(debug_assertions)), pyclass)]
pub struct DiscoveredAgent {
    pub pid: u32,
    pub ppid: u32,
    pub name: String,
    pub cmd: String,
    pub cwd: String,
    pub session_id: Option<String>,
    pub memory_kb: u64,
    pub cpu_usage: f32,
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pymethods]
impl DiscoveredAgent {
    #[getter]
    fn get_pid(&self) -> u32 {
        self.pid
    }

    #[getter]
    fn get_ppid(&self) -> u32 {
        self.ppid
    }

    #[getter]
    fn get_name(&self) -> String {
        self.name.clone()
    }

    #[getter]
    fn get_cmd(&self) -> String {
        self.cmd.clone()
    }

    #[getter]
    fn get_cwd(&self) -> String {
        self.cwd.clone()
    }

    #[getter]
    fn get_session_id(&self) -> Option<String> {
        self.session_id.clone()
    }

    #[getter]
    fn get_memory_kb(&self) -> u64 {
        self.memory_kb
    }

    #[getter]
    fn get_cpu_usage(&self) -> f32 {
        self.cpu_usage
    }
}

pub struct DiscoveryManager {
    resume_re: Regex,
}

impl DiscoveryManager {
    pub fn new() -> Self {
        Self {
            resume_re: Regex::new(r"--resume=([a-f0-9\-]+)").unwrap(),
        }
    }

    pub fn scan_agents(&mut self) -> Vec<DiscoveredAgent> {
        let mut agents: Vec<DiscoveredAgent> = Vec::new();
        let re = &self.resume_re;

        // Get all process info from ps in one call
        let ps_output = Command::new("ps")
            .args(["ax", "-o", "pid,ppid,comm,command,rss,cputime"])
            .output()
            .expect("Failed to run ps");

        if let Ok(output_str) = String::from_utf8(ps_output.stdout) {
            for line in output_str.lines().skip(1) {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() < 6 {
                    continue;
                }

                let pid: u32 = parts[0].parse().unwrap_or(0);
                let ppid: u32 = parts[1].parse().unwrap_or(0);
                let name = parts[2].to_string();
                let cmd = parts[3..parts.len() - 2].join(" ");
                let cmd_lower = cmd.to_lowercase();
                let name_lower = name.to_lowercase();
                let memory_kb: u64 = parts[parts.len() - 2].parse().unwrap_or(0);

                // Parse CPU time (format: MM:SS or HH:MM:SS)
                let cpu_time_str = parts[parts.len() - 1];
                let cpu_usage = Self::parse_cpu_time_to_percent(cpu_time_str);

                let agent_name: Option<String> = if cmd_lower.contains("cursor-agent")
                    || cmd_lower.contains("cursor agent")
                    || (cmd_lower.contains("cursor") && cmd.contains("--resume="))
                {
                    Some("cursor-agent".to_string())
                } else if cmd_lower.contains("claude-code")
                    || cmd_lower.contains("claude code")
                    || cmd_lower.contains("clode")
                    || name_lower.starts_with("claude")
                    || name_lower.starts_with("clode")
                {
                    Some("claude-code".to_string())
                } else if name_lower == "codex"
                    || cmd_lower.contains("codex")
                    || cmd_lower.contains("dex")
                {
                    Some("codex".to_string())
                } else {
                    None
                };

                if let Some(final_name) = agent_name {
                    let mut session_id: Option<String> = None;
                    if let Some(caps) = re.captures(&cmd) {
                        if let Some(m) = caps.get(1) {
                            session_id = Some(m.as_str().to_string());
                        }
                    }

                    let cwd = Self::get_cwd_for_pid(pid).unwrap_or_else(|| String::from("unknown"));

                    agents.push(DiscoveredAgent {
                        pid,
                        ppid,
                        name: final_name,
                        cmd,
                        cwd,
                        session_id,
                        memory_kb,
                        cpu_usage,
                    });
                }
            }
        }
        agents
    }

    fn parse_cpu_time_to_percent(time_str: &str) -> f32 {
        // Very rough approximation - parse time and estimate %
        let parts: Vec<&str> = time_str.split(":").collect();
        let seconds: u32 = match parts.len() {
            3 => {
                let hours: u32 = parts[0].parse().unwrap_or(0);
                let mins: u32 = parts[1].parse().unwrap_or(0);
                let secs: u32 = parts[2].parse().unwrap_or(0);
                hours * 3600 + mins * 60 + secs
            }
            2 => {
                let mins: u32 = parts[0].parse().unwrap_or(0);
                let secs: u32 = parts[1].parse().unwrap_or(0);
                mins * 60 + secs
            }
            _ => parts[0].parse().unwrap_or(0),
        };

        // Rough estimate: if process has been running for N seconds,
        // and we're sampling, this is just a placeholder
        (seconds as f32 * 0.01).min(100.0)
    }

    fn get_cwd_for_pid(pid: u32) -> Option<String> {
        let lsof_output = Command::new("lsof")
            .args(["-p", &pid.to_string(), "-d", "cwd", "-t"])
            .output();

        if let Ok(output) = lsof_output {
            if let Ok(output_str) = String::from_utf8(output.stdout) {
                let path = output_str.trim();
                if !path.is_empty() {
                    return Some(path.to_string());
                }
            }
        }
        None
    }

    pub fn get_system_info(&self) -> HashMap<String, f64> {
        let mut info = HashMap::new();

        // Get CPU count
        let sysctl_output = Command::new("sysctl")
            .args(["hw.ncpu", "hw.memsize"])
            .output();

        if let Ok(output) = sysctl_output {
            if let Ok(output_str) = String::from_utf8(output.stdout) {
                for line in output_str.lines() {
                    let parts: Vec<&str> = line.split(":").collect();
                    if parts.len() == 2 {
                        let key = parts[0].trim();
                        let value = parts[1].trim();
                        if key == "hw.ncpu" {
                            if let Ok(ncpu) = value.parse::<f64>() {
                                info.insert("cpus".to_string(), ncpu);
                            }
                        } else if key == "hw.memsize" {
                            if let Ok(mem_bytes) = value.parse::<f64>() {
                                info.insert(
                                    "memory_gb".to_string(),
                                    mem_bytes / (1024.0 * 1024.0 * 1024.0),
                                );
                            }
                        }
                    }
                }
            }
        }

        info
    }
}

impl Default for DiscoveryManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pyclass]
struct PyDiscoveryManager {
    manager: DiscoveryManager,
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pymethods]
impl PyDiscoveryManager {
    #[new]
    fn new() -> Self {
        Self {
            manager: DiscoveryManager::new(),
        }
    }

    fn scan_agents(&mut self) -> Vec<DiscoveredAgent> {
        self.manager.scan_agents()
    }

    fn get_system_info(&self) -> HashMap<String, f64> {
        self.manager.get_system_info()
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
#[pymodule]
fn thegent_discovery(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDiscoveryManager>()?;
    m.add_class::<DiscoveredAgent>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_discovery_manager_creation() {
        let manager = DiscoveryManager::new();
        // Verify regex is compiled correctly by checking it can match
        assert!(manager.resume_re.is_match("--resume=abc123-def456"));
    }

    #[test]
    fn test_resume_regex_matches() {
        let re = Regex::new(r"--resume=([a-f0-9\-]+)").unwrap();

        // Valid session IDs
        assert!(re.is_match("codex --resume=abc123"));
        assert!(re.is_match("cursor-agent --resume=a1b2c3d4-e5f6-7890-abcd-ef1234567890"));

        // Extract session ID
        let caps = re.captures("claude --resume=deadbeef-1234").unwrap();
        assert_eq!(caps.get(1).map(|m| m.as_str()), Some("deadbeef-1234"));
    }

    #[test]
    fn test_resume_regex_no_match() {
        let re = Regex::new(r"--resume=([a-f0-9\-]+)").unwrap();

        // Should not match invalid patterns
        assert!(!re.is_match("codex --resume="));
        assert!(!re.is_match("codex"));
        assert!(!re.is_match("--resume=XYZ")); // Invalid hex chars
    }

    #[test]
    fn test_discovered_agent_defaults() {
        let agent = DiscoveredAgent {
            pid: 12345,
            ppid: 1,
            name: "test-agent".to_string(),
            cmd: "/usr/bin/test".to_string(),
            cwd: "/home/user".to_string(),
            session_id: None,
            memory_kb: 1024,
            cpu_usage: 0.5,
        };

        assert_eq!(agent.pid, 12345);
        assert_eq!(agent.ppid, 1);
        assert_eq!(agent.name, "test-agent");
        assert!(agent.session_id.is_none());
    }

    #[test]
    fn test_discovered_agent_with_session() {
        let agent = DiscoveredAgent {
            pid: 54321,
            ppid: 1000,
            name: "claude-code".to_string(),
            cmd: "claude --resume=abc123".to_string(),
            cwd: "/workspace".to_string(),
            session_id: Some("abc123".to_string()),
            memory_kb: 2048,
            cpu_usage: 1.5,
        };

        assert_eq!(agent.session_id, Some("abc123".to_string()));
    }
}
