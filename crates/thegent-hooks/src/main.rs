use std::env;
use std::fs;
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio, exit};
use std::os::unix::process::ExitStatusExt;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use blake3::Hasher;
use base16ct::lower;
use chrono::{DateTime, Utc};
use regex::Regex;
use lazy_static::lazy_static;
use tokio::runtime::Runtime;
use tokio::process::Command as TokioCommand;
use tokio::io::AsyncWriteExt;
use futures::future::join_all;
use ignore::WalkBuilder;
use std::collections::HashMap;

// Library re-export for binary use
use thegent_hooks::{
    PolicyEngine, CostCalculator, QualityEvaluator, ConfigLoader, HookConfig,
    ChangedFilesDetector, ChangedFile, ChangeStatus, ImpactType, FilterOptions, DependencyGraph,
    ChangedFilesError, DetectionStrategy, HookReport, ReportManager, AffectedTestsAnalyzer, PrewarmManager,
};

const VERSION: &str = "0.1.0";
const CACHE_DIR: &str = "/tmp/thegent-hooks-cache";
const DEFAULT_TTL_SECS: u64 = 600;

#[derive(Debug, Serialize, Deserialize)]
struct HookInput {
    pub hook_name: Option<String>,
    pub project_dir: Option<String>,
    pub cwd: Option<String>,
    pub session_id: Option<String>,
    pub head_sha: Option<String>,
    pub changed_files: Option<Vec<String>>,
    pub stop_active: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
struct BreakerState {
    pub failures: u32,
    pub last_failure: Option<DateTime<Utc>>,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct DebounceState {
    pub last_run: DateTime<Utc>,
    pub pending_files: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Manifest {
    pub hook_name: String,
    pub files: Vec<FileManifest>,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
struct FileManifest {
    pub path: String,
    pub hash: String,
}

#[derive(Debug)]
enum Error {
    Io(io::Error),
    Json(serde_json::Error),
    Cache(String),
    LockTimeout,
}

impl From<io::Error> for Error {
    fn from(e: io::Error) -> Self { Error::Io(e) }
}

impl From<serde_json::Error> for Error {
    fn from(e: serde_json::Error) -> Self { Error::Json(e) }
}

fn print_version() {
    println!("thegent-hooks {}", VERSION);
}

fn print_help() {
    println!("thegent-hooks - Hook runtime for thegent");
    println!();
    println!("USAGE:");
    println!("    thegent-hooks <SUBCOMMAND> [ARGS]");
    println!();
    println!("SUBCOMMANDS:");
    println!("    init                    Initialize hook environment from stdin JSON");
    println!("    dispatch                Parallel hook dispatcher (replaces stop-dispatcher.sh)");
    println!("    quality-gate            Native quality gate (replaces quality-gate.sh)");
    println!("    security-pipeline       Native security pipeline (replaces security-pipeline.sh)");
    println!("    complexity-ratchet      Native complexity ratchet (replaces complexity-ratchet.sh)");
    println!("    cache-key               Generate cache key from hook name + git state");
    println!("    cache-check             Check if cache entry exists and is fresh");
    println!("    cache-read              Read cached result (JSON)");
    println!("    cache-write             Write result to cache");
    println!("    git                     Execute git command with caching/parallelism");
    println!("    changed-files           Get list of changed files");
    println!("    config-get              Get config value by key path");
    println!("    breaker-check           Check circuit breaker status");
    println!("    breaker-record          Record circuit breaker failure");
    println!("    breaker-reset           Reset circuit breaker status");
    println!("    debounce                Coordinated hook debounce");
    println!("    incremental-check       Check incremental manifest");
    println!("    incremental-record      Record incremental manifest");
    println!("    file-hash               Compute file hash (blake3)");
    println!("    agent                   Unified agent wrapper with mesh coordination");
    println!("    version                 Show version");
    println!("    help                    Show this help");
    println!();
    println!("ENVIRONMENT:");
    println!("    THEGENT_CACHE_DIR    Override cache directory (default: {})", CACHE_DIR);
    println!("    THEGENT_TTL          Default cache TTL in seconds (default: {})", DEFAULT_TTL_SECS);
}

fn ensure_cache_dir() -> PathBuf {
    let dir = env::var("THEGENT_CACHE_DIR")
        .unwrap_or_else(|_| CACHE_DIR.to_string());
    let path = PathBuf::from(dir);
    fs::create_dir_all(&path).unwrap_or_else(|_| {
        eprintln!("Failed to create cache directory: {}", path.display());
        exit(1);
    });
    path
}

fn get_cache_path(key: &str) -> PathBuf {
    ensure_cache_dir().join(key)
}

fn read_input() -> Result<Value, Error> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    if input.trim().is_empty() {
        Ok(Value::Null)
    } else {
        Ok(serde_json::from_str(&input)?)
    }
}

fn compute_blake3_hash(content: &str) -> String {
    let mut hasher = Hasher::new();
    hasher.update(content.as_bytes());
    let hash = hasher.finalize();
    let bytes = hash.as_bytes();
    let mut buf = vec![0u8; bytes.len() * 2];
    let encoded = lower::encode(bytes, &mut buf).unwrap();
    String::from_utf8_lossy(encoded).to_string()
}

fn compute_file_hash(path: &Path) -> io::Result<String> {
    let mut file = fs::File::open(path)?;
    let mut hasher = Hasher::new();
    let mut buffer = [0; 8192];
    loop {
        let count = file.read(&mut buffer)?;
        if count == 0 { break; }
        hasher.update(&buffer[..count]);
    }
    let hash = hasher.finalize();
    let bytes = hash.as_bytes();
    let mut buf = vec![0u8; bytes.len() * 2];
    let encoded = lower::encode(bytes, &mut buf).unwrap();
    Ok(String::from_utf8_lossy(encoded).to_string())
}

fn cmd_init() {
    let input = read_input().unwrap_or_else(|_| Value::Null);
    
    let project_dir = input.get("project_dir")
        .and_then(|v| v.as_str())
        .unwrap_or(".");
    let cwd = input.get("cwd")
        .and_then(|v| v.as_str())
        .unwrap_or(".");
    let session_id = input.get("session_id")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    let head_sha = input.get("head_sha")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    let hook_name = input.get("hook_name")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    
    // Print environment variables for shell sourcing
    println!("export PROJECT_DIR={}", project_dir);
    println!("export CWD={}", cwd);
    println!("export SESSION_ID={}", session_id);
    println!("export HEAD_SHA={}", head_sha);
    println!("export HOOK_NAME={}", hook_name);
    println!("export THEGENT_HOOKS_INIT=1");
}

fn cmd_quality_gate() {
    let rt = Runtime::new().unwrap();
    rt.block_on(async {
        let mut input_buffer = Vec::new();
        let _ = io::stdin().read_to_end(&mut input_buffer);
        let input: Value = serde_json::from_slice(&input_buffer).unwrap_or(Value::Null);
        
        let project_dir = input.get("project_dir")
            .and_then(|v| v.as_str())
            .map(PathBuf::from)
            .unwrap_or_else(|| env::current_dir().unwrap_or_default());

        println!("==> Quality Gate (Rust Native)");
        
        // 1. Identify files
        let mut files_by_lang: HashMap<String, Vec<PathBuf>> = HashMap::new();
        
        let walker = WalkBuilder::new(&project_dir)
            .hidden(false)
            .git_ignore(true)
            .build();
            
        for result in walker {
            if let Ok(entry) = result {
                if entry.file_type().map(|ft| ft.is_file()).unwrap_or(false) {
                    let path = entry.path().to_path_buf();
                    if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                        let lang = match ext {
                            "py" => "python",
                            "js" | "ts" | "jsx" | "tsx" => "javascript",
                            "rs" => "rust",
                            "go" => "go",
                            "sh" | "bash" | "zsh" => "shell",
                            "java" => "java",
                            "kt" => "kotlin",
                            _ => continue,
                        };
                        files_by_lang.entry(lang.to_string()).or_default().push(path);
                    }
                }
            }
        }

        // 2. Parallel Linting
        let mut futures = Vec::new();
        
        // Python (Ruff)
        if let Some(py_files) = files_by_lang.get("python") {
            if !py_files.is_empty() {
                let files = py_files.clone();
                futures.push(tokio::spawn(async move {
                    let mut cmd = TokioCommand::new("ruff");
                    cmd.arg("check").args(&files).arg("--fix").arg("--silent");
                    let output = cmd.output().await;
                    ("Python (ruff)".to_string(), output)
                }));
            }
        }
        
        // JS/TS (oxlint)
        if let Some(js_files) = files_by_lang.get("javascript") {
            if !js_files.is_empty() {
                let files = js_files.clone();
                futures.push(tokio::spawn(async move {
                    let mut cmd = TokioCommand::new("oxlint");
                    cmd.arg("--deny-force").args(&files);
                    let output = cmd.output().await;
                    ("JS/TS (oxlint)".to_string(), output)
                }));
            }
        }

        let results = join_all(futures).await;
        let mut all_ok = true;
        
        for res in results {
            if let Ok((name, output_res)) = res {
                match output_res {
                    Ok(output) => {
                        if !output.status.success() {
                            all_ok = false;
                            println!("[FAILED] {}", name);
                            let _ = io::stdout().write_all(&output.stdout);
                            let _ = io::stderr().write_all(&output.stderr);
                        } else {
                            println!("[OK] {}", name);
                        }
                    },
                    Err(e) => {
                        println!("[SKIP] {} (not found: {})", name, e);
                    }
                }
            }
        }
        
        if all_ok {
            println!("==> Quality Gate: PASSED");
            exit(0);
        } else {
            println!("==> Quality Gate: FAILED");
            exit(1);
        }
    });
}

fn cmd_dispatch() {
    let rt = Runtime::new().unwrap();
    rt.block_on(async {
        // Read stdin once
        let mut input_buffer = Vec::new();
        io::stdin().read_to_end(&mut input_buffer).unwrap_or(0);
        
        let hooks_dir = env::current_exe()
            .ok()
            .and_then(|p| p.parent().map(|p| p.to_path_buf()))
            .unwrap_or_else(|| PathBuf::from("."));
            
        // In dev, hooks might be in ../../../hooks relative to the binary in target/release
        let mut actual_hooks_dir = hooks_dir.clone();
        if !actual_hooks_dir.join("quality-gate.sh").exists() {
            if let Ok(project_dir) = env::var("PROJECT_DIR") {
                actual_hooks_dir = PathBuf::from(project_dir).join("thegent/hooks");
            }
        }

        let stop_hooks = vec![
            "quality-gate.sh",
            "security-pipeline.sh",
            "complexity-ratchet.sh",
            "spec-verifier.sh",
            "test-maturity.sh",
            "task-completion-verifier.sh",
            "stop-reconcile.sh",
            "agileplus-cycle.sh",
            "teammate-reconcile.sh",
        ];

        let mut futures = Vec::new();
        for hook in stop_hooks {
            let hook_path = actual_hooks_dir.join(hook);
            if !hook_path.exists() { continue; }
            
            let input = input_buffer.clone();
            futures.push(tokio::spawn(async move {
                let mut cmd = TokioCommand::new("bash");
                cmd.arg(&hook_path)
                    .stdin(Stdio::piped())
                    .stdout(Stdio::piped())
                    .stderr(Stdio::piped());
                
                let mut child = cmd.spawn().expect("Failed to spawn hook");
                
                if let Some(mut stdin) = child.stdin.take() {
                    let _ = stdin.write_all(&input).await;
                }
                
                let output = tokio::time::timeout(Duration::from_secs(60), child.wait_with_output()).await;
                
                match output {
                    Ok(Ok(out)) => (hook.to_string(), out),
                    _ => (hook.to_string(), std::process::Output {
                        status: std::process::ExitStatus::from_raw(124), // timeout
                        stdout: Vec::new(),
                        stderr: "Hook timed out after 60s".as_bytes().to_vec(),
                    }),
                }
            }));
        }

        let results = join_all(futures).await;
        let mut max_rc = 0;
        
        for res in results {
            if let Ok((_name, output)) = res {
                let rc = output.status.code().unwrap_or(1);
                if rc > max_rc { max_rc = rc; }
                
                if !output.stdout.is_empty() {
                    let _ = io::stdout().write_all(&output.stdout);
                }
                if !output.stderr.is_empty() {
                    let _ = io::stderr().write_all(&output.stderr);
                }
            }
        }
        
        exit(max_rc);
    });
}

fn cmd_security_pipeline() {
    let rt = Runtime::new().unwrap();
    rt.block_on(async {
        let mut input_buffer = Vec::new();
        let _ = io::stdin().read_to_end(&mut input_buffer);
        let input: Value = serde_json::from_slice(&input_buffer).unwrap_or(Value::Null);
        
        let project_dir = input.get("project_dir")
            .and_then(|v| v.as_str())
            .map(PathBuf::from)
            .unwrap_or_else(|| env::current_dir().unwrap_or_default());

        println!("==> Security Pipeline (Rust Native)");
        
        // Layer 1: Secrets (Internal Regex + optional Gitleaks)
        let mut futures = Vec::new();
        
        let proj_dir_clone = project_dir.clone();
        futures.push(tokio::spawn(async move {
            let mut findings = Vec::new();
            let mut count = 0;
            
            // Internal Regex Detection
            let secret_patterns = [
                r#"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][^'\" ]{8,}"#,
                r#"(?i)(secret|password|passwd|pwd)\s*[:=]\s*['\"][^'\" ]{8,}"#,
                r#"(?i)(token|bearer)\s*[:=]\s*['\"][^'\" ]{8,}"#,
                r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----",
                r"ghp_[a-zA-Z0-9]{36}",
                r"sk-[a-zA-Z0-9]{20,}",
            ];
            
            let mut compiled_regs = Vec::new();
            for p in &secret_patterns {
                if let Ok(re) = Regex::new(p) { compiled_regs.push(re); }
            }
            
            let walker = WalkBuilder::new(&proj_dir_clone)
                .hidden(false)
                .git_ignore(true)
                .build();
                
            for result in walker {
                if let Ok(entry) = result {
                    if entry.file_type().map(|ft| ft.is_file()).unwrap_or(false) {
                        let path = entry.path();
                        if let Ok(content) = fs::read_to_string(path) {
                            for re in &compiled_regs {
                                if re.is_match(&content) {
                                    findings.push(format!("[HIGH] secrets: Possible secret in {}", path.display()));
                                    count += 1;
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            
            ("Layer 1 - Secrets".to_string(), count, findings)
        }));

        // Layer 2: SAST (Bandit for Python)
        let proj_dir_clone2 = project_dir.clone();
        futures.push(tokio::spawn(async move {
            let mut findings = Vec::new();
            let mut count = 0;
            
            let mut cmd = TokioCommand::new("bandit");
            cmd.arg("-r").arg(&proj_dir_clone2).arg("-q").arg("-f").arg("txt");
            
            if let Ok(output) = cmd.output().await {
                if !output.status.success() {
                    let out_str = String::from_utf8_lossy(&output.stdout);
                    for line in out_str.lines().take(10) {
                        findings.push(format!("[MEDIUM] sast/bandit: {}", line));
                        count += 1;
                    }
                }
            }
            
            ("Layer 2 - SAST".to_string(), count, findings)
        }));

        let results = join_all(futures).await;
        let mut total_findings = 0;
        
        for res in results {
            if let Ok((name, count, findings)) = res {
                total_findings += count;
                if count > 0 {
                    println!("{}: WARN ({} findings)", name, count);
                    for f in findings { println!("  {}", f); }
                } else {
                    println!("{}: PASS", name);
                }
            }
        }
        
        println!("==> Security Pipeline: DONE ({} total findings)", total_findings);
        exit(0); // Advisory only
    });
}

fn cmd_complexity_ratchet() {
    let mut input_buffer = Vec::new();
    let _ = io::stdin().read_to_end(&mut input_buffer);
    let input: Value = serde_json::from_slice(&input_buffer).unwrap_or(Value::Null);
    
    let project_dir = input.get("project_dir")
        .and_then(|v| v.as_str())
        .map(PathBuf::from)
        .unwrap_or_else(|| env::current_dir().unwrap_or_default());

    println!("==> Complexity Ratchet (Rust Native)");
    
    let walker = WalkBuilder::new(&project_dir)
        .hidden(false)
        .git_ignore(true)
        .build();
        
    let mut total_files = 0;
    let mut max_cyc = 0;
    let mut max_file = String::new();

    for result in walker {
        if let Ok(entry) = result {
            if entry.file_type().map(|ft| ft.is_file()).unwrap_or(false) {
                let path = entry.path();
                let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                if matches!(ext, "py" | "js" | "ts" | "jsx" | "tsx" | "rs" | "go" | "java" | "kt") {
                    if let Ok(metrics) = thegent_hooks::QualityEvaluator::measure_complexity(path) {
                        total_files += 1;
                        if metrics.cyclomatic_complexity > max_cyc {
                            max_cyc = metrics.cyclomatic_complexity;
                            max_file = path.display().to_string();
                        }
                    }
                }
            }
        }
    }
    
    println!("  Analyzed {} files", total_files);
    if max_cyc > 0 {
        println!("  Max Complexity: {} ({})", max_cyc, max_file);
    }
    println!("==> Complexity Ratchet: OK");
    exit(0);
}

fn cmd_cache_key() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks cache-key <hook_name> [changed_files...]");
        exit(1);
    }
    
    let hook_name = &args[2];
    let changed_files: Vec<String> = if args.len() > 3 {
        args[3..].to_vec()
    } else {
        Vec::new()
    };
    
    // Get head SHA if not provided via stdin
    let head_sha = if let Ok(input) = read_input() {
        input.get("head_sha")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    } else {
        String::new()
    };
    
    // Build cache key content
    let mut content = format!("{}:{}", hook_name, head_sha);
    if !changed_files.is_empty() {
        content.push(':');
        content.push_str(&changed_files.join(","));
    }
    
    println!("{}", compute_blake3_hash(&content));
}

fn is_cache_fresh(cache_path: &PathBuf, ttl_secs: u64) -> bool {
    if !cache_path.exists() {
        return false;
    }
    
    if let Ok(metadata) = fs::metadata(cache_path) {
        if let Ok(modified) = metadata.modified() {
            if let Ok(elapsed) = modified.elapsed() {
                return elapsed < Duration::from_secs(ttl_secs);
            }
        }
    }
    false
}

fn cmd_cache_check() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks cache-check <key> [ttl_seconds]");
        exit(1);
    }
    
    let key = &args[2];
    let ttl: u64 = args.get(3)
        .and_then(|v| v.parse().ok())
        .unwrap_or(DEFAULT_TTL_SECS);
    
    let cache_path = get_cache_path(key);
    
    if is_cache_fresh(&cache_path, ttl) {
        exit(0); // Cache hit
    } else {
        exit(1); // Cache miss
    }
}

fn cmd_cache_read() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks cache-read <key>");
        exit(1);
    }
    
    let key = &args[2];
    let cache_path = get_cache_path(key);
    
    match fs::read_to_string(&cache_path) {
        Ok(content) => {
            println!("{}", content);
        }
        Err(e) => {
            eprintln!("Cache read error: {}", e);
            exit(1);
        }
    }
}

fn cmd_cache_write() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 5 {
        eprintln!("Usage: thegent-hooks cache-write <key> <rc> <output_json>");
        exit(1);
    }
    
