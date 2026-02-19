//! Unified Runtime Dispatch Binary
//! Consolidates all tool shims (find, grep, git, cat, ls, du, node, npm, npx, python, pip)
//! with fork failure handling, circuit breaker, caching, and indexing.

use std::env;
use std::ffi::CString;
use std::fs;
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::Mutex;
use std::time::{Duration, Instant};

use sha2::{Digest, Sha256};
use base16ct::lower;
use nix::unistd::execv;

// Circuit breaker state
struct CircuitBreaker {
    failure_count: usize,
    last_failure: Option<Instant>,
    open: bool,
}

impl CircuitBreaker {
    fn new() -> Self {
        Self {
            failure_count: 0,
            last_failure: None,
            open: false,
        }
    }

    fn check(&mut self) -> bool {
        if self.open {
            if let Some(last) = self.last_failure {
                if last.elapsed() > Duration::from_secs(30) {
                    // Reset after 30 seconds
                    self.open = false;
                    self.failure_count = 0;
                    return true;
                }
            }
            return false; // Circuit still open
        }
        true
    }

    fn record_failure(&mut self) {
        self.failure_count += 1;
        self.last_failure = Some(Instant::now());
        if self.failure_count >= 3 {
            self.open = true;
            env::set_var("ULTRA_SHIM_FORK_FAILURES", self.failure_count.to_string());
        }
    }

    fn record_success(&mut self) {
        if self.failure_count > 0 {
            self.failure_count = 0;
        }
    }
}

use std::sync::OnceLock;

static CIRCUIT_BREAKER: OnceLock<Mutex<CircuitBreaker>> = OnceLock::new();

fn get_circuit_breaker() -> &'static Mutex<CircuitBreaker> {
    CIRCUIT_BREAKER.get_or_init(|| {
        Mutex::new(CircuitBreaker {
            failure_count: 0,
            last_failure: None,
            open: false,
        })
    })
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 1 {
        eprintln!("runtime-dispatch: no tool name");
        std::process::exit(127);
    }

    let self_path = &args[0];
    let tool = Path::new(self_path)
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("unknown")
        .to_string();

    let tool_args: Vec<String> = args[1..].to_vec();

    // Check bypass
    if env::var("BYPASS_ULTRA_SHIM").unwrap_or_default() == "1" {
        if let Some(real_bin) = resolve_real_safe(&tool, self_path) {
            exec_real(real_bin, &tool_args);
        }
        // Fallback: try system PATH
        exec_real(tool.clone(), &tool_args);
        std::process::exit(127);
    }

    // Agent detection
    let is_agent = env::var("AGENT_ID").is_ok()
        || env::var("SHARECLI_AGENT").is_ok()
        || env::var("SHARECLI_AGENT_CONTEXT").is_ok();

    // Dispatch to handler
    match tool.as_str() {
        "git" => handle_git(&tool_args, self_path),
        "grep" => handle_grep(&tool_args, is_agent, self_path),
        "rg" => handle_rg(&tool_args, self_path),
        "ls" => handle_ls(&tool_args, is_agent, self_path),
        "find" => handle_find(&tool_args, is_agent, self_path),
        "du" => handle_du(&tool_args, is_agent, self_path),
        "cat" => handle_cat(&tool_args, self_path),
        "node" => handle_node(&tool_args, self_path),
        "npm" => handle_npm(&tool_args, self_path),
        "npx" => handle_npx(&tool_args, self_path),
        "python" | "python3" => handle_python(&tool_args, self_path),
        "pip" | "pip3" => handle_pip(&tool_args, &tool, self_path),
        _ => {
            // Fallback: resolve and execute real binary
            if let Some(real_bin) = resolve_real_safe(&tool, self_path) {
                exec_real(real_bin, &tool_args);
            }
            std::process::exit(127);
        }
    }
}

// Tool Handlers

