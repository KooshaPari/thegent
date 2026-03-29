use regex::Regex;
use std::fs;
use std::path::{Path, PathBuf};

fn should_skip_dir(name: &str) -> bool {
    matches!(
        name,
        "node_modules" | ".git" | ".venv" | "target" | "__pycache__"
    )
}

fn should_skip_dir_with_dist(name: &str) -> bool {
    should_skip_dir(name) || name == "dist"
}

pub(crate) fn count_ai_slop(dir: &Path) -> usize {
    let mut count = 0;
    let slop_patterns = [
        "As an AI",
        "I cannot",
        "I apologize",
        "I'm sorry, but",
        "As a language model",
    ];

    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if should_skip_dir(name) {
                    continue;
                }
                count += count_ai_slop(&path);
            } else if path.is_file() {
                let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                if matches!(ext, "py" | "js" | "ts" | "rs" | "go" | "md") {
                    if let Ok(content) = fs::read_to_string(&path) {
                        for p in &slop_patterns {
                            count += content.matches(p).count();
                        }
                    }
                }
            }
        }
    }

    count
}

pub(crate) fn scan_secrets(dir: &Path, secret_regexes: &[Regex]) -> usize {
    let mut count = 0;

    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if should_skip_dir_with_dist(name) {
                    continue;
                }
                count += scan_secrets(&path, secret_regexes);
            } else if path.is_file() {
                let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                if matches!(
                    ext,
                    "env" | "json" | "py" | "js" | "ts" | "yaml" | "yml" | "toml" | "xml"
                ) {
                    if let Ok(content) = fs::read_to_string(&path) {
                        for regex in secret_regexes {
                            if regex.is_match(&content) {
                                count += 1;
                                break;
                            }
                        }
                    }
                }
            }
        }
    }

    count
}

pub(crate) fn scan_deep_nesting(dir: &Path, limit: usize) -> Vec<PathBuf> {
    let mut results = Vec::new();

    fn recurse(dir: &Path, depth: usize, limit: usize, results: &mut Vec<PathBuf>) {
        if depth > limit {
            results.push(dir.to_path_buf());
            return;
        }
        if let Ok(entries) = fs::read_dir(dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_dir() {
                    let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                    if should_skip_dir(name) {
                        continue;
                    }
                    recurse(&path, depth + 1, limit, results);
                }
            }
        }
    }

    recurse(dir, 0, limit, &mut results);
    results
}

pub(crate) fn scan_large_files(dir: &Path, large_files: &mut Vec<PathBuf>, threshold: u64) {
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if should_skip_dir(name) {
                    continue;
                }
                scan_large_files(&path, large_files, threshold);
            } else if path.is_file() {
                if let Ok(metadata) = entry.metadata() {
                    if metadata.len() > threshold {
                        large_files.push(path);
                    }
                }
            }
        }
    }
}

pub(crate) fn count_todos(dir: &Path) -> std::io::Result<usize> {
    fn recurse(path: &Path, count: &mut usize, todo_re: &Regex) -> std::io::Result<()> {
        let entries = fs::read_dir(path)?;
        for entry in entries {
            let entry = entry?;
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if should_skip_dir(name) {
                    continue;
                }
                recurse(&path, count, todo_re)?;
            } else if path.is_file() {
                let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                if matches!(ext, "py" | "js" | "ts" | "rs" | "go" | "sh") {
                    let content = fs::read_to_string(&path)?;
                    *count += todo_re.find_iter(&content).count();
                }
            }
        }
        Ok(())
    }

    let mut count = 0;
    let todo_re = Regex::new(r"\b(TODO|FIXME)\b").unwrap();
    recurse(&dir, &mut count, &todo_re)?;
    Ok(count)
}

#[cfg(test)]
mod tests {
    use super::count_todos;
    use std::fs::{self, File};
    use std::io::Write;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn tmp_root(prefix: &str) -> std::path::PathBuf {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let base = std::env::temp_dir().join(format!("thegent-governance-fs-{prefix}-{unique}"));
        fs::create_dir_all(&base).unwrap();
        base
    }

    #[test]
    fn count_todos_counts_keywords_across_supported_files() {
        let root = tmp_root("count");
        fs::create_dir(root.join("nested")).unwrap();
        let mut file = File::create(root.join("root.rs")).unwrap();
        writeln!(file, "// TODO: top-level").unwrap();
        writeln!(file, "let _ = \"FIXME\";").unwrap();
        writeln!(file, "# FIXME: nested marker").unwrap();
        let mut nested = File::create(root.join("nested").join("inner.py")).unwrap();
        writeln!(nested, "TODO").unwrap();
        writeln!(nested, "TODO TODO FIXME").unwrap();

        assert_eq!(count_todos(&root).unwrap(), 7);
        fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn count_todos_is_empty_for_unsupported_extensions() {
        let root = tmp_root("unsupported");
        let mut file = File::create(root.join("ignore.txt")).unwrap();
        writeln!(file, "TODO FIXME TODO").unwrap();

        assert_eq!(count_todos(&root).unwrap(), 0);
        fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn count_todos_ignores_markers_without_boundaries() {
        let root = tmp_root("embedded");
        let mut file = File::create(root.join("weird.py")).unwrap();
        writeln!(file, "TODO_LIST FIXME_CASE TODOFIXME FIXMEs").unwrap();

        assert_eq!(count_todos(&root).unwrap(), 0);
        fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn count_todos_returns_io_error_for_missing_root() {
        let missing = std::env::temp_dir().join(format!(
            "thegent-governance-fs-missing-{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));

        assert!(count_todos(&missing).is_err());
    }
}
