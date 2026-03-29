use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::Command;
use std::thread;

pub fn run(real_cmd: &Path, debounce_ms: u64, args: &[&str]) -> Result<i32, String> {
    thread::sleep(std::time::Duration::from_millis(debounce_ms));
    let err = Command::new(real_cmd).args(args).exec();
    eprintln!("exec {:?} failed: {}", real_cmd, err);
    std::process::exit(127);
}