fn handle_git(args: &[String], self_path: &str) {
    if env::var("USE_FAST_GIT").unwrap_or_default() == "0" {
        if let Some(real_bin) = resolve_real_safe("git", self_path) {
            exec_real(real_bin, args);
        }
        return;
    }

    if let Some(cmd) = args.first() {
        let read_only_commands = [
            "status", "diff", "rev-parse", "ls-files", "log", "show",
            "name-rev", "symbolic-ref", "branch", "tag", "remote", "config",
            "ls-tree", "cat-file", "describe",
        ];

        if read_only_commands.contains(&cmd.as_str()) {
            if try_cache("git", args) {
                return;
            }

            let mut target = resolve_real_safe("git", self_path).unwrap_or_else(|| "git".to_string());
            if let Ok(gix) = which::which("gix") {
                target = gix.to_string_lossy().to_string();
            }

            run_and_cache_safe(&target, args, "git", args);
            return;
        }
    }

    if let Some(real_bin) = resolve_real_safe("git", self_path) {
        exec_real(real_bin, args);
    }
}

fn handle_grep(args: &[String], is_agent: bool, self_path: &str) {
    if env::var("USE_FAST_GREP").unwrap_or_default() == "0" {
        if let Some(real_bin) = resolve_real_safe("grep", self_path) {
            exec_real(real_bin, args);
        }
        return;
    }

    let mut is_recursive = false;
    let mut new_args = Vec::new();

    for arg in args {
        // Detect recursion
        if arg == "-r" || arg == "-R" || arg == "--recursive" {
            is_recursive = true;
            continue;
        }

        // Handle combined flags
        let mut processed = arg.clone();
        if arg.starts_with('-') && !arg.starts_with("--") {
            if arg.contains('r') || arg.contains('R') {
                is_recursive = true;
                processed = processed.replace('r', "").replace('R', "");
            }
            if arg.contains('E') {
                processed = processed.replace('E', "");
            }
        }

        if arg != "-" && arg != "--extended-regexp" && !processed.is_empty() {
            new_args.push(processed);
        }
    }

    // Safety check
    if is_recursive && is_agent && contains_any(args, "trace") {
        eprintln!("\x1b[31m[SAFETY] Recursive grep blocked in 'trace/' for agents.\x1b[0m");
        std::process::exit(1);
    }

    // Try rg
    let cmd = if which::which("rg").is_ok() {
        "rg"
    } else {
        "grep"
    };

    if cmd == "grep" {
        new_args = args.to_vec();
    }

    if try_cache("grep", args) {
        return;
    }

    let target = resolve_real_safe(cmd, self_path).unwrap_or_else(|| cmd.to_string());
    run_and_cache_safe(&target, &new_args, "grep", args);
}

fn handle_rg(args: &[String], self_path: &str) {
    let mut new_args = Vec::new();
    let mut i = 0;
    while i < args.len() {
        let arg = &args[i];
        if (arg == "-E" || arg == "--encoding") && i + 1 < args.len() {
            let next = &args[i + 1];
            // If it looks like a regex, treat as pattern not encoding
            if next.contains('|') || next.contains('=') || next.contains('(') {
                new_args.push("-e".to_string());
                new_args.push(next.clone());
                i += 2;
                continue;
            }
        }
        new_args.push(arg.clone());
        i += 1;
    }

    if let Some(real_bin) = resolve_real_safe("rg", self_path) {
        exec_real(real_bin, &new_args);
    }
}

