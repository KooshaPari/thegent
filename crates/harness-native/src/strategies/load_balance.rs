use std::path::Path;

use crate::os_exec::exec_replace;

pub fn run(real_cmd: &Path, args: &[&str]) -> Result<i32, String> {
    exec_replace(real_cmd, args);
}
