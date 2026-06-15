use std::path::Path;
use std::thread;

use crate::os_exec::exec_replace;

pub fn run(real_cmd: &Path, debounce_ms: u64, args: &[&str]) -> Result<i32, String> {
    thread::sleep(std::time::Duration::from_millis(debounce_ms));
    exec_replace(real_cmd, args);
}