fn handle_ls(args: &[String], is_agent: bool, self_path: &str) {
    if env::var("USE_FAST_LS").unwrap_or_default() == "0" {
        if let Some(real_bin) = resolve_real_safe("ls", self_path) {
            exec_real(real_bin, args);
        }
        return;
    }

    let is_recursive = args.iter().any(|a| a == "-R" || a == "--recursive");

    if is_recursive {
        if is_agent && contains_any(args, "trace") {
            eprintln!("\x1b[31m[SAFETY] Recursive walk blocked in 'trace/' for agents.\x1b[0m");
            std::process::exit(1);
        }
        if count_items(".") > 10000 {
            eprintln!("\x1b[33m[SAFETY] Massive directory. Skipping recursion.\x1b[0m");
            std::process::exit(1);
        }
    }

    // Use eza for TTY, plain ls for agents/pipes
    #[cfg(unix)]
    let stdout_is_tty = unsafe { libc::isatty(libc::STDOUT_FILENO) != 0 };
    #[cfg(not(unix))]
    let stdout_is_tty = false;
    let use_eza = !is_agent && stdout_is_tty;

    let cmd = if use_eza && which::which("eza").is_ok() {
        "eza"
    } else {
        "ls"
    };

    let mut final_args = args.to_vec();
    if cmd == "eza" && !args.iter().any(|a| a.contains("--icons")) {
        final_args.insert(0, "--icons".to_string());
        final_args.insert(1, "--git".to_string());
        final_args.insert(2, "--group-directories-first".to_string());
    }

    if let Some(real_bin) = resolve_real_safe(cmd, self_path) {
        exec_real(real_bin, &final_args);
    }
}

fn handle_find(args: &[String], is_agent: bool, self_path: &str) {
    if env::var("USE_FAST_FIND").unwrap_or_default() == "0" {
        if let Some(real_bin) = resolve_real_safe("find", self_path) {
            exec_real(real_bin, args);
        }
        return;
    }

    if is_agent && contains_any(args, "trace") {
        eprintln!("\x1b[31m[SAFETY] Recursive find blocked in 'trace/' for agents.\x1b[0m");
        std::process::exit(1);
    }

    // Try fd
    if let Ok(fd_path) = which::which("fd") {
        let mut can_use_fd = true;
        let mut fd_args = Vec::new();
        let mut dir = ".";

        let mut i = 0;
        while i < args.len() {
            let arg = &args[i];
            if !arg.starts_with('-') {
                if Path::new(arg).is_dir() && dir == "." {
                    dir = arg;
                } else if dir == "." {
                    dir = arg;
                } else {
                    can_use_fd = false;
                    break;
                }
            } else {
                match arg.as_str() {
                    "-name" => {
                        if i + 1 < args.len() {
                            fd_args.push("--glob".to_string());
                            fd_args.push(args[i + 1].clone());
                            i += 1;
                        }
                    }
                    "-type" => {
                        if i + 1 < args.len() {
                            fd_args.push("--type".to_string());
                            fd_args.push(args[i + 1].clone());
                            i += 1;
                        }
                    }
                    "-maxdepth" => {
                        if i + 1 < args.len() {
                            fd_args.push("--max-depth".to_string());
                            fd_args.push(args[i + 1].clone());
                            i += 1;
                        }
                    }
                    "-print" | "-print0" => {
                        // ignore
                    }
                    _ => {
                        can_use_fd = false;
                        break;
                    }
                }
            }
            i += 1;
        }

        if can_use_fd {
            if try_cache("find", args) {
                return;
            }

            // Try index for simple name patterns
            let name_pattern = args
                .iter()
                .position(|a| a == "-name")
                .and_then(|i| args.get(i + 1))
                .cloned();

            if let Some(pattern) = name_pattern {
                if try_index_safe(&dir, &pattern) {
                    return;
                }
            }

            if fd_args.is_empty() {
                fd_args.push(".".to_string());
            }
            fd_args.push(dir.to_string());

            run_and_cache_safe(&fd_path.to_string_lossy(), &fd_args, "find", args);
            return;
        }
    }

    if let Some(real_bin) = resolve_real_safe("find", self_path) {
        exec_real(real_bin, args);
    }
}

fn handle_cat(args: &[String], self_path: &str) {
    if env::var("USE_FAST_CAT").unwrap_or_default() == "0" {
        if let Some(real_bin) = resolve_real_safe("cat", self_path) {
            exec_real(real_bin, args);
        }
        return;
    }

    let cmd = if which::which("bat").is_ok() {
        "bat"
    } else {
        "cat"
    };

    let mut final_args = args.to_vec();
    if cmd == "bat" && !args.iter().any(|a| a.contains("--paging")) {
        final_args.insert(0, "--paging=never".to_string());
    }

    if let Some(real_bin) = resolve_real_safe(cmd, self_path) {
        exec_real(real_bin, &final_args);
    }
}

