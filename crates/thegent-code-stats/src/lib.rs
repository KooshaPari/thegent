//! High-performance code statistics and LOC counting for thegent.
//!
//! This crate provides fast, parallel code analysis with support for:
//! - Lines of code (LOC), code, comments, blank lines
//! - File and folder tree generation
//! - Technology/language detection
//! - Git blame integration for ownership
//! - Multiple output formats (JSON, Markdown, Mermaid)
//!
//! # Performance
//!
//! Uses rayon for parallel file processing and memmap2 for fast file reading.
//! Can process large repositories (10k+ files) in seconds.

use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use walkdir::WalkDir;

mod config;
mod detectors;
mod output;
mod stats;
mod tree;

pub use config::*;
pub use detectors::*;
pub use output::*;
pub use stats::*;
pub use tree::*;

// ============================================================================
// Public API
// ============================================================================

/// Run code statistics analysis on a directory tree.
pub fn analyze_directory<P: AsRef<Path>>(
    root: P,
    config: &AnalyzeConfig,
) -> anyhow::Result<CodeStats> {
    let root = root.as_ref();
    let config = Arc::new(config.clone());

    // Collect all files to analyze
    let files: Vec<PathBuf> = if config.use_git_files {
        collect_git_tracked_files(root)?
    } else {
        collect_files(root, &config)?
    };

    // Process files in parallel
    let results: Vec<FileStats> = files
        .par_iter()
        .filter_map(|path| {
            let cfg = config.as_ref();
            if should_process(path, cfg) {
                process_file(path, cfg).ok()
            } else {
                None
            }
        })
        .collect();

    // Aggregate results
    Ok(aggregate_stats(results))
}

/// Collect files tracked by git.
fn collect_git_tracked_files(root: &Path) -> anyhow::Result<Vec<PathBuf>> {
    use std::process::Command;

    let output = Command::new("git")
        .args(["ls-files", "-z"])
        .current_dir(root)
        .output()?;

    if !output.status.success() {
        anyhow::bail!("git ls-files failed");
    }

    let files: Vec<PathBuf> = output.stdout
        .split(|&b| b == 0)
        .filter(|s| !s.is_empty())
        .filter_map(|s| {
            let path = String::from_utf8_lossy(s).into_owned();
            // Filter to source files
            if is_source_file(&path) {
                Some(PathBuf::from(path))
            } else {
                None
            }
        })
        .collect();

    Ok(files)
}

/// Collect all files from directory (non-git).
fn collect_files(root: &Path, config: &AnalyzeConfig) -> anyhow::Result<Vec<PathBuf>> {
    let mut files = Vec::new();

    let walker = WalkDir::new(root)
        .follow_links(false)
        .max_depth(config.max_depth.unwrap_or(usize::MAX));

    for entry in walker.into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.is_file() && is_source_file(&path.to_string_lossy()) {
            files.push(path.to_path_buf());
        }
    }

    Ok(files)
}

/// Check if a file should be processed based on config.
fn should_process(path: &Path, config: &AnalyzeConfig) -> bool {
    let path_str = path.to_string_lossy();

    // Check exclusions
    for pattern in &config.exclude_patterns {
        if glob_match(pattern, &path_str) {
            return false;
        }
    }

    // Check inclusions (if specified)
    if !config.include_patterns.is_empty() {
        let mut included = false;
        for pattern in &config.include_patterns {
            if glob_match(pattern, &path_str) {
                included = true;
                break;
            }
        }
        if !included {
            return false;
        }
    }

    true
}

/// Fast glob matching for simple patterns.
fn glob_match(pattern: &str, path: &str) -> bool {
    // Simple patterns: **/foo/**, *.rs, src/**
    if pattern.starts_with("**/") {
        let suffix = &pattern[3..];
        return path.contains(suffix);
    }
    if pattern.ends_with("/**") {
        let prefix = &pattern[..pattern.len() - 3];
        return path.starts_with(prefix);
    }
    if pattern.contains('*') {
        let parts: Vec<&str> = pattern.split('*').collect();
        let mut pos = 0;
        for part in parts {
            if let Some(idx) = path[pos..].find(part) {
                pos += idx + part.len();
            } else {
                return false;
            }
        }
        return true;
    }
    path.contains(pattern)
}

