use std::env;
use std::fs;
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, exit};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use blake3::Hasher;
use base16ct::lower;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use chrono::{DateTime, Utc};
// Library re-export for binary use
use thegent_hooks::{
    PolicyEngine, CostCalculator, QualityEvaluator, ConfigLoader, HookConfig,
    ChangedFilesDetector, ChangedFile, ChangeStatus, ImpactType, FilterOptions, DependencyGraph,
};

#[cfg(feature = "gix")]
use thegent_git::gix_impl;

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
    println!("    cache-key               Generate cache key from hook name + git state");
    println!("    cache-check             Check if cache entry exists and is fresh");
    println!("    cache-read              Read cached result (JSON)");
    println!("    cache-write             Write result to cache");
    println!("    git                     Execute git command with caching");
    println!("    changed-files           Get list of changed files (basic, JSON output)");
    println!("    changed-files-filter    Get changed files with advanced filtering");
    println!("                            Filters: --extension, --directory, --status, --impact");
    println!("                            Exclusions: --exclude-extension, --exclude-directory");
    println!("    changed-files-impact    Get code-impacting changes only");
    println!("    changed-files-deps      Analyze dependencies between changed files");
    println!("                            Options: --dependents (include reverse deps)");
    println!("    config-get              Get config value by key path");
    println!("    breaker-check           Check circuit breaker status");
    println!("    breaker-record          Record circuit breaker failure");
    println!("    breaker-reset           Reset circuit breaker status");
    println!("    debounce                Coordinated hook debounce");
    println!("    incremental-check       Check incremental manifest");
    println!("    incremental-record      Record incremental manifest");
    println!("    file-hash               Compute file hash (blake3)");
    println!("    fr-ids                  Extract FR IDs from FUNCTIONAL_REQUIREMENTS.md");
    println!("    fr-index                Index file-to-FR mappings from codebase");
    println!("    progress                Update or show task progress");
    println!("    report                  Generate hook execution report (JSON)");
    println!("    learning-record         Record hook learning data");
    println!("    learning-should-skip    Check if hook should skip based on learning");
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
    let mut buf = vec![0u8; base16ct::encoded_len(bytes.len())];
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
    let mut buf = vec![0u8; base16ct::encoded_len(bytes.len())];
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
    
    // Agent passthrough
    if matches!(command.as_str(), "codex" | "copilot" | "dex" | "claude" | "cursor") {
        let status = Command::new(command)
            .args(&git_args)
            .status()
            .expect("Failed to execute agent");
        exit(status.code().unwrap_or(0));
    }
    
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
                io::stdout().write_all(&output.stdout).unwrap();
            } else {
                io::stdout().write_all(&output.stdout).unwrap();
                io::stderr().write_all(&output.stderr).unwrap();
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

fn cmd_changed_files_filter() {
    let args: Vec<String> = env::args().collect();
    let mut filters = FilterOptions::default();
    let mut range: Option<&str> = None;
    let mut i = 2;

    while i < args.len() {
        match args[i].as_str() {
            "--extension" | "-e" => {
                if i + 1 < args.len() {
                    filters.extensions.push(args[i + 1].trim_start_matches('.').to_string());
                    i += 2;
                } else {
                    eprintln!("--extension requires an argument");
                    exit(1);
                }
            }
            "--directory" | "-d" => {
                if i + 1 < args.len() {
                    filters.directories.push(args[i + 1].to_string());
                    i += 2;
                } else {
                    eprintln!("--directory requires an argument");
                    exit(1);
                }
            }
            "--status" | "-s" => {
                if i + 1 < args.len() {
                    match args[i + 1].as_str() {
                        "modified" => filters.statuses.push(ChangeStatus::Modified),
                        "added" => filters.statuses.push(ChangeStatus::Added),
                        "deleted" => filters.statuses.push(ChangeStatus::Deleted),
                        "untracked" => filters.statuses.push(ChangeStatus::Untracked),
                        _ => {
                            eprintln!("Unknown status: {}", args[i + 1]);
                            exit(1);
                        }
                    }
                    i += 2;
                } else {
                    eprintln!("--status requires an argument");
                    exit(1);
                }
            }
            "--impact" | "-i" => {
                if i + 1 < args.len() {
                    match args[i + 1].as_str() {
                        "code" => filters.impact_types.push(ImpactType::CodeImpacting),
                        "docs" => filters.impact_types.push(ImpactType::DocsOnly),
                        "config" => filters.impact_types.push(ImpactType::Config),
                        "tests" => filters.impact_types.push(ImpactType::Tests),
                        "build" => filters.impact_types.push(ImpactType::Build),
                        _ => {
                            eprintln!("Unknown impact type: {}", args[i + 1]);
                            exit(1);
                        }
                    }
                    i += 2;
                } else {
                    eprintln!("--impact requires an argument");
                    exit(1);
                }
            }
            "--exclude-extension" => {
                if i + 1 < args.len() {
                    filters.exclude_extensions.push(args[i + 1].trim_start_matches('.').to_string());
                    i += 2;
                } else {
                    eprintln!("--exclude-extension requires an argument");
                    exit(1);
                }
            }
            "--exclude-directory" => {
                if i + 1 < args.len() {
                    filters.exclude_directories.push(args[i + 1].to_string());
                    i += 2;
                } else {
                    eprintln!("--exclude-directory requires an argument");
                    exit(1);
                }
            }
            "--range" | "-r" => {
                if i + 1 < args.len() {
                    range = Some(&args[i + 1]);
                    i += 2;
                } else {
                    eprintln!("--range requires an argument");
                    exit(1);
                }
            }
            _ => {
                eprintln!("Unknown option: {}", args[i]);
                exit(1);
            }
        }
    }

    match ChangedFilesDetector::new() {
        Ok(detector) => {
            match detector.get_filtered(filters, range) {
                Ok(changed) => {
                    let output: Vec<_> = changed
                        .iter()
                        .map(|f| serde_json::json!({
                            "path": f.path.display().to_string(),
                            "status": format!("{:?}", f.status),
                            "impact": format!("{:?}", f.impact),
                        }))
                        .collect();
                    println!("{}", serde_json::to_string(&output).unwrap_or_else(|_| "[]".to_string()));
                }
                Err(e) => {
                    eprintln!("Error getting changed files: {}", e);
                    exit(1);
                }
            }
        }
        Err(e) => {
            eprintln!("Error initializing detector: {}", e);
            exit(1);
        }
    }
}

fn cmd_changed_files_impact() {
    let args: Vec<String> = env::args().collect();
    let range = args.get(2).map(|s| s.as_str());

    match ChangedFilesDetector::new() {
        Ok(detector) => {
            match detector.code_impact_paths(range) {
                Ok(paths) => {
                    let paths: Vec<String> = paths.iter().map(|p| p.display().to_string()).collect();
                    println!("{}", serde_json::to_string(&paths).unwrap_or_else(|_| "[]".to_string()));
                }
                Err(e) => {
                    eprintln!("Error getting code-impacting files: {}", e);
                    exit(1);
                }
            }
        }
        Err(e) => {
            eprintln!("Error initializing detector: {}", e);
            exit(1);
        }
    }
}

fn cmd_changed_files_deps() {
    let args: Vec<String> = env::args().collect();
    let range = args.get(2).map(|s| s.as_str());
    let show_dependents = args.contains(&"--dependents".to_string());

    match ChangedFilesDetector::new() {
        Ok(detector) => {
            match detector.get_changed_files(range) {
                Ok(changed) => {
                    let files: Vec<_> = changed.iter().map(|f| f.path.clone()).collect();

                    match detector.build_dependency_graph(&files) {
                        Ok(graph) => {
                            let mut result = serde_json::json!({});

                            for file in &files {
                                let deps = graph.get_transitive_deps(file);
                                let dep_strs: Vec<String> = deps.iter()
                                    .map(|p| p.display().to_string())
                                    .collect();

                                if show_dependents {
                                    let dependents = graph.get_transitive_dependents(file);
                                    let dep_strs: Vec<String> = dependents.iter()
                                        .map(|p| p.display().to_string())
                                        .collect();
                                    result[file.display().to_string()] = serde_json::json!({
                                        "depends_on": dep_strs,
                                        "depended_by": dep_strs,
                                    });
                                } else {
                                    result[file.display().to_string()] = serde_json::json!({
                                        "depends_on": dep_strs,
                                    });
                                }
                            }

                            println!("{}", serde_json::to_string(&result).unwrap_or_else(|_| "{}".to_string()));
                        }
                        Err(e) => {
                            eprintln!("Error building dependency graph: {}", e);
                            exit(1);
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error getting changed files: {}", e);
                    exit(1);
                }
            }
        }
        Err(e) => {
            eprintln!("Error initializing detector: {}", e);
            exit(1);
        }
    }
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

#[derive(Debug, Serialize, Deserialize)]
struct LearningData {
    pub hook_name: String,
    pub successes: u32,
    pub failures: u32,
    pub last_result: String, // "success", "failure"
    pub patterns: std::collections::HashMap<String, u32>,
}

fn get_learning_path(hook_name: &str) -> PathBuf {
    ensure_cache_dir().join(format!("learning-{}.json", hook_name))
}

fn cmd_learning_record() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 4 {
        eprintln!("Usage: thegent-hooks learning-record <hook_name> <result> [patterns...]");
        exit(1);
    }
    
    let hook_name = &args[2];
    let result = &args[3];
    let patterns = if args.len() > 4 { args[4..].to_vec() } else { Vec::new() };
    
    let path = get_learning_path(hook_name);
    let mut data = if path.exists() {
        fs::read_to_string(&path)
            .ok()
            .and_then(|c| serde_json::from_str::<LearningData>(&c).ok())
            .unwrap_or(LearningData {
                hook_name: hook_name.to_string(),
                successes: 0,
                failures: 0,
                last_result: "".to_string(),
                patterns: std::collections::HashMap::new(),
            })
    } else {
        LearningData {
            hook_name: hook_name.to_string(),
            successes: 0,
            failures: 0,
            last_result: "".to_string(),
            patterns: std::collections::HashMap::new(),
        }
    };
    
    if result == "success" {
        data.successes += 1;
    } else {
        data.failures += 1;
    }
    data.last_result = result.to_string();
    
    for pattern in patterns {
        *data.patterns.entry(pattern).or_default() += 1;
    }
    
    if let Ok(content) = serde_json::to_string(&data) {
        let _ = fs::write(&path, content);
    }
}

fn cmd_learning_should_skip() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks learning-should-skip <hook_name> [patterns...]");
        exit(1);
    }
    
    let hook_name = &args[2];
    let patterns = if args.len() > 3 { args[3..].to_vec() } else { Vec::new() };
    
    let path = get_learning_path(hook_name);
    if !path.exists() {
        println!("false");
        exit(0);
    }
    
    if let Ok(content) = fs::read_to_string(&path) {
        if let Ok(data) = serde_json::from_str::<LearningData>(&content) {
            // Very simple heuristic: skip if > 10 successes and 0 failures for all patterns
            if data.failures == 0 && data.successes > 10 {
                let mut all_match = true;
                for p in patterns {
                    if *data.patterns.get(&p).unwrap_or(&0) < 5 {
                        all_match = false;
                        break;
                    }
                }
                if all_match {
                    println!("true");
                    exit(0);
                }
            }
        }
    }
    
    println!("false");
    exit(0);
}

fn cmd_fr_ids() {
    let args: Vec<String> = env::args().collect();
    let fr_file = args.get(2).map(|s| s.as_str()).unwrap_or("FUNCTIONAL_REQUIREMENTS.md");
    let path = PathBuf::from(fr_file);
    
    if !path.exists() {
        eprintln!("FR file not found: {}", path.display());
        exit(1);
    }
    
    let content = fs::read_to_string(&path).unwrap_or_default();
    let re = regex::Regex::new(r"### (FR-[A-Z]+-[0-9]+)").unwrap();
    let mut ids = Vec::new();
    for cap in re.captures_iter(&content) {
        ids.push(cap[1].to_string());
    }
    
    println!("{}", serde_json::to_string(&ids).unwrap_or_else(|_| "[]".to_string()));
}

fn cmd_fr_index() {
    let args: Vec<String> = env::args().collect();
    let root = args.get(2).map(|s| s.as_str()).unwrap_or(".");
    let root_path = PathBuf::from(root);
    
    let re = regex::Regex::new(r"(FR-[A-Z]+-[0-9]+)").unwrap();
    let mut index: std::collections::HashMap<String, Vec<String>> = std::collections::HashMap::new();
    
    for entry in walkdir::WalkDir::new(root_path)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
    {
        let path = entry.path();
        let path_str = path.to_string_lossy().to_string();
        
        if path_str.contains("/.") || path_str.contains("/node_modules/") || path_str.contains("/dist/") || path_str.contains("/target/") {
            continue;
        }
        
        if let Ok(content) = fs::read_to_string(path) {
            for cap in re.captures_iter(&content) {
                let id = cap[1].to_string();
                index.entry(id).or_default().push(path_str.clone());
            }
        }
    }
    
    for paths in index.values_mut() {
        paths.sort();
        paths.dedup();
    }
    
    println!("{}", serde_json::to_string(&index).unwrap_or_else(|_| "{}".to_string()));
}

#[derive(Debug, Serialize, Deserialize)]
struct Progress {
    pub task_id: String,
    pub status: String,
    pub percent: f32,
    pub message: String,
}

fn cmd_progress() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks progress <task_id> [status] [percent] [message]");
        exit(1);
    }
    
    let task_id = &args[2];
    let status = args.get(3).cloned().unwrap_or_else(|| "in_progress".to_string());
    let percent = args.get(4).and_then(|v| v.parse().ok()).unwrap_or(0.0);
    let message = args.get(5).cloned().unwrap_or_default();
    
    let progress = Progress { task_id: task_id.to_string(), status, percent, message };
    let path = ensure_cache_dir().join(format!("progress-{}.json", task_id));
    
    if let Ok(content) = serde_json::to_string(&progress) {
        let _ = fs::write(path, content);
    }
    
    println!("{}", serde_json::to_string(&progress).unwrap_or_default());
}

