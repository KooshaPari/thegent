use serde::Deserialize;
use std::collections::HashMap;
use std::env;
use std::fs;
use std::io::Read;
use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

// ---------------------------------------------------------------------------
// Input schema
// ---------------------------------------------------------------------------

#[derive(Deserialize)]
struct HookInput {
    tool_name: Option<String>,
    tool_input: Option<serde_json::Value>,
    session_id: Option<String>,
    project_dir: Option<String>,
    cwd: Option<String>,
}

// ---------------------------------------------------------------------------
// Mode enum — all Claude Code hook event types
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, PartialEq)]
enum Mode {
    Pretool,       // PreToolUse: sequential, fail-fast (blocking)
    Posttool,      // PostToolUse: parallel, advisory
    Stop,          // Stop: parallel with timeout, propagate exit code
    SessionStart,  // SessionStart: sequential, advisory
    PromptSubmit,  // UserPromptSubmit: sequential, blocking (fail-fast)
    SubagentStart, // SubagentStart: single script, advisory
    SubagentStop,  // SubagentStop: single script, advisory
    PreCompact,    // PreCompact: sequential, advisory
    SessionEnd,    // SessionEnd: single script, advisory
    TaskCompleted, // TaskCompleted: single script, advisory
}

// ---------------------------------------------------------------------------
// Temp file RAII guard
// ---------------------------------------------------------------------------

struct TempFile {
    path: PathBuf,
}

impl TempFile {
    fn new(content: &str) -> Self {
        let path = PathBuf::from(format!("/tmp/hook-dispatch-{}.json", std::process::id()));
        fs::write(&path, content).expect("failed to write temp file");
        TempFile { path }
    }
}

impl Drop for TempFile {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.path);
    }
}

// ---------------------------------------------------------------------------
// Tool lookup helper (native PATH scan, no subprocess)
// ---------------------------------------------------------------------------

fn find_in_path(name: &str) -> Option<String> {
    let path_var = env::var("PATH").unwrap_or_default();
    for dir in path_var.split(':') {
        let candidate = Path::new(dir).join(name);
        if candidate.is_file() {
            return Some(candidate.to_string_lossy().into_owned());
        }
    }
    None
}

fn first_available(names: &[&str]) -> String {
    for name in names {
        if let Some(path) = find_in_path(name) {
            return path;
        }
    }
    String::new()
}

// ---------------------------------------------------------------------------
// Resolve hooks directory
// ---------------------------------------------------------------------------

fn resolve_hooks_dir() -> PathBuf {
    // 1. HOOKS_DIR env var
    if let Ok(dir) = env::var("HOOKS_DIR") {
        return PathBuf::from(dir);
    }
    // 2. Derive from binary location: go up to hooks/
    //    binary could be at hooks/hook-dispatcher/target/release/hook-dispatcher
    //    or at ~/.claude/bin/hook-dispatcher (symlinked or copied)
    if let Ok(exe) = env::current_exe() {
        // Walk ancestors looking for a directory that contains *.sh hook files
        let mut dir = exe.parent().map(|p| p.to_path_buf());
        for _ in 0..5 {
            if let Some(ref d) = dir {
                // Check if this directory looks like the hooks dir
                if d.join("pretool-dispatcher.sh").exists()
                    || d.join("doc-location-guard.sh").exists()
                {
                    return d.clone();
                }
                dir = d.parent().map(|p| p.to_path_buf());
            } else {
                break;
            }
        }
    }
    // 3. Fallback: ~/.claude/hooks/
    let home = env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
    PathBuf::from(format!("{home}/.claude/hooks"))
}

// ---------------------------------------------------------------------------
// Build environment map
// ---------------------------------------------------------------------------

