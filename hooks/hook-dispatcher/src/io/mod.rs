use std::env;
use std::path::PathBuf;

pub(crate) fn find_in_path(executable: &str) -> Option<String> {
    if let Ok(path_var) = env::var("PATH") {
        for path in env::split_paths(&path_var) {
            let exe_path = path.join(executable);
            if exe_path.is_file() {
                return Some(exe_path.to_string_lossy().to_string());
            }
            if cfg!(target_os = "windows") {
                let with_exe = path.join(format!("{}.exe", executable));
                if with_exe.is_file() {
                    return Some(with_exe.to_string_lossy().to_string());
                }
            }
        }
    }
    None
}

pub(crate) fn first_available(names: &[&str]) -> String {
    for name in names {
        if let Some(path) = find_in_path(name) {
            return path;
        }
    }
    String::new()
}

pub(crate) fn resolve_hooks_dir() -> PathBuf {
    if let Ok(dir) = env::var("HOOKS_DIR") {
        return PathBuf::from(dir);
    }

    if let Ok(exe) = env::current_exe() {
        let mut dir = exe.parent().map(|p| p.to_path_buf());
        for _ in 0..5 {
            if let Some(ref d) = dir {
                if d.join("pretool-dispatcher.sh").exists() || d.join("doc-location-guard.sh").exists()
                {
                    return d.clone();
                }
                dir = d.parent().map(|p| p.to_path_buf());
            } else {
                break;
            }
        }
    }

    let home = env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
    PathBuf::from(format!("{home}/.claude/hooks"))
}