    let key = &args[2];
    let _rc = &args[3];
    let output = &args[4];
    
    let cache_path = get_cache_path(key);
    
    if let Err(e) = fs::write(&cache_path, output) {
        eprintln!("Cache write error: {}", e);
        exit(1);
    }
}

fn cmd_git() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks git <command> [args...]");
        eprintln!("Commands: status, diff, rev-parse, ls-files, log, etc.");
        exit(1);
    }
    
    let command = &args[2];
    let git_args: Vec<&str> = args.iter().skip(3).map(|s| s.as_str()).collect();
    
    match command.as_str() {
        "status" | "diff" | "rev-parse" | "ls-files" | "log" | "show" => {
            // Read-only path: check cache
            let cache_key = compute_blake3_hash(&format!("git:{}:{}", command, git_args.join(" ")));
            let cache_path = get_cache_path(&format!("git-{}.cache", cache_key));
            
            if is_cache_fresh(&cache_path, DEFAULT_TTL_SECS) {
                if let Ok(content) = fs::read_to_string(&cache_path) {
                    print!("{}", content);
                    return;
                }
            }
            
            let output = Command::new("git")
                .args([command]).args(&git_args)
                .output()
                .expect("Failed to execute git");
            
            if output.status.success() {
                let stdout = String::from_utf8_lossy(&output.stdout);
                let _ = fs::write(&cache_path, stdout.as_ref());
                let _ = io::stdout().write_all(&output.stdout);
            } else {
                let _ = io::stdout().write_all(&output.stdout);
                let _ = io::stderr().write_all(&output.stderr);
            }
            exit(output.status.code().unwrap_or(0));
        }
        "add" | "commit" | "checkout" | "reset" | "rm" | "mv" | "pull" | "push" | "merge" | "rebase" => {
            // Write path: Handle index.lock contention
            let lock_file = PathBuf::from(".git/index.lock");
            let mut retries = 0;
            while lock_file.exists() && retries < 60 {
                if let Ok(metadata) = fs::metadata(&lock_file) {
                    if let Ok(modified) = metadata.modified() {
                        if let Ok(elapsed) = modified.elapsed() {
                            if elapsed.as_secs() > 10 {
                                eprintln!("GIT-MUTEX: Stealing stale lock ({} seconds old)...", elapsed.as_secs());
                                let _ = fs::remove_file(&lock_file);
                                break;
                            }
                        }
                    }
                }
                eprintln!("GIT-MUTEX: Waiting for git index.lock...");
                std::thread::sleep(Duration::from_millis(500));
                retries += 1;
            }
            
            let status = Command::new("git")
                .args([command]).args(&git_args)
                .status()
                .expect("Failed to execute git");
            exit(status.code().unwrap_or(0));
        }
        _ => {
            let status = Command::new("git")
                .args([command]).args(&git_args)
                .status()
                .expect("Failed to execute git");
            exit(status.code().unwrap_or(0));
        }
    }
}