fn build_env(
    input: &HookInput,
    raw_json: &str,
    mode: Mode,
    hooks_dir: &Path,
) -> HashMap<String, String> {
    let mut env_map: HashMap<String, String> = HashMap::new();

    let tool_name = input.tool_name.as_deref().unwrap_or("");
    let resolved_dir = input
        .cwd
        .clone()
        .or_else(|| input.project_dir.clone())
        .or_else(|| env::current_dir().ok().map(|p| p.to_string_lossy().into_owned()))
        .unwrap_or_default();
    let project_dir = resolved_dir.as_str();
    let session_id = input.session_id.as_deref().unwrap_or("");

    let tool_input = input.tool_input.as_ref();
    let get_str = |key: &str| -> String {
        tool_input
            .and_then(|v| v.get(key))
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    };

    // From JSON
    env_map.insert("TOOL_NAME".into(), tool_name.into());
    env_map.insert("FILE_PATH".into(), get_str("file_path"));
    env_map.insert("PROJECT_DIR".into(), project_dir.into());
    env_map.insert("SESSION_ID".into(), session_id.into());
    env_map.insert("CWD".into(), project_dir.into());
    env_map.insert("INPUT".into(), raw_json.into());
    env_map.insert("TOOL_CONTENT".into(), get_str("content"));
    env_map.insert("TOOL_NEW_STRING".into(), get_str("new_string"));
    env_map.insert("TOOL_OLD_STRING".into(), get_str("old_string"));

    // Computed
    env_map.insert("_HOOK_DISPATCHED".into(), "1".into());
    env_map.insert(
        "VERIFY_DIR".into(),
        format!("{project_dir}/.claude/verification"),
    );
    env_map.insert(
        "QA_STATE".into(),
        format!("{project_dir}/.claude/verification/qa-state.json"),
    );
    env_map.insert(
        "CHANGE_LOG".into(),
        format!("{project_dir}/.claude/session-changes.log"),
    );

    // QUALITY_CONFIG: project-local, then global, then empty
    let project_quality = format!("{project_dir}/.claude/quality.json");
    let home = env::var("HOME").unwrap_or_else(|_| "/tmp".into());
    let global_quality = format!("{home}/.claude/quality.json");
    let quality_config = if Path::new(&project_quality).exists() {
        project_quality
    } else if Path::new(&global_quality).exists() {
        global_quality
    } else {
        String::new()
    };
    env_map.insert("QUALITY_CONFIG".into(), quality_config);

    // Tool paths (available for ALL modes)
    env_map.insert("JQ_CMD".into(), first_available(&["jaq", "jq"]));
    env_map.insert("HUNIQ_CMD".into(), first_available(&["huniq"]));
    env_map.insert(
        "TIMEOUT_CMD".into(),
        first_available(&["gtimeout", "timeout"]),
    );
    env_map.insert("RG_CMD".into(), first_available(&["rg"]));

    // Signal to hooks that tool detection is already done
    env_map.insert("_TOOL_CACHE_LOADED".into(), "1".into());

    // Hooks dir for child scripts
    env_map.insert(
        "HOOKS_DIR".into(),
        hooks_dir.to_string_lossy().into_owned(),
    );

    // Stop-mode extras: pre-compute git state
    if mode == Mode::Stop && !project_dir.is_empty() {
        env_map.insert("STOP_ACTIVE".into(), "1".into());

        let head_sha = Command::new("git")
            .args(["rev-parse", "HEAD"])
            .current_dir(project_dir)
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .output()
            .ok()
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
            .unwrap_or_default();
        env_map.insert("HEAD_SHA".into(), head_sha);

        let changed = Command::new("git")
            .args(["diff", "--name-only", "HEAD"])
            .current_dir(project_dir)
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .output()
            .ok()
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
            .unwrap_or_default();
        env_map.insert("CHANGED_FILES".into(), changed);
    }

    // Mode identifier for hooks that need to know
    let mode_str = match mode {
        Mode::Pretool => "pretool",
        Mode::Posttool => "posttool",
        Mode::Stop => "stop",
        Mode::SessionStart => "sessionstart",
        Mode::PromptSubmit => "promptsubmit",
        Mode::SubagentStart => "subagentstart",
        Mode::SubagentStop => "subagentstop",
        Mode::PreCompact => "precompact",
        Mode::SessionEnd => "sessionend",
        Mode::TaskCompleted => "taskcompleted",
    };
    env_map.insert("HOOK_MODE".into(), mode_str.into());

    env_map
}