/// Check if file is a source file based on extension.
fn is_source_file(path: &str) -> bool {
    let source_exts = [
        "rs", "py", "js", "ts", "tsx", "jsx", "go", "java", "kt", "rb",
        "c", "cpp", "cxx", "h", "hpp", "cs", "swift", "rs", "zig",
        "sh", "bash", "zsh", "fish",
        "md", "markdown",
        "yaml", "yml", "toml", "json", "jsonc",
        "sql", "xml",
        "css", "scss", "sass", "less",
        "html", "htm", "vue", "svelte",
        "tf", "hcl",
        "dockerfile", "makefile", "gradle",
        "proto",
    ];

    if let Some(ext) = Path::new(path).extension() {
        let ext_str = ext.to_string_lossy().to_lowercase();
        return source_exts.contains(&ext_str.as_str());
    }

    // Check for special filenames
    let name = Path::new(path).file_name()
        .map(|n| n.to_string_lossy().to_lowercase())
        .unwrap_or_default();

    matches!(
        name.as_str(),
        "makefile" | "dockerfile" | "gemfile" | "rakefile" | "procfile"
    )
}

/// Process a single file and return its statistics.
fn process_file(path: &Path, config: &AnalyzeConfig) -> anyhow::Result<FileStats> {
    let content = if config.fast_mode {
        read_file_fast(path)?
    } else {
        std::fs::read_to_string(path)?
    };

    let extension = path.extension()
        .map(|e| e.to_string_lossy().to_lowercase())
        .unwrap_or_default();

    let (code, comment, blank) = count_lines(&content, &extension);

    Ok(FileStats {
        path: path.to_path_buf(),
        extension,
        language: detect_language(&extension),
        lines: LineCounts {
            total: content.lines().count(),
            code,
            comment,
            blank,
        },
    })
}

/// Fast file reading using memory mapping.
fn read_file_fast(path: &Path) -> anyhow::Result<String> {
    use memmap2::Mmap;

    let file = std::fs::File::open(path)?;
    let mmap = unsafe { Mmap::map(&file)? };

    // Validate UTF-8
    String::from_utf8(mmap.to_vec())
        .map_err(|_| anyhow::anyhow!("file is not valid UTF-8"))
}

/// Count lines by type (code, comment, blank).
fn count_lines(content: &str, extension: &str) -> (usize, usize, usize) {
    let mut code = 0;
    let mut comment = 0;
    let mut blank = 0;

    let is_comment_line = get_comment_line_checker(extension);

    for line in content.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            blank += 1;
        } else if is_comment_line(trimmed) {
            comment += 1;
        } else {
            code += 1;
        }
    }

    (code, comment, blank)
}

/// Get the comment line checker for a given language.
fn get_comment_line_checker(ext: &str) -> impl Fn(&str) -> bool + '_ {
    move |line: &str| {
        match ext {
            "rs" | "c" | "cpp" | "cxx" | "h" | "hpp" | "java" | "kt" | "go"
            | "swift" | "zig" | "cs" | "js" | "ts" | "tsx" | "jsx" => {
                line.starts_with("//") || line.starts_with("/*") || line.starts_with("*")
            }
            "py" | "rb" | "yaml" | "yml" | "sh" | "bash" | "zsh" | "fish" => {
                line.starts_with('#') || line.starts_with("---")
            }
            "md" | "markdown" => line.starts_with("<!--") || line.starts_with("***"),
            _ => line.starts_with("--") || line.starts_with("/*") || line.starts_with("<!--"),
        }
    }
}