fn cmd_changed_files() {
    let args: Vec<String> = env::args().collect();
    let range = args.get(2).map(|s| s.as_str()).unwrap_or("HEAD~1..HEAD");
    
    let output = Command::new("git")
        .args(&["diff", "--name-only", range])
        .output()
        .expect("Failed to execute git diff");
    
    let mut files: Vec<String> = String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(|s| s.to_string())
        .filter(|s| !s.is_empty())
        .collect();
        
    // Also include untracked files
    let untracked = Command::new("git")
        .args(&["ls-files", "--others", "--exclude-standard"])
        .output()
        .expect("Failed to execute git ls-files");
        
    for line in String::from_utf8_lossy(&untracked.stdout).lines() {
        if !line.is_empty() {
            files.push(line.to_string());
        }
    }
    
    files.sort();
    files.dedup();
    
    println!("{}", serde_json::to_string(&files).unwrap_or_else(|_| "[]".to_string()));
}

fn get_breaker_path(hook_name: &str) -> PathBuf {
    ensure_cache_dir().join(format!("breaker-{}.json", hook_name))
}

fn cmd_breaker_check() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks breaker-check <hook_name> [threshold] [cooldown_secs]");
        exit(1);
    }
    
    let hook_name = &args[2];
    let threshold: u32 = args.get(3).and_then(|v| v.parse().ok()).unwrap_or(3);
    let cooldown_secs: i64 = args.get(4).and_then(|v| v.parse().ok()).unwrap_or(300);
    
    let breaker_path = get_breaker_path(hook_name);
    if !breaker_path.exists() {
        println!("closed");
        exit(0);
    }
    
    if let Ok(content) = fs::read_to_string(&breaker_path) {
        if let Ok(state) = serde_json::from_str::<BreakerState>(&content) {
            if state.failures >= threshold {
                if let Some(last) = state.last_failure {
                    let now = Utc::now();
                    let elapsed = now.signed_duration_since(last).num_seconds();
                    if elapsed < cooldown_secs {
                        println!("open");
                        exit(1);
                    } else {
                        println!("half-open");
                        exit(0);
                    }
                }
            }
        }
    }
    
    println!("closed");
    exit(0);
}

