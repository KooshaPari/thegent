//! File Watcher Module
//!
//! Watches for file changes and triggers task re-execution.

use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::Duration;

use notify::{Config, Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher as NotifyWatcher};
use parking_lot::RwLock;
use tokio::sync::mpsc;

pub type FileState = Arc<RwLock<std::collections::HashMap<PathBuf, std::time::Instant>>>;
pub type ChangeCallback = Arc<dyn Fn(Vec<PathBuf>) + Send + Sync>;

/// File system watcher with debouncing
pub struct FileWatcher {
    paths: Vec<PathBuf>,
    debounce_ms: u64,
    ignore_patterns: Vec<String>,
    file_state: FileState,
    callback: Option<ChangeCallback>,
}

impl FileWatcher {
    pub fn new(paths: Vec<PathBuf>) -> Self {
        Self {
            paths,
            debounce_ms: 100,
            ignore_patterns: vec![
                String::from("*.git/*"),
                String::from("*.tmp"),
                String::from("*.swp"),
                String::from("*/target/*"),
                String::from("*/node_modules/*"),
                String::from(".DS_Store"),
            ],
            file_state: Arc::new(RwLock::new(std::collections::HashMap::new())),
            callback: None,
        }
    }

    pub fn debounce(mut self, ms: u64) -> Self {
        self.debounce_ms = ms;
        self
    }

    pub fn ignore_patterns(mut self, patterns: Vec<String>) -> Self {
        self.ignore_patterns.extend(patterns);
        self
    }

    pub fn on_change<C>(mut self, callback: C) -> Self
    where
        C: Fn(Vec<PathBuf>) + Send + Sync + 'static,
    {
        self.callback = Some(Arc::new(callback));
        self
    }

    fn should_ignore(&self, path: &Path) -> bool {
        let path_str = path.to_string_lossy();

        for pattern in &self.ignore_patterns {
            if matches_glob(path_str.as_ref(), pattern) {
                return true;
            }
        }

        false
    }

    pub async fn run(mut self) -> crate::Result<()> {
        let (tx, mut rx) = mpsc::channel::<Event>(100);

        let watcher_tx = tx.clone();
        let mut watcher: RecommendedWatcher = NotifyWatcher::new(
            move |res: std::result::Result<Event, notify::Error>| {
                if let Ok(event) = res {
                    let _ = watcher_tx.blocking_send(event);
                }
            },
            Config::default().with_poll_interval(Duration::from_millis(self.debounce_ms)),
        ).map_err(|e| crate::ForgeError::WatcherError(e.to_string()))?;

        for path in &self.paths {
            watcher.watch(path, RecursiveMode::Recursive)
                .map_err(|e| crate::ForgeError::WatcherError(e.to_string()))?;
            tracing::info!("Watching: {}", path.display());
        }

        tracing::info!("File watcher started, press Ctrl+C to stop");

        let mut debounce_timer: Option<tokio::task::JoinHandle<()>> = None;
        let mut pending_changes: Vec<PathBuf> = Vec::new();

        while let Some(event) = rx.recv().await {
            let paths = self.process_event(event);

            if paths.is_empty() {
                continue;
            }

            {
                let mut state = self.file_state.write();
                for path in &paths {
                    state.insert(path.clone(), std::time::Instant::now());
                }
            }

            pending_changes.extend(paths);

            if let Some(handle) = debounce_timer.take() {
                handle.abort();
            }

            let paths_clone = pending_changes.clone();
            let callback = self.callback.clone();
            let debounce_ms = self.debounce_ms;

            debounce_timer = Some(tokio::spawn(async move {
                tokio::time::sleep(Duration::from_millis(debounce_ms)).await;

                if let Some(cb) = callback {
                    cb(paths_clone);
                }
            }));
        }

        Ok(())
    }

    fn process_event(&self, event: Event) -> Vec<PathBuf> {
        let mut paths = Vec::new();

        match event.kind {
            EventKind::Create(_) | EventKind::Modify(_) | EventKind::Remove(_) => {
                for path in event.paths {
                    if !self.should_ignore(&path) {
                        paths.push(path);
                    }
                }
            }
            _ => {}
        }

        paths
    }

    pub fn file_state(&self) -> FileState {
        Arc::clone(&self.file_state)
    }
}

fn matches_glob(path: &str, pattern: &str) -> bool {
    if pattern.starts_with("*.") {
        let ext = &pattern[2..];
        return path.ends_with(&format!(".{}", ext)) || glob_match(&pattern[1..], path);
    }

    if pattern.starts_with("*/") {
        let suffix = &pattern[2..];
        return path.contains(suffix);
    }

    if pattern.starts_with("*") {
        let suffix = &pattern[1..];
        return path.ends_with(suffix);
    }

    glob_match(pattern, path)
}

fn glob_match(pattern: &str, path: &str) -> bool {
    let mut pattern_chars = pattern.chars().peekable();
    let mut path_chars = path.chars().peekable();

    while pattern_chars.peek().is_some() || path_chars.peek().is_some() {
        match (pattern_chars.peek(), path_chars.peek()) {
            (Some('*'), _) => {
                pattern_chars.next();
                if pattern_chars.peek().is_none() {
                    return true;
                }
                while path_chars.peek().is_some() {
                    if glob_match(
                        &pattern_chars.clone().collect::<String>(),
                        &path_chars.clone().collect::<String>(),
                    ) {
                        return true;
                    }
                    path_chars.next();
                }
                return false;
            }
            (Some(p), Some(c)) if p == c => {
                pattern_chars.next();
                path_chars.next();
            }
            (Some(_), Some(_)) => return false,
            _ => return path_chars.peek().is_none(),
        }
    }

    true
}

// Re-export as Watcher for compatibility
pub use FileWatcher as Watcher;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_glob_matching() {
        assert!(matches_glob("*.rs", "main.rs"));
        assert!(matches_glob("*.rs", "lib.rs"));
        assert!(!matches_glob("*.rs", "main.txt"));

        assert!(matches_glob("*/target/*", "/home/user/project/target/debug"));
        assert!(matches_glob("*.tmp", "file.tmp"));

        assert!(!matches_glob("*.git/*", "src/main.rs"));
        assert!(matches_glob("*.git/*", ".git/config"));
    }

    #[test]
    fn test_should_ignore() {
        let watcher = FileWatcher::new(vec![PathBuf::from(".")]);

        assert!(watcher.should_ignore(Path::new(".git/config")));
        assert!(watcher.should_ignore(Path::new("target/debug/main")));
        assert!(watcher.should_ignore(Path::new("node_modules/package/index.js")));
        assert!(watcher.should_ignore(Path::new(".DS_Store")));

        assert!(!watcher.should_ignore(Path::new("src/main.rs")));
        assert!(!watcher.should_ignore(Path::new("Cargo.toml")));
    }
}