#[derive(Debug, Serialize, Deserialize)]
struct HookReport {
    pub hook_name: String,
    pub session_id: String,
    pub start_time: DateTime<Utc>,
    pub end_time: DateTime<Utc>,
    pub status: String,
    pub exit_code: i32,
    pub issues: Vec<String>,
}

fn cmd_report() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: thegent-hooks report <hook_name> <session_id> <status> <exit_code> [issues...]");
        exit(1);
    }
    
    let hook_name = &args[2];
    let session_id = &args[3];
    let status = &args[4];
    let exit_code = args.get(5).and_then(|v| v.parse().ok()).unwrap_or(0);
    let issues = if args.len() > 6 { args[6..].to_vec() } else { Vec::new() };
    
    let report = HookReport {
        hook_name: hook_name.to_string(),
        session_id: session_id.to_string(),
        start_time: Utc::now() - Duration::from_secs(1),
        end_time: Utc::now(),
        status: status.to_string(),
        exit_code,
        issues,
    };
    
    let report_dir = PathBuf::from("docs/reports");
    fs::create_dir_all(&report_dir).unwrap_or_default();
    let path = report_dir.join(format!("report-{}-{}.json", hook_name, Utc::now().format("%Y-%m-%d")));
    
    if let Ok(content) = serde_json::to_string_pretty(&report) {
        let _ = fs::write(&path, content);
        println!("{}", path.display());
    }
}