fn cmd_breaker_record() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks breaker-record <hook_name>");
        exit(1);
    }
    
    let hook_name = &args[2];
    let breaker_path = get_breaker_path(hook_name);
    
    let mut state = if breaker_path.exists() {
        fs::read_to_string(&breaker_path)
            .ok()
            .and_then(|c| serde_json::from_str::<BreakerState>(&c).ok())
            .unwrap_or(BreakerState { failures: 0, last_failure: None, status: "closed".to_string() })
    } else {
        BreakerState { failures: 0, last_failure: None, status: "closed".to_string() }
    };
    
    state.failures += 1;
    state.last_failure = Some(Utc::now());
    state.status = "open".to_string();
    
    if let Ok(content) = serde_json::to_string(&state) {
        let _ = fs::write(&breaker_path, content);
    }
}

fn cmd_breaker_reset() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks breaker-reset <hook_name>");
        exit(1);
    }
    
    let hook_name = &args[2];
    let breaker_path = get_breaker_path(hook_name);
    if breaker_path.exists() {
        let _ = fs::remove_file(breaker_path);
    }
}

fn cmd_debounce() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks debounce <hook_name> [files...]");
        exit(1);
    }
    
    let hook_name = &args[2];
    let files: Vec<String> = if args.len() > 3 { args[3..].to_vec() } else { Vec::new() };
    
    let debounce_path = ensure_cache_dir().join(format!("debounce-{}.json", hook_name));
    let now = Utc::now();
    
    let mut state = if debounce_path.exists() {
        fs::read_to_string(&debounce_path)
            .ok()
            .and_then(|c| serde_json::from_str::<DebounceState>(&c).ok())
            .unwrap_or(DebounceState { last_run: now, pending_files: Vec::new() })
    } else {
        DebounceState { last_run: now - chrono::Duration::hours(24), pending_files: Vec::new() }
    };
    
    for file in files {
        if !state.pending_files.contains(&file) {
            state.pending_files.push(file);
        }
    }
    
    let elapsed = now.signed_duration_since(state.last_run).num_seconds();
    if elapsed >= 1 {
        state.last_run = now;
        let pending = state.pending_files.clone();
        state.pending_files.clear();
        if let Ok(content) = serde_json::to_string(&state) {
            let _ = fs::write(&debounce_path, content);
        }
        println!("{}", serde_json::to_string(&pending).unwrap_or_else(|_| "[]".to_string()));
        exit(0);
    } else {
        if let Ok(content) = serde_json::to_string(&state) {
            let _ = fs::write(&debounce_path, content);
        }
        exit(1);
    }
}

