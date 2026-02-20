use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::Command;

pub fn run(
    _harness_home: &Path,
    real_cmd: &Path,
    _cmd_name: &str,
    _subcmd: &str,
    _cache_key: &str,
    _ttl: u64,
    _debounce_ms: u64,
    _error_ttl: u64,
    args: &[&str],
) -> Result<i32, String> {
    // TODO: Proactive warmup
    let err = Command::new(real_cmd).args(args).exec();
    eprintln!("exec {:?} failed: {}", real_cmd, err);
    std::process::exit(127);
}
