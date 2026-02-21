use regex::Regex;
use std::fs;
use std::path::{Path, PathBuf};

fn should_skip_dir(name: &str) -> bool {
    matches!(name, "node_modules" | ".git" | ".venv" | "target" | "__pycache__")
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
                if matches!(ext, "env" | "json" | "py" | "js" | "ts" | "yaml" | "yml" | "toml" | "xml")
                {
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

pub(crate) fn count_todos(dir: &Path) -> usize {
    let mut count = 0;
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
                if should_skip_dir(name) {
                    continue;
                }
                count += count_todos(&path);
            } else if path.is_file() {
                let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                if matches!(ext, "py" | "js" | "ts" | "rs" | "go" | "sh") {
                    if let Ok(content) = fs::read_to_string(&path) {
                        count += content.matches("TODO").count();
                        count += content.matches("FIXME").count();
                    }
                }
            }
        }
    }
    count
}