fn handle_du(args: &[String], is_agent: bool, self_path: &str) {
    if env::var("USE_FAST_DU").unwrap_or_default() == "0" {
        if let Some(real_bin) = resolve_real_safe("du", self_path) {
            exec_real(real_bin, args);
        }
        return;
    }

    let is_heavy = args.iter().any(|a| a == "-a" || a == "--all" || a == "-h");

    if is_heavy && is_agent && contains_any(args, "trace") {
        eprintln!("\x1b[31m[SAFETY] Recursive du blocked in 'trace/' for agents.\x1b[0m");
        std::process::exit(1);
    }

    let cmd = if which::which("dust").is_ok() {
        "dust"
    } else {
        "du"
    };

    if let Some(real_bin) = resolve_real_safe(cmd, self_path) {
        exec_real(real_bin, args);
    }
}

fn handle_node(args: &[String], self_path: &str) {
    if env::var("USE_BUN_TOOLS").unwrap_or_default() != "0" {
        if let Ok(bun) = which::which("bun") {
            let bun_args = args_to_bun(args);
            exec_real(bun.to_string_lossy().to_string(), &bun_args);
            return;
        }
    }

    if let Some(real_bin) = resolve_real_safe("node", self_path) {
        exec_real(real_bin, args);
    }
}

fn handle_npm(args: &[String], self_path: &str) {
    if env::var("USE_BUN_TOOLS").unwrap_or_default() != "0" {
        if let Ok(bun) = which::which("bun") {
            exec_real(bun.to_string_lossy().to_string(), args);
            return;
        }
    }

    if let Some(real_bin) = resolve_real_safe("npm", self_path) {
        exec_real(real_bin, args);
    }
}

fn handle_npx(args: &[String], self_path: &str) {
    if env::var("USE_BUN_TOOLS").unwrap_or_default() != "0" {
        if let Ok(bunx) = which::which("bunx") {
            exec_real(bunx.to_string_lossy().to_string(), args);
            return;
        }
    }

    if let Some(real_bin) = resolve_real_safe("npx", self_path) {
        exec_real(real_bin, args);
    }
}

fn handle_python(args: &[String], self_path: &str) {
    if env::var("USE_FAST_PYTHON").unwrap_or_default() != "0" {
        if let Ok(pypy) = which::which("pypy3") {
            exec_real(pypy.to_string_lossy().to_string(), args);
            return;
        }
    }

    if let Some(real_bin) = resolve_real_safe("python3", self_path) {
        exec_real(real_bin, args);
    }
}

fn handle_pip(args: &[String], tool: &str, self_path: &str) {
    if env::var("USE_FAST_TOOLS").unwrap_or_default() != "0" {
        if let Ok(uv) = which::which("uv") {
            let mut pip_args = vec!["pip".to_string()];
            pip_args.extend_from_slice(args);
            exec_real(uv.to_string_lossy().to_string(), &pip_args);
            return;
        }
    }

    if let Some(real_bin) = resolve_real_safe(tool, self_path) {
        exec_real(real_bin, args);
    }
}

// Helper Functions

fn args_to_bun(args: &[String]) -> Vec<String> {
    if args.is_empty() {
        return args.to_vec();
    }
    let head = &args[0];
    if head == "-v" || head == "--version" {
        return vec!["--version".to_string()];
    }
    if head == "-h" || head == "--help" {
        return vec!["--help".to_string()];
    }
    if head.starts_with('-') {
        return args.to_vec();
    }
    let mut result = vec!["run".to_string()];
    result.extend_from_slice(args);
    result
}

fn contains_any(args: &[String], pattern: &str) -> bool {
    args.iter().any(|a| a.contains(pattern))
        || env::current_dir()
            .map(|cwd| cwd.to_string_lossy().contains(pattern))
            .unwrap_or(false)
}