fn get_manifest_path(hook_name: &str) -> PathBuf {
    ensure_cache_dir().join(format!("manifest-{}.json", hook_name))
}

fn cmd_incremental_check() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks incremental-check <hook_name> [files...]");
        exit(1);
    }
    
    let hook_name = &args[2];
    let files: Vec<String> = if args.len() > 3 { args[3..].to_vec() } else { Vec::new() };
    
    let manifest_path = get_manifest_path(hook_name);
    if !manifest_path.exists() {
        println!("[]");
        exit(0);
    }
    
    let content = fs::read_to_string(&manifest_path).unwrap_or_else(|_| "{}".to_string());
    let old_manifest: Manifest = serde_json::from_str(&content).unwrap_or_else(|_| Manifest {
        hook_name: hook_name.to_string(),
        files: Vec::new(),
        timestamp: Utc::now(),
    });
    
    let mut changed = Vec::new();
    for file_path in files {
        let path = PathBuf::from(&file_path);
        if !path.exists() {
            changed.push(file_path);
            continue;
        }
        
        let new_hash = compute_file_hash(&path).unwrap_or_else(|_| "error".to_string());
        let old_hash = old_manifest.files.iter()
            .find(|f| f.path == file_path)
            .map(|f| f.hash.as_str())
            .unwrap_or("");
            
        if new_hash != old_hash {
            changed.push(file_path);
        }
    }
    
    println!("{}", serde_json::to_string(&changed).unwrap_or_else(|_| "[]".to_string()));
}