/// Detect language from file extension.
fn detect_language(ext: &str) -> &'static str {
    match ext {
        "rs" => "Rust",
        "py" => "Python",
        "js" => "JavaScript",
        "ts" => "TypeScript",
        "tsx" => "TSX",
        "jsx" => "JSX",
        "go" => "Go",
        "java" => "Java",
        "kt" => "Kotlin",
        "rb" => "Ruby",
        "c" => "C",
        "cpp" | "cxx" | "cc" => "C++",
        "h" | "hpp" => "C/C++ Header",
        "cs" => "C#",
        "swift" => "Swift",
        "zig" => "Zig",
        "sh" | "bash" | "zsh" | "fish" => "Shell",
        "md" | "markdown" => "Markdown",
        "yaml" | "yml" => "YAML",
        "toml" => "TOML",
        "json" | "jsonc" => "JSON",
        "sql" => "SQL",
        "xml" => "XML",
        "css" | "scss" | "sass" | "less" => "CSS",
        "html" | "htm" => "HTML",
        "vue" | "svelte" => "Component",
        "tf" | "hcl" => "Terraform",
        "dockerfile" => "Docker",
        "makefile" => "Make",
        "gradle" => "Gradle",
        "proto" => "Protobuf",
        _ => "Other",
    }
}

/// Aggregate file stats into directory-level stats.
fn aggregate_stats(files: Vec<FileStats>) -> CodeStats {
    let mut total_lines = LineCounts::default();
    let mut by_language: HashMap<String, LineCounts> = HashMap::new();
    let mut by_extension: HashMap<String, LineCounts> = HashMap::new();
    let mut folder_totals: HashMap<String, LineCounts> = HashMap::new();

    for file in files {
        // Update totals
        total_lines += file.lines;

        // By language
        let lang_counts = by_language.entry(file.language.to_string()).or_default();
        *lang_counts += file.lines;

        // By extension
        let ext_counts = by_extension.entry(file.extension.clone()).or_default();
        *ext_counts += file.lines;

        // By folder
        let folder = file.path.parent()
            .map(|p| p.to_string_lossy().to_string())
            .unwrap_or_default();
        let folder_counts = folder_totals.entry(folder).or_default();
        *folder_counts += file.lines;
    }

    CodeStats {
        files: files.len(),
        total: total_lines,
        by_language,
        by_extension,
        by_folder: folder_totals,
        file_details: Vec::new(), // Populated separately if needed
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;
    use std::fs::File;
    use std::io::Write;

    #[test]
    fn test_is_source_file() {
        assert!(is_source_file("src/main.rs"));
        assert!(is_source_file("lib.py"));
        assert!(is_source_file("index.ts"));
        assert!(is_source_file("Makefile"));
        assert!(is_source_file("Dockerfile"));
        assert!(!is_source_file("image.png"));
        assert!(!is_source_file("data.bin"));
    }

    #[test]
    fn test_count_lines() {
        let content = r#"fn main() {
    // This is a comment
    let x = 42;

}
"#;
        let (code, comment, blank) = count_lines(content, "rs");
        assert_eq!(code, 3); // fn main, let x, closing }
        assert_eq!(comment, 1);
        assert_eq!(blank, 2);
    }

    #[test]
    fn test_glob_match() {
        assert!(glob_match("**/node_modules/**", "foo/node_modules/bar"));
        assert!(glob_match("src/**", "src/lib.rs"));
        assert!(glob_match("*.rs", "main.rs"));
        assert!(!glob_match("*.py", "main.rs"));
    }

    #[test]
    fn test_analyze_directory() {
        let tmp = TempDir::new().unwrap();

        // Create test files
        let rs_file = tmp.path().join("lib.rs");
        File::create(&rs_file).unwrap().write_all(b"fn main() {}\n").unwrap();

        let py_file = tmp.path().join("script.py");
        File::create(&py_file).unwrap().write_all(b"# Python\nprint('hi')\n").unwrap();

        let config = AnalyzeConfig::default();
        let stats = analyze_directory(tmp.path(), &config).unwrap();

        assert_eq!(stats.files, 2);
        assert!(stats.total.code > 0);
    }
}
