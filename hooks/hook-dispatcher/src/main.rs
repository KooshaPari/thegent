use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use std::fs;
use std::io::{BufRead, BufReader, IsTerminal, Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};
use regex::Regex;
use std::sync::OnceLock;

fn get_secret_regexes() -> &'static Vec<Regex> {
    static SECRET_REGEXES: OnceLock<Vec<Regex>> = OnceLock::new();
    SECRET_REGEXES.get_or_init(|| {
        vec![
            Regex::new(r"sk-[a-zA-Z0-9]{48}").unwrap(),      // OpenAI
            Regex::new(r"AIza[0-9A-Za-z-_]{35}").unwrap(),   // Google Cloud
            Regex::new(r"xox[baprs]-[0-9]{12}").unwrap(),    // Slack
            Regex::new(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----").unwrap(), // Private keys
            Regex::new(r"sq0atp-[0-9A-Za-z-_]{22}").unwrap(), // Square
            Regex::new(r"access_key_id.:\s*.AKIA").unwrap(),  // AWS
            Regex::new(r"secret_access_key.:").unwrap(),     // AWS
            Regex::new(r"ghp_[a-zA-Z0-9]{36}").unwrap(),     // GitHub PAT
        ]
    })
}

// ---------------------------------------------------------------------------
// Worker Pool (MTSP-06)
// ---------------------------------------------------------------------------

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

struct WorkerPool {
    workers: Vec<Worker>,
    sender: Option<std::sync::mpsc::Sender<Box<dyn FnOnce() + Send>>>,
}

impl WorkerPool {
    fn new(size: usize) -> Self {
        let (sender, receiver) = std::sync::mpsc::channel::<Box<dyn FnOnce() + Send>>();
        let receiver = Arc::new(Mutex::new(receiver));
        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            let rx = Arc::clone(&receiver);
            let thread = thread::spawn(move || loop {
                let job = rx.lock().unwrap().recv();
                match job {
                    Ok(f) => f(),
                    Err(_) => break,
                }
            });
            workers.push(Worker { id, thread: Some(thread) });
        }

        WorkerPool { workers, sender: Some(sender) }
    }

    fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        if let Some(ref sender) = self.sender {
            sender.send(Box::new(f)).expect("failed to send job to worker");
        }
    }
}

// ---------------------------------------------------------------------------
// Input schema
// ---------------------------------------------------------------------------

#[derive(Deserialize, Serialize)]
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
    TeammateIdle,  // TeammateIdle: single script, advisory (exit 2 sentinel)
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
// Native hook implementations
// ---------------------------------------------------------------------------

fn run_doc_location_guard(_env_map: &HashMap<String, String>) -> i32 {
    // ... code ...
    0
}

fn run_session_cleanup(env_map: &HashMap<String, String>) -> i32 {
    let project_dir = env_map.get("PROJECT_DIR").map(|s| s.as_str()).unwrap_or(".");
    
    let change_log = format!("{}/.claude/session-changes.log", project_dir);
    let qa_state = format!("{}/.claude/qa-state.json", project_dir);

    let _ = fs::remove_file(change_log);
    let _ = fs::remove_file(qa_state);

    0
}