fn count_items(dir: &str) -> usize {
    fs::read_dir(dir)
        .map(|entries| entries.count())
        .unwrap_or(0)
}

fn is_self_binary(candidate: &str, self_path: &str) -> bool {
    if candidate.is_empty() || self_path.is_empty() {
        return false;
    }

    let candidate_file = Path::new(candidate).file_name().and_then(|n| n.to_str());
    let self_file = Path::new(self_path).file_name().and_then(|n| n.to_str());

    if candidate_file == self_file {
        return true;
    }

    matches!(
        candidate_file,
        Some("runtime-dispatch" | "ultra-shim" | "runtime-dispatch.exe" | "ultra-shim.exe")
    )
}

fn resolve_real_safe(name: &str, self_path: &str) -> Option<String> {
    // Use safe PATH (exclude project directories)
    let safe_paths = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
    ];

    for p in &safe_paths {
        let full = Path::new(p).join(name);
        if let Ok(metadata) = fs::metadata(&full) {
            if metadata.is_dir() {
                continue;
            }

            if !metadata.is_file() {
                continue;
            }

            // Check if executable or has shebang
            let mode = metadata.permissions();
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                if mode.mode() & 0o111 == 0 {
                    if !has_shebang(&full) {
                        continue;
                    }
                }
            }

            if is_self_binary(&full.to_string_lossy(), self_path) {
                continue;
            }

            return Some(full.to_string_lossy().to_string());
        }
    }

    // Fallback: try system PATH (but filter carefully)
    if let Ok(path) = which::which(name) {
        let path_str = path.to_string_lossy().to_string();
        if !is_self_binary(&path_str, self_path) {
            if let Ok(metadata) = fs::metadata(&path) {
                if metadata.is_file() {
                    #[cfg(unix)]
                    {
                        use std::os::unix::fs::PermissionsExt;
                        let mode = metadata.permissions();
                        if mode.mode() & 0o111 != 0 || has_shebang(&path) {
                            return Some(path_str);
                        }
                    }
                    #[cfg(not(unix))]
                    {
                        return Some(path_str);
                    }
                }
            }
        }
    }

    None
}

fn has_shebang(path: &Path) -> bool {
    if let Ok(mut file) = fs::File::open(path) {
        let mut buf = [0u8; 2];
        if file.read_exact(&mut buf).is_ok() && buf == [b'#', b'!'] {
            return true;
        }
    }
    false
}

fn exec_real(path: String, args: &[String]) -> ! {
    let c_path = CString::new(path.clone()).unwrap();
    let mut c_args: Vec<CString> = vec![c_path.clone()];
    c_args.extend(args.iter().map(|a| CString::new(a.clone()).unwrap()));
    let c_args_ptrs: Vec<*const libc::c_char> = c_args.iter().map(|a| a.as_ptr()).collect();

    match execv(&c_path, &c_args_ptrs) {
        Ok(_) => unreachable!(),
        Err(e) => {
            eprintln!("runtime-dispatch: exec failed: {}", e);
            std::process::exit(127);
        }
    }
}

// Caching Logic

fn get_cache_dir() -> PathBuf {
    let home = env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
    let dir = Path::new(&home).join(".cache").join("thegent").join("tool-cache");
    fs::create_dir_all(&dir).ok();
    dir
}

fn get_cache_key(tool: &str, args: &[String]) -> String {
    let cwd = env::current_dir()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_default();
    let data = format!("{}{}{}", tool, args.join(" "), cwd);
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    let hash = hasher.finalize();
    let mut buf = vec![0u8; base16ct::encoded_len(hash.len())];
    let encoded = lower::encode(&hash, &mut buf).unwrap();
    String::from_utf8_lossy(encoded).to_string()
}