// ---------------------------------------------------------------------------
// Hook execution result
// ---------------------------------------------------------------------------

#[derive(Debug)]
struct HookResult {
    name: String,
    rc: i32,
    stdout: String,
    stderr: String,
}

// ---------------------------------------------------------------------------
// Run a single hook
// ---------------------------------------------------------------------------

fn run_hook(
    hooks_dir: &Path,
    hook_name: &str,
    extra_args: &[&str],
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    timeout: Option<Duration>,
) -> HookResult {
    let script = hooks_dir.join(hook_name);
    if !script.exists() {
        return HookResult {
            name: hook_name.into(),
            rc: 0,
            stdout: String::new(),
            stderr: String::new(),
        };
    }

    let stdin_file = match fs::File::open(temp_path) {
        Ok(f) => f,
        Err(e) => {
            return HookResult {
                name: hook_name.into(),
                rc: 1,
                stdout: String::new(),
                stderr: format!("failed to open temp file: {e}"),
            };
        }
    };

    let mut cmd = Command::new("bash");
    cmd.arg(&script);

    // Append extra arguments (e.g., "start" or "stop" for subagent gate)
    for arg in extra_args {
        cmd.arg(arg);
    }

    cmd.stdin(Stdio::from(stdin_file))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // Inherit parent environment (avoids bash rehashing PATH from scratch).
    // Overlay our hook env vars on top.
    for (k, v) in env_map {
        cmd.env(k, v);
    }

    // Set working directory to project dir if available
    if let Some(project_dir) = env_map.get("PROJECT_DIR") {
        if !project_dir.is_empty() && Path::new(project_dir).is_dir() {
            cmd.current_dir(project_dir);
        }
    }

    let mut child = match cmd.spawn() {
        Ok(c) => c,
        Err(e) => {
            return HookResult {
                name: hook_name.into(),
                rc: 1,
                stdout: String::new(),
                stderr: format!("failed to spawn hook: {e}"),
            };
        }
    };

    match timeout {
        Some(dur) => {
            let start = Instant::now();
            loop {
                match child.try_wait() {
                    Ok(Some(status)) => {
                        let mut stdout_buf = Vec::new();
                        let mut stderr_buf = Vec::new();
                        if let Some(mut so) = child.stdout.take() {
                            let _ = so.read_to_end(&mut stdout_buf);
                        }
                        if let Some(mut se) = child.stderr.take() {
                            let _ = se.read_to_end(&mut stderr_buf);
                        }
                        return HookResult {
                            name: hook_name.into(),
                            rc: status.code().unwrap_or(1),
                            stdout: String::from_utf8_lossy(&stdout_buf).into_owned(),
                            stderr: String::from_utf8_lossy(&stderr_buf).into_owned(),
                        };
                    }
                    Ok(None) => {
                        if start.elapsed() >= dur {
                            let _ = child.kill();
                            let _ = child.wait();
                            return HookResult {
                                name: hook_name.into(),
                                rc: 124,
                                stdout: String::new(),
                                stderr: format!(
                                    "{hook_name}: timed out after {}s",
                                    dur.as_secs()
                                ),
                            };
                        }
                        thread::sleep(Duration::from_millis(50));
                    }
                    Err(e) => {
                        return HookResult {
                            name: hook_name.into(),
                            rc: 1,
                            stdout: String::new(),
                            stderr: format!("wait error: {e}"),
                        };
                    }
                }
            }
        }
        None => {
            let output = child.wait_with_output().unwrap_or_else(|e| {
                panic!("failed to wait on hook {hook_name}: {e}");
            });
            HookResult {
                name: hook_name.into(),
                rc: output.status.code().unwrap_or(1),
                stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
                stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Run hooks sequentially, fail-fast (pretool, promptsubmit)
// Returns the first non-zero exit code, or 0 if all succeed.
// ---------------------------------------------------------------------------

fn run_sequential_blocking(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
) -> i32 {
    for (hook, args) in hooks {
        let result = run_hook(hooks_dir, hook, args, env_map, temp_path, None);
        if !result.stdout.is_empty() {
            eprint!("{}", result.stdout);
        }
        if result.rc != 0 {
            if !result.stderr.is_empty() {
                eprint!("{}", result.stderr);
            }
            return result.rc;
        }
    }
    0
}

// ---------------------------------------------------------------------------
// Run hooks in a SINGLE bash process via source (saves N-1 bash spawns).
// Generates a wrapper script that sources each hook sequentially.
// Fail-fast: stops on first non-zero exit.
// ---------------------------------------------------------------------------

fn run_combined_blocking(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
) -> i32 {
    // Filter to hooks that actually exist
    let existing: Vec<&str> = hooks
        .iter()
        .filter(|(h, _)| hooks_dir.join(h).exists())
        .map(|(h, _)| *h)
        .collect();

    if existing.is_empty() {
        return 0;
    }

    // If only one hook, just run it directly (no wrapper overhead)
    if existing.len() == 1 {
        let result = run_hook(hooks_dir, existing[0], &[], env_map, temp_path, None);
        if !result.stdout.is_empty() {
            eprint!("{}", result.stdout);
        }
        if result.rc != 0 && !result.stderr.is_empty() {
            eprint!("{}", result.stderr);
        }
        return result.rc;
    }

    // Generate combined wrapper script
    let hdir = hooks_dir.to_string_lossy();
    let mut script = String::from("#!/usr/bin/env bash\nset -uo pipefail\n");
    for h in &existing {
        // Source each hook in a subshell so `exit` doesn't kill the wrapper
        script.push_str(&format!(
            "( source \"{hdir}/{h}\" ) < \"{}\" || exit $?\n",
            temp_path.to_string_lossy()
        ));
    }
    script.push_str("exit 0\n");

    // Write wrapper to temp file
    let wrapper_path = PathBuf::from(format!(
        "/tmp/hook-combined-{}.sh",
        std::process::id()
    ));
    if fs::write(&wrapper_path, &script).is_err() {
        // Fallback to individual execution
        return run_sequential_blocking(hooks, hooks_dir, env_map, temp_path);
    }

    let stdin_file = match fs::File::open(temp_path) {
        Ok(f) => f,
        Err(_) => {
            let _ = fs::remove_file(&wrapper_path);
            return 1;
        }
    };

    let mut cmd = Command::new("bash");
    cmd.arg(&wrapper_path)
        .stdin(Stdio::from(stdin_file))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // Inherit parent environment + overlay hook vars
    for (k, v) in env_map {
        cmd.env(k, v);
    }

    if let Some(project_dir) = env_map.get("PROJECT_DIR") {
        if !project_dir.is_empty() && Path::new(project_dir).is_dir() {
            cmd.current_dir(project_dir);
        }
    }

    let result = match cmd.output() {
        Ok(output) => {
            if !output.stdout.is_empty() {
                eprint!("{}", String::from_utf8_lossy(&output.stdout));
            }
            if output.status.code().unwrap_or(1) != 0 && !output.stderr.is_empty() {
                eprint!("{}", String::from_utf8_lossy(&output.stderr));
            }
            output.status.code().unwrap_or(1)
        }
        Err(_) => {
            let _ = fs::remove_file(&wrapper_path);
            return run_sequential_blocking(hooks, hooks_dir, env_map, temp_path);
        }
    };

    let _ = fs::remove_file(&wrapper_path);
    result
}

// ---------------------------------------------------------------------------
// Same as run_combined_blocking but advisory (always returns 0).
// ---------------------------------------------------------------------------

fn run_combined_advisory(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    label: &str,
) -> i32 {
    let existing: Vec<&str> = hooks
        .iter()
        .filter(|(h, _)| hooks_dir.join(h).exists())
        .map(|(h, _)| *h)
        .collect();

    if existing.is_empty() {
        return 0;
    }

    if existing.len() == 1 {
        let result = run_hook(hooks_dir, existing[0], &[], env_map, temp_path, None);
        if !result.stdout.is_empty() {
            eprint!("{}", result.stdout);
        }
        if result.rc != 0 {
            if !result.stderr.is_empty() {
                eprint!("{}", result.stderr);
            }
            eprintln!("{label} DISPATCHER: advisory failure: {}(rc={})", result.name, result.rc);
        }
        return 0;
    }

    let hdir = hooks_dir.to_string_lossy();
    let mut script = String::from("#!/usr/bin/env bash\nset -uo pipefail\n_failures=\"\"\n");
    for h in &existing {
        script.push_str(&format!(
            "( source \"{hdir}/{h}\" ) < \"{}\" || _failures=\"$_failures {h}\"\n",
            temp_path.to_string_lossy()
        ));
    }
    script.push_str(&format!(
        "[[ -n \"$_failures\" ]] && echo \"{label} DISPATCHER: advisory failures:$_failures\" >&2\nexit 0\n"
    ));

    let wrapper_path = PathBuf::from(format!("/tmp/hook-combined-{}.sh", std::process::id()));
    if fs::write(&wrapper_path, &script).is_err() {
        return run_sequential_advisory(hooks, hooks_dir, env_map, temp_path, label);
    }

    let stdin_file = match fs::File::open(temp_path) {
        Ok(f) => f,
        Err(_) => {
            let _ = fs::remove_file(&wrapper_path);
            return 0;
        }
    };

    let mut cmd = Command::new("bash");
    cmd.arg(&wrapper_path)
        .stdin(Stdio::from(stdin_file))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    for (k, v) in env_map {
        cmd.env(k, v);
    }

    if let Some(project_dir) = env_map.get("PROJECT_DIR") {
        if !project_dir.is_empty() && Path::new(project_dir).is_dir() {
            cmd.current_dir(project_dir);
        }
    }

    if let Ok(output) = cmd.output() {
        if !output.stdout.is_empty() {
            eprint!("{}", String::from_utf8_lossy(&output.stdout));
        }
        if !output.stderr.is_empty() {
            eprint!("{}", String::from_utf8_lossy(&output.stderr));
        }
    }

    let _ = fs::remove_file(&wrapper_path);
    0
}

// ---------------------------------------------------------------------------
// Run hooks sequentially, advisory (sessionstart, precompact)
// Runs all hooks regardless of exit code. Always returns 0.
// ---------------------------------------------------------------------------

fn run_sequential_advisory(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    label: &str,
) -> i32 {
    let mut failures = Vec::new();
    for (hook, args) in hooks {
        let result = run_hook(hooks_dir, hook, args, env_map, temp_path, None);
        if !result.stdout.is_empty() {
            eprint!("{}", result.stdout);
        }
        if result.rc != 0 {
            failures.push(format!("{}(rc={})", result.name, result.rc));
            if !result.stderr.is_empty() {
                eprint!("{}", result.stderr);
            }
        }
    }
    if !failures.is_empty() {
        eprintln!(
            "{} DISPATCHER: advisory failures: {}",
            label,
            failures.join("; ")
        );
    }
    0
}

// ---------------------------------------------------------------------------
// Run hooks in parallel (posttool / stop)
// ---------------------------------------------------------------------------

fn run_parallel(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    timeout: Option<Duration>,
) -> Vec<HookResult> {
    let env_arc = Arc::new(env_map.clone());
    let hooks_dir_arc = Arc::new(hooks_dir.to_path_buf());
    let temp_path_arc = Arc::new(temp_path.to_path_buf());
    let results: Arc<Mutex<Vec<HookResult>>> = Arc::new(Mutex::new(Vec::new()));

    let mut handles = Vec::new();

    for (hook, args) in hooks {
        let hook_name = hook.to_string();
        let args_owned: Vec<String> = args.iter().map(|a| a.to_string()).collect();
        let env_c = Arc::clone(&env_arc);
        let hdir = Arc::clone(&hooks_dir_arc);
        let tpath = Arc::clone(&temp_path_arc);
        let res = Arc::clone(&results);

        let handle = thread::spawn(move || {
            let args_refs: Vec<&str> = args_owned.iter().map(|s| s.as_str()).collect();
            let result = run_hook(&hdir, &hook_name, &args_refs, &env_c, &tpath, timeout);
            res.lock().unwrap().push(result);
        });
        handles.push(handle);
    }

    for h in handles {
        let _ = h.join();
    }

    Arc::try_unwrap(results).unwrap().into_inner().unwrap()
}

// ---------------------------------------------------------------------------
// Run a single hook, advisory (subagentstart, subagentstop, sessionend,
// taskcompleted). Always returns 0.
// ---------------------------------------------------------------------------

fn run_single_advisory(
    hook: &str,
    args: &[&str],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    label: &str,
) -> i32 {
    let result = run_hook(hooks_dir, hook, args, env_map, temp_path, None);
    if !result.stdout.is_empty() {
        eprint!("{}", result.stdout);
    }
    if result.rc != 0 {
        if !result.stderr.is_empty() {
            eprint!("{}", result.stderr);
        }
        eprintln!(
            "{} DISPATCHER: advisory failure: {}(rc={})",
            label, result.name, result.rc
        );
    }
    0
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!(
            "usage: hook-dispatcher <pretool|posttool|stop|sessionstart|promptsubmit|\
             subagentstart|subagentstop|precompact|sessionend|taskcompleted>"
        );
        return ExitCode::from(1);
    }

    let mode = match args[1].as_str() {
        "pretool" => Mode::Pretool,
        "posttool" => Mode::Posttool,
        "stop" => Mode::Stop,
        "sessionstart" => Mode::SessionStart,
        "promptsubmit" => Mode::PromptSubmit,
        "subagentstart" => Mode::SubagentStart,
        "subagentstop" => Mode::SubagentStop,
        "precompact" => Mode::PreCompact,
        "sessionend" => Mode::SessionEnd,
        "taskcompleted" => Mode::TaskCompleted,
        other => {
            eprintln!("unknown mode: {other}");
            return ExitCode::from(1);
        }
    };

    // Read stdin
    let mut raw_json = String::new();
    std::io::stdin()
        .read_to_string(&mut raw_json)
        .expect("failed to read stdin");

    // Parse JSON
    let input: HookInput = match serde_json::from_str(&raw_json) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("JSON parse error: {e}");
            return ExitCode::from(1);
        }
    };

    let hooks_dir = resolve_hooks_dir();
    let env_map = build_env(&input, &raw_json, mode, &hooks_dir);
    let temp_file = TempFile::new(&raw_json);

    match mode {
        // -----------------------------------------------------------------
        // PreToolUse: sequential, fail-fast (blocking)
        // -----------------------------------------------------------------
        Mode::Pretool => {
            let tool_name = input.tool_name.as_deref().unwrap_or("");
            let hooks: Vec<(&str, &[&str])> = match tool_name {
                "Write" => vec![
                    ("doc-location-guard.sh", &[]),
                    ("pre-write-validator.sh", &[]),
                    ("suppression-blocker.sh", &[]),
                ],
                "Edit" => vec![
                    ("pre-write-validator.sh", &[]),
                    ("suppression-blocker.sh", &[]),
                ],
                _ => return ExitCode::from(0),
            };
            let rc = run_combined_blocking(&hooks, &hooks_dir, &env_map, &temp_file.path);
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // PostToolUse: parallel, advisory
        // -----------------------------------------------------------------
        Mode::Posttool => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("change-doc-tracker.sh", &[]),
                ("qa-evidence-recorder.sh", &[]),
                ("qa-policy-test.sh", &[]),
                ("post-edit-checker.sh", &[]),
                ("async-test-runner.sh", &[]),
                ("speculative-stop-prewarmer.sh", &[]),
            ];
            let results =
                run_parallel(&hooks, &hooks_dir, &env_map, &temp_file.path, None);

            let mut failures = Vec::new();
            for r in &results {
                if !r.stdout.is_empty() {
                    eprint!("{}", r.stdout);
                }
                if r.rc != 0 {
                    failures.push(format!("{}(rc={})", r.name, r.rc));
                    if !r.stderr.is_empty() {
                        eprint!("{}", r.stderr);
                    }
                }
            }
            if !failures.is_empty() {
                eprintln!(
                    "POSTTOOL DISPATCHER: advisory failures: {}",
                    failures.join("; ")
                );
            }
            ExitCode::from(0)
        }

        // -----------------------------------------------------------------
        // Stop: parallel with timeout, propagate exit code
        // -----------------------------------------------------------------
        Mode::Stop => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("governance-gates.sh", &[]),
                ("qa-supply-chain-verifier.sh", &[]),
                ("quality-gate.sh", &[]),
                ("complexity-ratchet.sh", &[]),
                ("security-pipeline.sh", &[]),
                ("spec-verifier.sh", &[]),
                ("test-maturity.sh", &[]),
                ("stop-reconcile.sh", &[]),
                ("task-completion-verifier.sh", &[]),
            ];
            let timeout = Duration::from_secs(30);
            let results = run_parallel(
                &hooks,
                &hooks_dir,
                &env_map,
                &temp_file.path,
                Some(timeout),
            );

            let mut max_rc: i32 = 0;
            let mut failures = Vec::new();
            for r in &results {
                if !r.stdout.is_empty() {
                    eprint!("{}", r.stdout);
                }
                if r.rc != 0 {
                    failures.push(format!("{}(rc={})", r.name, r.rc));
                    if !r.stderr.is_empty() {
                        eprint!("{}", r.stderr);
                    }
                }
                if r.rc > max_rc {
                    max_rc = r.rc;
                }
            }
            if !failures.is_empty() {
                eprintln!(
                    "STOP DISPATCHER: non-zero from: {}",
                    failures.join("; ")
                );
            }
            // Clamp to u8 range
            let exit_val = if max_rc > 255 { 255 } else { max_rc as u8 };
            ExitCode::from(exit_val)
        }

        // -----------------------------------------------------------------
        // SessionStart: sequential, advisory
        // -----------------------------------------------------------------
        Mode::SessionStart => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("spec-preflight.sh", &[]),
                ("qa-preflight.sh", &[]),
            ];
            let rc = run_combined_advisory(
                &hooks,
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "SESSIONSTART",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // UserPromptSubmit: sequential, blocking (fail-fast)
        // -----------------------------------------------------------------
        Mode::PromptSubmit => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("prompt-submit-guard.sh", &[]),
            ];
            let rc = run_combined_blocking(&hooks, &hooks_dir, &env_map, &temp_file.path);
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // SubagentStart: single script, advisory (with "start" argument)
        // -----------------------------------------------------------------
        Mode::SubagentStart => {
            let rc = run_single_advisory(
                "subagent-quality-gate.sh",
                &["start"],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "SUBAGENTSTART",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // SubagentStop: single script, advisory (with "stop" argument)
        // -----------------------------------------------------------------
        Mode::SubagentStop => {
            let rc = run_single_advisory(
                "subagent-quality-gate.sh",
                &["stop"],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "SUBAGENTSTOP",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // PreCompact: sequential, advisory
        // -----------------------------------------------------------------
        Mode::PreCompact => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("pre-compact-snapshot.sh", &[]),
                ("auto-checkpoint.sh", &[]),
            ];
            let rc = run_combined_advisory(
                &hooks,
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "PRECOMPACT",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // SessionEnd: single script, advisory
        // -----------------------------------------------------------------
        Mode::SessionEnd => {
            let rc = run_single_advisory(
                "session-cleanup.sh",
                &[],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "SESSIONEND",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // TaskCompleted: single script, advisory
        // -----------------------------------------------------------------
        Mode::TaskCompleted => {
            let rc = run_single_advisory(
                "task-completion-verifier.sh",
                &[],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "TASKCOMPLETED",
            );
            ExitCode::from(rc as u8)
        }
    }
}