fn run_prompt_submit_guard(_env_map: &HashMap<String, String>, input_json: &serde_json::Value) -> i32 {
    let prompt_text = input_json.get("tool_input")
        .and_then(|ti| ti.get("prompt").or_else(|| ti.get("content")))
        .or_else(|| input_json.get("content"))
        .and_then(|v| v.as_str())
        .unwrap_or("");

    if prompt_text.is_empty() {
        return 0;
    }

    let prompt_lower = prompt_text.to_lowercase();
    let mut antipatterns = Vec::new();

    // Test-skipping
    let test_patterns = ["skip tests", "skip the tests", "don't write tests", "no tests", "dont write tests", "without tests"];
    for p in &test_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("test-skipping: \"{p}\""));
            break;
        }
    }

    // Lint-skipping
    let lint_patterns = ["disable lint", "ignore lint", "skip lint", "no linting"];
    for p in &lint_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("lint-skipping: \"{p}\""));
            break;
        }
    }

    // Quality-skipping
    let quality_patterns = ["just make it work", "just get it working", "just get it done", "make it work somehow"];
    for p in &quality_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("quality-shortcut: \"{p}\""));
            break;
        }
    }

    // Error-suppression
    let error_patterns = ["ignore the errors", "ignore errors", "suppress the", "suppress errors", "hide the errors"];
    for p in &error_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("error-suppression: \"{p}\""));
            break;
        }
    }

    // Dangerous git
    let git_patterns = ["--no-verify", "--force", "force push", "force-push", "--force-with-lease"];
    for p in &git_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("dangerous-git: \"{p}\""));
            break;
        }
    }

    if !antipatterns.is_empty() {
        eprintln!("QA Governance Reminder: Quality enforcement is active.");
        eprintln!("  Detected patterns:");
        for ap in &antipatterns {
            eprintln!("    - {ap}");
        }
        eprintln!("  Consider:\n    - Tests are required for all new code (TDD mandate)\n    - Suppressions require inline justification\n    - All linters must pass");
    }

    // Workflow triggers (Idea/Task)
    let idea_patterns = ["idea", "research", "explore", "figure out", "add feature", "build", "implement", "design", "create", "task", "feature", "investigate"];
    for p in &idea_patterns {
        if prompt_lower.contains(p) {
            eprintln!("\n--- Agent workflow (idea/task detected) ---");
            eprintln!("1. Dump research to docs/research/ (or docs/guides/ as appropriate)");
            eprintln!("2. Create or update specs in docs/docset/ (formal specification docset)");
            eprintln!("3. Add work items to unified work stream (docs/reference/, contracts/, or project tracker)");
            eprintln!("4. This enables: spam ideas here → open new chat → ask 'find the next thing to do'");
            break;
        }
    }

    // Special flags: $defer, $pending, $block, $idea
    if prompt_text.contains("$defer") || prompt_text.contains("$pending") || prompt_text.contains("$block") || prompt_text.contains("$idea") {
        return 99; // Sentinel value to trigger fallback
    }

    0
}

fn run_governance_scan(project_dir: &str) -> i32 {
    // MTSP-08: Native 8-dimension scan (Rust implementation)
    let project_path = Path::new(project_dir);
    let mut violation_count = 0;
    
    println!("--- MTSP-08: Rust Governance Scan ---");

    // 1. Doc Disorganization
    let required_dirs = ["docs/guides", "docs/reference", "docs/reports"];
    let mut missing = Vec::new();
    for d in &required_dirs {
        if !project_path.join(d).is_dir() {
            missing.push(*d);
        }
    }
    if !missing.is_empty() {
        eprintln!("GOVERNANCE [Dimension 1: Docs]: missing required doc subdirs: {:?}", missing);
        violation_count += 1;
    }

    // 2. Stale Specs (7 days)
    let specs_dir = project_path.join("specs");
    if specs_dir.is_dir() {
        let cutoff = std::time::SystemTime::now() - Duration::from_secs(7 * 86400);
        let mut stale_count = 0;
        if let Ok(entries) = fs::read_dir(specs_dir) {
            for entry in entries.flatten() {
                if let Ok(metadata) = entry.metadata() {
                    if let Ok(modified) = metadata.modified() {
                        if modified < cutoff {
                            stale_count += 1;
                        }
                    }
                }
            }
        }
        if stale_count > 0 {
            eprintln!("GOVERNANCE [Dimension 2: Specs]: found {stale_count} stale spec file(s)");
            violation_count += 1;
        }
    }

    // 3. Large Files (> 100KB)
    let mut large_files = Vec::new();
    scan_large_files(project_path, &mut large_files, 100 * 1024);
    if !large_files.is_empty() {
        eprintln!("GOVERNANCE [Dimension 3: Size]: found {} file(s) > 100KB", large_files.len());
        for f in large_files.iter().take(5) {
            eprintln!("  - {:?}", f);
        }
        violation_count += 1;
    }

    // 4. TODO Sprawl
    let todo_count = count_todos(project_path);
    if todo_count > 50 {
        eprintln!("GOVERNANCE [Dimension 4: TODOs]: high TODO count: {}", todo_count);
        violation_count += 1;
    }

    // 5. AI Slop Detection (Dimension 5)
    let slop_count = count_ai_slop(project_path);
    if slop_count > 0 {
        eprintln!("GOVERNANCE [Dimension 5: Slop]: detected {} instance(s) of AI slop", slop_count);
        violation_count += 1;
    }

    // 6. Secret Detection (Dimension 6)
    let secret_count = scan_secrets(project_path);
    if secret_count > 0 {
        eprintln!("GOVERNANCE [Dimension 6: Security]: detected {} potential secret(s)", secret_count);
        violation_count += 1;
    }

    // 7. Complexity (Dimension 7: Deep Nesting)
    let deep_files = scan_deep_nesting(project_path, 8);
    if !deep_files.is_empty() {
        eprintln!("GOVERNANCE [Dimension 7: Complexity]: found {} file(s) nested deeper than 8 levels", deep_files.len());
        violation_count += 1;
    }

    // 8. License/Provenance (Dimension 8)
    if !project_path.join("LICENSE").exists() && !project_path.join("COPYING").exists() && !project_path.join("LICENSE.md").exists() {
        eprintln!("GOVERNANCE [Dimension 8: Provenance]: missing LICENSE file");
        violation_count += 1;
    }

    if violation_count > 0 {
        eprintln!("GOVERNANCE: scan completed with {} dimension violation(s)", violation_count);
    } else {
        println!("GOVERNANCE: all dimensions green.");
    }

    0
}