fn try_cache(tool: &str, args: &[String]) -> bool {
    if env::var("USE_CACHE").unwrap_or_default() == "0" {
        return false;
    }

    let key = get_cache_key(tool, args);
    let cache_path = get_cache_dir().join(key);

    if let Ok(metadata) = fs::metadata(&cache_path) {
        let ttl = env::var("CACHE_TTL")
            .unwrap_or_else(|_| "60".to_string())
            .parse::<u64>()
            .unwrap_or(60);

        if let Ok(modified) = metadata.modified() {
            if let Ok(elapsed) = modified.elapsed() {
                if elapsed.as_secs() <= ttl {
                    if let Ok(content) = fs::read(&cache_path) {
                        io::stdout().write_all(&content).ok();
                        return true;
                    }
                }
            }
        }
    }

    false
}

fn save_cache(tool: &str, args: &[String], output: &[u8]) {
    let key = get_cache_key(tool, args);
    let cache_path = get_cache_dir().join(key);
    fs::write(cache_path, output).ok();
}

fn run_and_cache_safe(path: &str, args: &[String], tool: &str, original_args: &[String]) -> ! {
    let mut cb = get_circuit_breaker().lock().unwrap();

    // Check circuit breaker
    if !cb.check() {
        drop(cb);
        // Circuit open: bypass caching, use direct exec
        exec_real(path.to_string(), args);
    }

    drop(cb);

    // Try fork (for caching)
    let output = match Command::new(path).args(args).output() {
        Ok(output) => output,
        Err(e) => {
            let err_str = e.to_string();
            if err_str.contains("fork")
                || err_str.contains("resource temporarily unavailable")
                || err_str.contains("too many processes")
            {
                // Fork failed: update circuit breaker
                let mut cb = get_circuit_breaker().lock().unwrap();
                cb.record_failure();
                drop(cb);

                // Fall back to direct exec (no fork, no caching)
                exec_real(path.to_string(), args);
            }

            // Other errors
            io::stderr().write_all(err_str.as_bytes()).ok();
            std::process::exit(1);
        }
    };

    // Success: record success and cache
    let mut cb = get_circuit_breaker().lock().unwrap();
    cb.record_success();
    drop(cb);

    if output.status.success() && !output.stdout.is_empty() {
        save_cache(tool, original_args, &output.stdout);
    }

    io::stdout().write_all(&output.stdout).ok();
    io::stderr().write_all(&output.stderr).ok();

    std::process::exit(
        output
            .status
            .code()
            .unwrap_or(if output.status.success() { 0 } else { 1 }),
    );
}

// Indexing Logic

fn get_index_file() -> PathBuf {
    let home = env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
    Path::new(&home)
        .join(".cache")
        .join("thegent")
        .join("file-index")
}

fn try_index_safe(dir: &str, pattern: &str) -> bool {
    if env::var("USE_INDEX").unwrap_or_default() == "0" {
        return false;
    }

    let indexPath = get_index_file();
    if let Ok(metadata) = fs::metadata(&indexPath) {
        if let Ok(modified) = metadata.modified() {
            if let Ok(elapsed) = modified.elapsed() {
                if elapsed.as_secs() > 300 {
                    // TTL: 5 minutes
                    return false;
                }
            }
        }
    } else {
        return false;
    }

    if pattern.is_empty() {
        return false;
    }

    // Normalize pattern for grep
    let grep_pattern = pattern.replace('*', ".*");

    // Use absolute path to real grep (avoid shim interception)
    let grep_path = resolve_real_safe("grep", "")
        .unwrap_or_else(|| "/usr/bin/grep".to_string());

    let output = if dir != "." {
        Command::new("sh")
            .arg("-c")
            .arg(format!(
                "{} -E '{}' {} | {} '^{}'",
                grep_path, grep_pattern, indexPath.display(), grep_path, dir
            ))
            .output()
    } else {
        Command::new(&grep_path)
            .arg("-E")
            .arg(&grep_pattern)
            .arg(&indexPath)
            .output()
    };

    if let Ok(output) = output {
        if output.status.success() && !output.stdout.is_empty() {
            io::stdout().write_all(&output.stdout).ok();
            return true;
        }
    }

    false
}