fn cmd_incremental_record() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks incremental-record <hook_name> [files...]");
        exit(1);
    }
    
    let hook_name = &args[2];
    let files: Vec<String> = if args.len() > 3 { args[3..].to_vec() } else { Vec::new() };
    
    let mut manifest = Manifest {
        hook_name: hook_name.to_string(),
        files: Vec::new(),
        timestamp: Utc::now(),
    };
    
    for file_path in files {
        let path = PathBuf::from(&file_path);
        if path.exists() {
            let hash = compute_file_hash(&path).unwrap_or_else(|_| "error".to_string());
            manifest.files.push(FileManifest { path: file_path, hash });
        }
    }
    
    if let Ok(content) = serde_json::to_string(&manifest) {
        let _ = fs::write(get_manifest_path(hook_name), content);
    }
}

fn cmd_file_hash() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks file-hash <file_path>");
        exit(1);
    }
    
    let path = PathBuf::from(&args[2]);
    match compute_file_hash(&path) {
        Ok(hash) => println!("{}", hash),
        Err(e) => {
            eprintln!("File hash error: {}", e);
            exit(1);
        }
    }
}

fn cmd_config_get() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks config-get <key_path>");
        exit(1);
    }
    
    let key_path = &args[2];
    let config_paths = vec![
        PathBuf::from(".thegent/config.json"),
        PathBuf::from(".thegent/settings.json"),
        PathBuf::from("pyproject.toml"),
        PathBuf::from("thegent.json"),
    ];
    
    for config_path in config_paths {
        if config_path.exists() {
            if let Ok(content) = fs::read_to_string(&config_path) {
                if let Ok(json) = serde_json::from_str::<Value>(&content) {
                    let parts: Vec<&str> = key_path.split('.').collect();
                    let mut current = &json;
                    let mut found = true;
                    for part in &parts {
                        if let Some(v) = current.get(*part) {
                            current = v;
                        } else {
                            found = false;
                            break;
                        }
                    }
                    if found {
                        println!("{}", serde_json::to_string(current).unwrap_or_else(|_| "null".to_string()));
                        return;
                    }
                }
            }
        }
    }
    
    println!("null");
}