fn count_ai_slop(dir: &Path) -> usize {
    let mut count = 0;
    let slop_patterns = ["As an AI", "I cannot", "I apologize", "I'm sorry, but", "As a language model"];
    
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if name == "node_modules" || name == ".git" || name == ".venv" || name == "target" || name == "__pycache__" {
                    continue;
                }
                count += count_ai_slop(&path);
            } else if path.is_file() {
                let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                if ext == "py" || ext == "js" || ext == "ts" || ext == "rs" || ext == "go" || ext == "md" {
                    if let Ok(content) = fs::read_to_string(&path) {
                        for p in &slop_patterns {
                            count += content.matches(p).count();
                        }
                    }
                }
            }
        }
    }
    count
}

fn scan_secrets(dir: &Path) -> usize {
    let mut count = 0;
    
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if name == "node_modules" || name == ".git" || name == ".venv" || name == "target" || name == "__pycache__" || name == "dist" {
                    continue;
                }
                count += scan_secrets(&path);
            } else if path.is_file() {
                let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                if ext == "env" || ext == "json" || ext == "py" || ext == "js" || ext == "ts" || ext == "yaml" || ext == "yml" || ext == "toml" || ext == "xml" {
                    if let Ok(content) = fs::read_to_string(&path) {
                        for regex in get_secret_regexes().iter() {
                            if regex.is_match(&content) {
                                count += 1;
                                break;
                            }
                        }
                    }
                }
            }
        }
    }
    count
}

fn scan_deep_nesting(dir: &Path, limit: usize) -> Vec<PathBuf> {
    let mut results = Vec::new();
    fn recurse(dir: &Path, depth: usize, limit: usize, results: &mut Vec<PathBuf>) {
        if depth > limit {
            results.push(dir.to_path_buf());
            return;
        }
        if let Ok(entries) = fs::read_dir(dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_dir() {
                    let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                    if name == "node_modules" || name == ".git" || name == ".venv" || name == "target" || name == "__pycache__" {
                        continue;
                    }
                    recurse(&path, depth + 1, limit, results);
                }
            }
        }
    }
    recurse(dir, 0, limit, &mut results);
    results
}

fn scan_large_files(dir: &Path, large_files: &mut Vec<PathBuf>, threshold: u64) {
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if name == "node_modules" || name == ".git" || name == ".venv" || name == "target" || name == "__pycache__" {
                    continue;
                }
                scan_large_files(&path, large_files, threshold);
            } else if path.is_file() {
                if let Ok(metadata) = entry.metadata() {
                    if metadata.len() > threshold {
                        large_files.push(path);
                    }
                }
            }
        }
    }
}

fn count_todos(dir: &Path) -> usize {
    let mut count = 0;
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if name == "node_modules" || name == ".git" || name == ".venv" || name == "target" || name == "__pycache__" {
                    continue;
                }
                count += count_todos(&path);
            } else if path.is_file() {
                let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                if ext == "py" || ext == "js" || ext == "ts" || ext == "rs" || ext == "go" || ext == "sh" {
                    if let Ok(content) = fs::read_to_string(&path) {
                        count += content.matches("TODO").count();
                        count += content.matches("FIXME").count();
                    }
                }
            }
        }
    }
    count
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
// Read skip hooks from .claude.qa-local.json
// ---------------------------------------------------------------------------