fn cmd_prewarm() {
    println!("Prewarming caches...");
    // Mock implementation
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
        "cache-key" => cmd_cache_key(),
        "cache-check" => cmd_cache_check(),
        "cache-read" => cmd_cache_read(),
        "cache-write" => cmd_cache_write(),
        "git" => cmd_git(),
        "changed-files" => cmd_changed_files(),
        "changed-files-filter" => cmd_changed_files_filter(),
        "changed-files-impact" => cmd_changed_files_impact(),
        "changed-files-deps" => cmd_changed_files_deps(),
        "config-get" => cmd_config_get(),
        "breaker-check" => cmd_breaker_check(),
        "breaker-record" => cmd_breaker_record(),
        "breaker-reset" => cmd_breaker_reset(),
        "debounce" => cmd_debounce(),
        "incremental-check" => cmd_incremental_check(),
        "incremental-record" => cmd_incremental_record(),
        "file-hash" => cmd_file_hash(),
        "fr-ids" => cmd_fr_ids(),
        "fr-index" => cmd_fr_index(),
        "progress" => cmd_progress(),
        "report" => cmd_report(),
        "learning-record" => cmd_learning_record(),
        "learning-should-skip" => cmd_learning_should_skip(),
        _ => {
            eprintln!("Unknown subcommand: {}", args[1]);
            print_help();
            exit(1);
        }
    }
}