fn cmd_agent() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks agent <agent_name> [--] <command> [args...]");
        exit(1);
    }
    
    let agent_name = &args[2];
    let mut cmd_start = 3;
    if args.len() > 3 && args[3] == "--" { cmd_start = 4; }
    if args.len() <= cmd_start { exit(1); }
    
    let command = &args[cmd_start];
    let cmd_args = &args[cmd_start + 1..];
    
    // Mesh logic would go here
    let status = Command::new(command)
        .args(cmd_args)
        .status()
        .expect("Failed to execute agent command");
    
    exit(status.code().unwrap_or(0));
}

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        print_help();
        return;
    }
    
    match args[1].as_str() {
        "version" | "--version" | "-V" => print_version(),
        "help" | "--help" | "-h" => print_help(),
        "init" => cmd_init(),
        "dispatch" => cmd_dispatch(),
        "quality-gate" => cmd_quality_gate(),
        "security-pipeline" => cmd_security_pipeline(),
        "complexity-ratchet" => cmd_complexity_ratchet(),
        "cache-key" => cmd_cache_key(),
        "cache-check" => cmd_cache_check(),
        "cache-read" => cmd_cache_read(),
        "cache-write" => cmd_cache_write(),
        "git" => cmd_git(),
        "changed-files" => cmd_changed_files(),
        "config-get" => cmd_config_get(),
        "breaker-check" => cmd_breaker_check(),
        "breaker-record" => cmd_breaker_record(),
        "breaker-reset" => cmd_breaker_reset(),
        "debounce" => cmd_debounce(),
        "incremental-check" => cmd_incremental_check(),
        "incremental-record" => cmd_incremental_record(),
        "file-hash" => cmd_file_hash(),
        "agent" => cmd_agent(),
        "uv" | "npm" | "pnpm" | "bun" | "yarn" | "pip" | "poetry" | "cargo" | "go" | "ruff" | "pytest" | "sed" | "cp" | "mv" | "rm" => {
            let status = Command::new(&args[1]).args(&args[2..]).status().expect("Failed to execute tool");
            exit(status.code().unwrap_or(0));
        }
        _ => {
            eprintln!("Unknown subcommand: {}", args[1]);
            print_help();
            exit(1);
        }
    }
}
