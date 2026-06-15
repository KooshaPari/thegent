use std::path::Path;

use crate::os_exec::exec_replace;

pub fn exec_direct(cmd: &Path, args: &[&str]) -> ! {
    exec_replace(cmd, args);
}

pub fn run(real_cmd: &Path, args: &[&str]) -> Result<i32, String> {
    exec_direct(real_cmd, args);
}
