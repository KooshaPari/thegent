use serde::{Deserialize, Serialize};
use regex::Regex;
use std::collections::HashMap;
use std::process::Command;
use pyo3::prelude::*;
use pyo3::types::PyModule;

#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct DiscoveredAgent {
    #[pyo3(get)]
    pub pid: u32,
    #[pyo3(get)]
    pub ppid: u32,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub cmd: String,
    #[pyo3(get)]
    pub cwd: String,
    #[pyo3(get)]
    pub session_id: Option<String>,
    #[pyo3(get)]
    pub memory_kb: u64,
    #[pyo3(get)]
    pub cpu_usage: f32,
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
            .args(&["ax", "-o", "pid,ppid,comm,command,rss,cputime"])
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
                let cmd = parts[3..parts.len()-2].join(" ");
                let cmd_lower = cmd.to_lowercase();
                let name_lower = name.to_lowercase();
                let memory_kb: u64 = parts[parts.len()-2].parse().unwrap_or(0);
                
                // Parse CPU time (format: MM:SS or HH:MM:SS)
                let cpu_time_str = parts[parts.len()-1];
                let cpu_usage = Self::parse_cpu_time_to_percent(cpu_time_str);

                let agent_name: Option<String> = if cmd_lower.contains("cursor-agent") 
                    || cmd_lower.contains("cursor agent") 
                    || (cmd_lower.contains("cursor") && cmd.contains("--resume=")) {
                    Some("cursor-agent".to_string())
                } else if cmd_lower.contains("claude-code") 
                    || cmd_lower.contains("claude code") 
                    || cmd_lower.contains("clode") 
                    || name_lower.starts_with("claude") 
                    || name_lower.starts_with("clode") {
                    Some("claude-code".to_string())
                } else if name_lower == "codex" 
                    || cmd_lower.contains("codex") 
                    || cmd_lower.contains("dex") {
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
            },
            2 => {
                let mins: u32 = parts[0].parse().unwrap_or(0);
                let secs: u32 = parts[1].parse().unwrap_or(0);
                mins * 60 + secs
            },
            _ => parts[0].parse().unwrap_or(0),
        };
        
        // Rough estimate: if process has been running for N seconds, 
        // and we're sampling, this is just a placeholder
        (seconds as f32 * 0.01).min(100.0)
    }

    fn get_cwd_for_pid(pid: u32) -> Option<String> {
        let lsof_output = Command::new("lsof")
            .args(&["-p", &pid.to_string(), "-d", "cwd", "-t"])
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
            .args(&["hw.ncpu", "hw.memsize"])
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
                                info.insert("memory_gb".to_string(), mem_bytes / (1024.0 * 1024.0 * 1024.0));
                            }
                        }
                    }
                }
            }
        }
        
        info
    }
}

#[pyclass]
struct PyDiscoveryManager {
    manager: DiscoveryManager,
}

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

#[pymodule]
fn thegent_discovery(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyDiscoveryManager>()?;
    m.add_class::<DiscoveredAgent>()?;
    Ok(())
}
