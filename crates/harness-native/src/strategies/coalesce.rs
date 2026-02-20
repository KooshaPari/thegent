use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::Command;

use crate::strategies::cache;

pub fn exec_direct(cmd: &Path, args: &[&str]) -> ! {
    let err = Command::new(cmd).args(args).exec();
    eprintln!("exec {:?} failed: {}", cmd, err);
    std::process::exit(127);
}

pub fn run(
    _harness_home: &Path,
    real_cmd: &Path,
    _cache_key: &str,
    _ttl: u64,
    _debounce_ms: u64,
    _error_ttl: u64,
    _stale_threshold: u64,
    args: &[&str],
) -> Result<i32, String> {
    // TODO: Check cache, debounce, execute
    exec_direct(real_cmd, args);
}
