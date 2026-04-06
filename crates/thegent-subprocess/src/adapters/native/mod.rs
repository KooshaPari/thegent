//! # Native Process Executor
//!
//! Production implementation using the native `Command` API.
//!
//! On macOS this adapter enforces:
//! - **nice** priority via `libc::setpriority` in a pre-exec hook
//! - **resource limits** (CPU time, memory, open files, child processes,
//!   file size) via `libc::setrlimit` in a pre-exec hook
//! - **background QoS / I/O throttling** by wrapping the command with
//!   `taskpolicy -b -c background -d throttle`
//!
//! These controls protect interactive workloads (e.g. Parsec remote
//! desktop streaming) from being starved by heavy agent-spawned commands.

use std::collections::HashMap;
use std::process::{Command, Stdio};
use crate::domain::entities::Process;
use crate::domain::value_objects::ExitStatus;
use crate::ports::driven::ProcessExecutorPort;

/// Native process executor using std::process::Command
pub struct NativeProcessExecutor {
    /// Currently running child processes
    processes: HashMap<u32, std::process::Child>,
}

impl NativeProcessExecutor {
    pub fn new() -> Self {
        Self {
            processes: HashMap::new(),
        }
    }

    /// Build a `Command` from a `Process` entity, applying priority,
    /// resource limits, and macOS QoS policies where configured.
    fn build_command(process: &Process) -> Command {
        // When background_qos or throttle_io are requested we wrap the
        // user command with `taskpolicy` so the *entire* process tree
        // inherits the scheduling policy.
        let use_taskpolicy = process.background_qos || process.throttle_io;

        let mut cmd = if use_taskpolicy {
            let mut c = Command::new("taskpolicy");
            if process.background_qos {
                c.arg("-b").arg("-c").arg("background");
            }
            if process.throttle_io {
                c.arg("-d").arg("throttle");
            }
            // Append the real command + args after the taskpolicy flags.
            c.arg(&process.command);
            for arg in &process.args {
                c.arg(arg);
            }
            c
        } else {
            let mut c = Command::new(&process.command);
            for arg in &process.args {
                c.arg(arg);
            }
            c
        };

        // Working directory
        if let Some(ref cwd) = process.cwd {
            cmd.current_dir(cwd);
        }

        // Environment variables
        for (key, value) in &process.env {
            cmd.env(key, value);
        }

        // I/O redirection
        match process.stdin {
            Some(_) => { cmd.stdin(Stdio::piped()); }
            None => { cmd.stdin(Stdio::null()); }
        }
        cmd.stdout(Stdio::piped());
        cmd.stderr(Stdio::piped());

        // ------------------------------------------------------------- //
        // Pre-exec: apply nice + setrlimit *inside* the child, before
        // exec replaces the process image.  This is Unix-only.
        // ------------------------------------------------------------- //
        #[cfg(unix)]
        {
            use std::os::unix::process::CommandExt;

            let nice_val = process.nice;
            let limits = process.limits.clone();

            // SAFETY: pre_exec runs between fork() and exec().  We only
            // call async-signal-safe libc functions (setpriority,
            // setrlimit) so this is safe.
            unsafe {
                cmd.pre_exec(move || {
                    // -- nice priority --
                    if let Some(n) = nice_val {
                        let ret = libc::setpriority(libc::PRIO_PROCESS, 0, n);
                        if ret != 0 {
                            let e = std::io::Error::last_os_error();
                            eprintln!("[thegent-subprocess] setpriority({n}) failed: {e}");
                            // Non-fatal: continue even if we cannot lower priority.
                        }
                    }

                    // -- resource limits --
                    if let Some(ref lim) = limits {
                        // Helper: set a single rlimit.
                        fn set_rlimit(resource: libc::c_int, value: u64) {
                            let rlim = libc::rlimit {
                                rlim_cur: value,
                                rlim_max: value,
                            };
                            let ret = unsafe { libc::setrlimit(resource, &rlim) };
                            if ret != 0 {
                                let e = std::io::Error::last_os_error();
                                eprintln!(
                                    "[thegent-subprocess] setrlimit({resource}) failed: {e}"
                                );
                            }
                        }

                        if let Some(cpu) = lim.max_cpu_seconds {
                            set_rlimit(libc::RLIMIT_CPU, cpu);
                        }
                        if let Some(mem) = lim.max_memory_bytes {
                            // RLIMIT_AS caps virtual address space — the
                            // closest portable approximation of a memory
                            // limit on macOS / Linux.
                            set_rlimit(libc::RLIMIT_AS, mem);
                        }
                        if let Some(nproc) = lim.max_processes {
                            set_rlimit(libc::RLIMIT_NPROC, nproc as u64);
                        }
                        if let Some(fsize) = lim.max_file_size {
                            set_rlimit(libc::RLIMIT_FSIZE, fsize);
                        }
                        if let Some(nofile) = lim.max_open_files {
                            set_rlimit(libc::RLIMIT_NOFILE, nofile as u64);
                        }
                    }

                    Ok(())
                });
            }
        }

        cmd
    }
}

impl Default for NativeProcessExecutor {
    fn default() -> Self {
        Self::new()
    }
}

impl ProcessExecutorPort for NativeProcessExecutor {
    fn execute(&mut self, process: &Process) -> Result<u32, String> {
        let mut cmd = Self::build_command(process);

        let child = cmd.spawn()
            .map_err(|e| format!("Failed to spawn process: {}", e))?;

        let pid = child.id();
        self.processes.insert(pid, child);

        Ok(pid)
    }

    fn execute_with_output(&mut self, process: &Process) -> Result<ExitStatus, String> {
        let mut cmd = Self::build_command(process);

        // For execute_with_output we need to collect output, so we
        // re-open stdout/stderr as piped (build_command already does
        // this) and call `output()`.  However `output()` starts a
        // *new* child, so we must re-apply stdio settings.
        cmd.stdout(Stdio::piped());
        cmd.stderr(Stdio::piped());

        let output = cmd.output()
            .map_err(|e| format!("Failed to execute: {}", e))?;

        let exit_code = output.status.code().unwrap_or(-1);
        Ok(ExitStatus { code: exit_code })
    }

    fn wait(&mut self, pid: u32) -> Result<ExitStatus, String> {
        if let Some(mut child) = self.processes.remove(&pid) {
            let status = child.wait()
                .map_err(|e| format!("Failed to wait for process: {}", e))?;
            let exit_code = status.code().unwrap_or(-1);
            return Ok(ExitStatus { code: exit_code });
        }
        Err(format!("Process {} not found", pid))
    }

    fn kill(&mut self, pid: u32) -> Result<(), String> {
        if let Some(mut child) = self.processes.remove(&pid) {
            child.kill()
                .map_err(|e| format!("Failed to kill process: {}", e))?;
            return Ok(());
        }
        Err(format!("Process {} not found", pid))
    }

    fn list_running(&self) -> Result<Vec<u32>, String> {
        Ok(self.processes.keys().copied().collect())
    }
}
