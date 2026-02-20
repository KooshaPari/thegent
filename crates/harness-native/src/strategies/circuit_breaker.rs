use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::Command;

pub fn run(
    _harness_home: &Path,
    real_cmd: &Path,
    _cache_key: &str,
    _ttl: u64,
    _debounce_ms: u64,
    _error_ttl: u64,
    _breaker_threshold: u32,
    _breaker_window: u64,
    _breaker_cooldown: u64,
    args: &[&str],
) -> Result<i32, String> {
    // TODO: Circuit breaker logic
    let err = Command::new(real_cmd).args(args).exec();
    eprintln!("exec {:?} failed: {}", real_cmd, err);
    std::process::exit(127);
}