fn get_skip_hooks(project_dir: &str) -> Vec<String> {
    let qa_config_path = format!("{}/.claude/qa-local.json", project_dir);
    let path = Path::new(&qa_config_path);
    if !path.exists() {
        return Vec::new();
    }

    match fs::read_to_string(path) {
        Ok(content) => {
            match serde_json::from_str::<serde_json::Value>(&content) {
                Ok(json) => {
                    let mut skip_list = Vec::new();
                    if let Some(hooks) = json.get("hooks").and_then(|h| h.get("skip")) {
                        if let Some(arr) = hooks.as_array() {
                            for item in arr {
                                if let Some(s) = item.as_str() {
                                    skip_list.push(s.to_string());
                                }
                            }
                        }
                    }
                    skip_list
                }
                Err(_) => Vec::new(),
            }
        }
        Err(_) => Vec::new(),
    }
}

fn should_skip_hook(hook_name: &str, skip_list: &[String]) -> bool {
    // Hook name comes as "foo.sh", skip list has "foo" or "foo.sh"
    let hook_base = hook_name.trim_end_matches(".sh");
    skip_list.iter().any(|s| {
        let skip_base = s.trim_end_matches(".sh");
        skip_base == hook_base
    })
}

#[derive(Debug, Clone)]
struct StopSettings {
    idle_timeout_sec: u64,
    max_timeout_sec: u64,
    profile: String,
}

fn clamp_stop_idle(v: u64) -> u64 {
    v.clamp(5, 15)
}

fn clamp_stop_max(v: u64, idle: u64) -> u64 {
    v.max(idle).clamp(5, 15)
}

