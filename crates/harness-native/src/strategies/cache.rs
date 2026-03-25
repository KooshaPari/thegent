use std::path::{Path, PathBuf};

use fs2::FileExt;

pub fn l1_path(harness_home: &Path, key: &str) -> PathBuf {
    harness_home
        .join("var")
        .join("cache")
        .join("l1")
        .join(format!("{}.json", key))
}

pub fn l2_path(harness_home: &Path, key: &str) -> PathBuf {
    harness_home
        .join("var")
        .join("cache")
        .join("l2")
        .join(format!("{}.json", key))
}

pub fn lock_shared(path: &Path, _timeout_secs: u64) -> Option<std::fs::File> {
    let file = std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(true)
        .open(path)
        .ok()?;
    fs2::FileExt::lock_shared(&file).ok()?;
    Some(file)
}