fn read_stop_settings(project_dir: &str) -> StopSettings {
    // Defaults: aggressively bounded for low-latency operator loops.
    let mut idle_timeout_sec: u64 = 5;
    let mut max_timeout_sec: u64 = 15;
    let mut profile = "fast".to_string();

    let qa_config_path = format!("{}/.claude/qa-local.json", project_dir);
    if let Ok(content) = fs::read_to_string(&qa_config_path) {
        if let Ok(json) = serde_json::from_str::<serde_json::Value>(&content) {
            if let Some(stop) = json.get("stop") {
                if let Some(v) = stop.get("idle_timeout_sec").and_then(|x| x.as_u64()) {
                    idle_timeout_sec = v;
                }
                if let Some(v) = stop.get("max_timeout_sec").and_then(|x| x.as_u64()) {
                    max_timeout_sec = v;
                }
                if let Some(v) = stop.get("profile").and_then(|x| x.as_str()) {
                    let p = v.trim().to_ascii_lowercase();
                    if p == "ultrafast" || p == "fast" || p == "standard" || p == "full" {
                        profile = p;
                    }
                }
            }
        }
    }

    // Env overrides (highest priority)
    if let Ok(v) = env::var("THGENT_STOP_IDLE_TIMEOUT_SEC") {
        if let Ok(n) = v.parse::<u64>() {
            idle_timeout_sec = n;
        }
    }
    if let Ok(v) = env::var("THGENT_STOP_MAX_TIMEOUT_SEC") {
        if let Ok(n) = v.parse::<u64>() {
            max_timeout_sec = n;
        }
    }
    if let Ok(v) = env::var("THGENT_STOP_PROFILE") {
        let p = v.trim().to_ascii_lowercase();
        if p == "ultrafast" || p == "fast" || p == "standard" || p == "full" {
            profile = p;
        }
    }

    idle_timeout_sec = clamp_stop_idle(idle_timeout_sec);
    max_timeout_sec = clamp_stop_max(max_timeout_sec, idle_timeout_sec);

    StopSettings {
        idle_timeout_sec,
        max_timeout_sec,
        profile,
    }
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
    env_map.insert("RG_TIMEOUT_SEC".into(), env::var("RG_TIMEOUT_SEC").unwrap_or_else(|_| "30".into()));
    env_map.insert("FD_CMD".into(), first_available(&["fd", "fdfind"]));
    env_map.insert("PGREP_CMD".into(), first_available(&["pgrep"]));
    env_map.insert("HASH_CMD".into(), first_available(&["b3sum", "sha256sum", "shasum"]));

    // Timestamps
    let now = std::time::SystemTime::now();
    let ts = now.duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
    env_map.insert("START_TIMESTAMP".into(), ts.to_string());

    // Signal to hooks that tool detection is already done
    env_map.insert("_TOOL_CACHE_LOADED".into(), "1".into());

    // Hooks dir for child scripts
    env_map.insert(
        "HOOKS_DIR".into(),
        hooks_dir.to_string_lossy().into_owned(),
    );

    // Stop-mode extras: pre-compute git changed files
    if mode == Mode::Stop && !project_dir.is_empty() {
        env_map.insert("STOP_ACTIVE".into(), "1".into());

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
        Mode::TeammateIdle => "teammateidle",
    };
    env_map.insert("HOOK_MODE".into(), mode_str.into());

    // Global Git State (MTSP-07)
    // Pre-compute HEAD_SHA for all modes to eliminate 100+ git spawns
    if !project_dir.is_empty() {
        let head_sha = Command::new("git")
            .args(["rev-parse", "HEAD"])
            .current_dir(project_dir)
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .output()
            .ok()
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
            .unwrap_or_default();
        if !head_sha.is_empty() {
            env_map.insert("HEAD_SHA".into(), head_sha);
        }
    }

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
// Run a single hook with output-based (idle) timeout
// Monitors stdout/stderr in real-time and resets idle timer on each output
// ---------------------------------------------------------------------------

fn run_hook_with_idle_timeout(
    hooks_dir: &Path,
    hook_name: &str,
    extra_args: &[&str],
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    idle_timeout: Duration,
    max_timeout: Duration,
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

    for arg in extra_args {
        cmd.arg(arg);
    }

    cmd.stdin(Stdio::from(stdin_file))
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

    // Shared state between output reader threads and the main loop
    let last_output = Arc::new(Mutex::new(Instant::now()));
    let stdout_done = Arc::new(AtomicBool::new(false));
    let stderr_done = Arc::new(AtomicBool::new(false));
    let stdout_buf = Arc::new(Mutex::new(Vec::new()));
    let stderr_buf = Arc::new(Mutex::new(Vec::new()));

    // Spawn thread to read stdout in real-time
    let last_out = Arc::clone(&last_output);
    let stdout_done_flag = Arc::clone(&stdout_done);
    let stdout_buffer = Arc::clone(&stdout_buf);
    if let Some(stdout) = child.stdout.take() {
        let reader = BufReader::new(stdout);
        thread::spawn(move || {
            for line in reader.lines() {
                if let Ok(line) = line {
                    let _ = stdout_buffer.lock().unwrap().write_all(line.as_bytes());
                    let _ = stdout_buffer.lock().unwrap().write_all(b"\n");
                    *last_out.lock().unwrap() = Instant::now();
                }
            }
            stdout_done_flag.store(true, Ordering::SeqCst);
        });
    }

    // Spawn thread to read stderr in real-time
    let last_err = Arc::clone(&last_output);
    let stderr_done_flag = Arc::clone(&stderr_done);
    let stderr_buffer = Arc::clone(&stderr_buf);
    if let Some(stderr) = child.stderr.take() {
        let reader = BufReader::new(stderr);
        thread::spawn(move || {
            for line in reader.lines() {
                if let Ok(line) = line {
                    let _ = stderr_buffer.lock().unwrap().write_all(line.as_bytes());
                    let _ = stderr_buffer.lock().unwrap().write_all(b"\n");
                    *last_err.lock().unwrap() = Instant::now();
                }
            }
            stderr_done_flag.store(true, Ordering::SeqCst);
        });
    }

    let start = Instant::now();
    loop {
        match child.try_wait() {
            Ok(Some(status)) => {
                // Process finished - wait for output readers to complete
                thread::sleep(Duration::from_millis(50));
                return HookResult {
                    name: hook_name.into(),
                    rc: status.code().unwrap_or(1),
                    stdout: String::from_utf8_lossy(&stdout_buf.lock().unwrap()).into_owned(),
                    stderr: String::from_utf8_lossy(&stderr_buf.lock().unwrap()).into_owned(),
                };
            }
            Ok(None) => {
                let elapsed = start.elapsed();
                let idle = last_output.lock().unwrap().elapsed();

                // Check absolute max timeout first
                if elapsed >= max_timeout {
                    let _ = child.kill();
                    let _ = child.wait();
                    return HookResult {
                        name: hook_name.into(),
                        rc: 124,
                        stdout: String::new(),
                        stderr: format!(
                            "{hook_name}: absolute timeout after {}s",
                            max_timeout.as_secs()
                        ),
                    };
                }

                // Check idle timeout - kill if no output for X seconds
                if idle >= idle_timeout {
                    let _ = child.kill();
                    let _ = child.wait();
                    return HookResult {
                        name: hook_name.into(),
                        rc: 124,
                        stdout: String::from_utf8_lossy(&stdout_buf.lock().unwrap()).into_owned(),
                        stderr: format!(
                            "{hook_name}: idle timeout after {}s of no output",
                            idle_timeout.as_secs()
                        ),
                    };
                }

                // Both streams done and no more coming - process must have exited
                if stdout_done.load(Ordering::SeqCst) && stderr_done.load(Ordering::SeqCst) {
                    // Give a moment for any remaining output
                    thread::sleep(Duration::from_millis(50));
                    return HookResult {
                        name: hook_name.into(),
                        rc: child
                            .wait()
                            .ok()
                            .and_then(|s| s.code())
                            .unwrap_or(1),
                        stdout: String::from_utf8_lossy(&stdout_buf.lock().unwrap()).into_owned(),
                        stderr: String::from_utf8_lossy(&stderr_buf.lock().unwrap()).into_owned(),
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

// ---------------------------------------------------------------------------
// Run a single hook (legacy time-based timeout)
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

// fn run_parallel(
//    hooks: &[(&str, &[&str])],
//    hooks_dir: &Path,
//    env_map: &HashMap<String, String>,
//    temp_path: &Path,
//    timeout: Option<Duration>,
// ) -> Vec<HookResult> {
//    let env_arc = Arc::new(env_map.clone());
//    let hooks_dir_arc = Arc::new(hooks_dir.to_path_buf());
//    let temp_path_arc = Arc::new(temp_path.to_path_buf());
//    let results: Arc<Mutex<Vec<HookResult>>> = Arc::new(Mutex::new(Vec::new()));
//
//    let mut handles = Vec::new();
//
//    for (hook, args) in hooks {
//        let hook_name = hook.to_string();
//        let args_owned: Vec<String> = args.iter().map(|a| a.to_string()).collect();
//        let env_c = Arc::clone(&env_arc);
//        let hdir = Arc::clone(&hooks_dir_arc);
//        let tpath = Arc::clone(&temp_path_arc);
//        let res = Arc::clone(&results);
//
//        let handle = thread::spawn(move || {
//            let args_refs: Vec<&str> = args_owned.iter().map(|s| s.as_str()).collect();
//            let result = run_hook(&hdir, &hook_name, &args_refs, &env_c, &tpath, timeout);
//            res.lock().unwrap().push(result);
//        });
//        handles.push(handle);
//    }
//
//    for h in handles {
//        let _ = h.join();
//    }
//
//    Arc::try_unwrap(results).unwrap().into_inner().unwrap()
// }

// ---------------------------------------------------------------------------
// Run hooks in parallel with output-based (idle) timeout
// ---------------------------------------------------------------------------

fn run_parallel_with_idle_timeout(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    idle_timeout: Duration,
    max_timeout: Duration,
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
            let result =
                run_hook_with_idle_timeout(&hdir, &hook_name, &args_refs, &env_c, &tpath, idle_timeout, max_timeout);
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

fn dispatch_notification(
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    event: &str,
    severity: &str,
    title: &str,
    message: &str,
) {
    let script = hooks_dir.join("notify-agent-event.sh");
    if !script.exists() {
        return;
    }
    let mut cmd = Command::new(script);
    cmd.arg("--event")
        .arg(event)
        .arg("--severity")
        .arg(severity)
        .arg("--title")
        .arg(title)
        .arg("--message")
        .arg(message)
        .current_dir(env_map.get("PROJECT_DIR").cloned().unwrap_or_default())
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    for (k, v) in env_map {
        cmd.env(k, v);
    }
    let _ = cmd.spawn();
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!(
            "usage: hook-dispatcher <pretool|posttool|stop|sessionstart|promptsubmit|\
             subagentstart|subagentstop|precompact|sessionend|taskcompleted|teammateidle>"
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
        "teammateidle" => Mode::TeammateIdle,
        other => {
            eprintln!("unknown mode: {other}");
            return ExitCode::from(1);
        }
    };

    // Read stdin — when run from TTY (e.g. `hook-dispatcher stop`), use empty JSON to avoid blocking
    let mut raw_json = String::new();
    if std::io::stdin().is_terminal() {
        raw_json = "{}".to_string();
    } else {
        std::io::stdin()
            .read_to_string(&mut raw_json)
            .expect("failed to read stdin");
        if raw_json.trim().is_empty() {
            raw_json = "{}".to_string();
        }
    }

    // Parse JSON
    let input: HookInput = match serde_json::from_str(&raw_json) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("JSON parse error: {e}");
            return ExitCode::from(1);
        }
    };

    let hooks_dir = resolve_hooks_dir();
    let mut env_map = build_env(&input, &raw_json, mode, &hooks_dir);
    let temp_file = TempFile::new(&raw_json);

    match mode {
        // -----------------------------------------------------------------
        // PreToolUse: sequential, fail-fast (blocking)
        // -----------------------------------------------------------------
        Mode::Pretool => {
            let tool_name = input.tool_name.as_deref().unwrap_or("");
            
            // Native pre-tool checks
            if tool_name == "Write" {
                let rc = run_doc_location_guard(&env_map);
                if rc != 0 {
                    return ExitCode::from(rc as u8);
                }
            }

            let hooks: Vec<(&str, &[&str])> = match tool_name {
                "Write" => vec![
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
            let rc = run_combined_advisory(&hooks, &hooks_dir, &env_map, &temp_file.path, "POSTTOOL");
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // Stop: parallel with timeout, propagate exit code
        // -----------------------------------------------------------------
        Mode::Stop => {
            let stop_settings = read_stop_settings(&env_map.get("PROJECT_DIR").cloned().unwrap_or_default());
            env_map.insert("THGENT_STOP_PROFILE".into(), stop_settings.profile.clone());
            env_map.insert(
                "THGENT_STOP_IDLE_TIMEOUT_SEC".into(),
                stop_settings.idle_timeout_sec.to_string(),
            );
            env_map.insert(
                "THGENT_STOP_MAX_TIMEOUT_SEC".into(),
                stop_settings.max_timeout_sec.to_string(),
            );

            // MTSP-08: Partial native governance scan
            if stop_settings.profile == "full" {
                if let Some(dir) = env_map.get("PROJECT_DIR") {
                    run_governance_scan(dir);
                }
            }

            // MTSP-18: Trigger memory scraping on Stop
            let _ = Command::new("thegent")
                .args(["memory", "scrape"])
                .current_dir(env_map.get("PROJECT_DIR").cloned().unwrap_or_default())
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .spawn();

            let hooks: Vec<(&str, &[&str])> = match stop_settings.profile.as_str() {
                // Minimal floor for very tight loops.
                "ultrafast" => vec![
                    ("stop-reconcile.sh", &[]),
                ],
                // Hybrid fast profile: keep bounded runtime while still running stage-gated quality checks.
                "fast" => vec![
                    ("quality-gate.sh", &[]),
                    ("stop-reconcile.sh", &[]),
                ],
                // Standard profile: adds task closure and orphan pruning.
                "standard" => vec![
                    ("quality-gate.sh", &[]),
                    ("prune-orphans-stop.sh", &[]),
                    ("stop-reconcile.sh", &[]),
                    ("task-completion-verifier.sh", &[]),
                ],
                // Full profile: all governance + verification hooks.
                _ => vec![
                    ("harvest-idea-seeds-stop.sh", &[]),
                    ("harvest-pending-queue.sh", &[]),
                    ("governance-gates.sh", &[]),
                    ("qa-supply-chain-verifier.sh", &[]),
                    ("quality-gate.sh", &[]),
                    ("complexity-ratchet.sh", &[]),
                    ("security-pipeline.sh", &[]),
                    ("spec-verifier.sh", &[]),
                    ("test-maturity.sh", &[]),
                    ("prune-orphans-stop.sh", &[]),
                    ("stop-reconcile.sh", &[]),
                    ("task-completion-verifier.sh", &[]),
                ],
            };

            // Filter out skipped hooks
            let project_dir = env_map.get("PROJECT_DIR").cloned().unwrap_or_default();
            let skip_list = get_skip_hooks(&project_dir);
            let hooks: Vec<(&str, &[&str])> = hooks
                .into_iter()
                .filter(|(name, _)| !should_skip_hook(name, &skip_list))
                .collect();

            // Print skip notifications
            for name in skip_list.iter() {
                eprintln!("SKIP_HOOKS: skipping {}.sh", name);
            }

            // Output-based (idle) timeout and absolute max timeout are hard-clamped
            // into the 5..15s range to avoid long Stop stalls.
            let idle_timeout = Duration::from_secs(stop_settings.idle_timeout_sec);
            let max_timeout = Duration::from_secs(stop_settings.max_timeout_sec);
            eprintln!(
                "STOP DISPATCHER: profile={}, idle_timeout={}s, max_timeout={}s, hooks={}",
                stop_settings.profile,
                stop_settings.idle_timeout_sec,
                stop_settings.max_timeout_sec,
                hooks.len()
            );
            let results = run_parallel_with_idle_timeout(
                &hooks,
                &hooks_dir,
                &env_map,
                &temp_file.path,
                idle_timeout,
                max_timeout,
            );

            let mut max_rc: i32 = 0;
            let mut failures = Vec::new();
            for r in &results {
                // Only print output on failure (not on success)
                if r.rc != 0 {
                    if !r.stdout.is_empty() {
                        eprint!("{}", r.stdout);
                    }
                    failures.push(format!("{}(rc={})", r.name, r.rc));
                    if !r.stderr.is_empty() {
                        eprint!("{}", r.stderr);
                    }
                }
                if r.rc > max_rc {
                    max_rc = r.rc;
                }
            }
            // Only print failure summary if there are actual failures
            // Silent on complete success (no output when all hooks pass)
            if !failures.is_empty() {
                eprintln!(
                    "STOP DISPATCHER: non-zero from: {}",
                    failures.join("; ")
                );
            }
            let notify_msg = if failures.is_empty() {
                format!(
                    "profile={} hooks={} status=ok",
                    stop_settings.profile,
                    hooks.len()
                )
            } else {
                format!(
                    "profile={} hooks={} failures={}",
                    stop_settings.profile,
                    hooks.len(),
                    failures.join(", ")
                )
            };
            dispatch_notification(
                &hooks_dir,
                &env_map,
                "stop",
                if failures.is_empty() { "info" } else { "error" },
                if failures.is_empty() { "Stop Complete" } else { "Stop Issues" },
                &notify_msg,
            );
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
                ("session-start-pending-notice.sh", &[]),
                ("session-start-spotlight-exclude.sh", &[]),
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
            let native_rc = run_prompt_submit_guard(&env_map, &serde_json::to_value(&input).unwrap());
            if native_rc != 99 {
                return ExitCode::from(native_rc as u8);
            }
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
            let rc = run_session_cleanup(&env_map);
            dispatch_notification(
                &hooks_dir,
                &env_map,
                "sessionend",
                "info",
                "Session Complete",
                "",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // TaskCompleted: single script, advisory
        // -----------------------------------------------------------------
        Mode::TaskCompleted => {
            // Run quality verifier first
            run_single_advisory(
                "task-completion-verifier.sh",
                &[],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "TASKCOMPLETED",
            );
            // Then run teammate coordination hook
            let rc = run_single_advisory(
                "task-completed.sh",
                &[],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "TASKCOMPLETED",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // TeammateIdle: single script, advisory (with exit 2 sentinel)
        // -----------------------------------------------------------------
        Mode::TeammateIdle => {
            // TeammateIdle is special: it can return exit 2 to signal feedback injection.
            // So we don't use run_single_advisory which forces exit 0.
            let result = run_hook(&hooks_dir, "teammate-idle.sh", &[], &env_map, &temp_file.path, None);
            if !result.stdout.is_empty() {
                eprint!("{}", result.stdout);
            }
            if result.rc != 0 && result.rc != 2 {
                if !result.stderr.is_empty() {
                    eprint!("{}", result.stderr);
                }
                eprintln!(
                    "TEAMMATEIDLE DISPATCHER: failure: {}(rc={})",
                    result.name, result.rc
                );
            }
            ExitCode::from(result.rc as u8)
        }
    }
}
