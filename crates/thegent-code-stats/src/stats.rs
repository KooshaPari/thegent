//! Statistics data structures.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Code statistics for a single file.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileStats {
    pub path: String,
    pub loc: usize,
    pub lines: usize,
    pub blank_lines: usize,
    pub comment_lines: usize,
    pub code_lines: usize,
    pub language: String,
    pub extension: String,
    pub size_bytes: u64,
}

/// Code statistics for a directory.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DirectoryStats {
    pub path: String,
    pub total_loc: usize,
    pub total_files: usize,
    pub languages: HashMap<String, usize>,
    pub files: Vec<FileStats>,
}

/// Summary statistics for the entire codebase.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SummaryStats {
    pub total_loc: usize,
    pub total_lines: usize,
    pub total_files: usize,
    pub total_directories: usize,
    pub blank_lines: usize,
    pub comment_lines: usize,
    pub code_lines: usize,
    pub languages: HashMap<String, LanguageStats>,
    pub largest_files: Vec<FileStats>,
    pub most_common_extensions: Vec<(String, usize)>,
}

/// Statistics aggregated by programming language.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LanguageStats {
    pub files: usize,
    pub loc: usize,
    pub lines: usize,
    pub blank_lines: usize,
    pub comment_lines: usize,
    pub code_lines: usize,
    pub percentage: f64,
}

impl SummaryStats {
    pub fn from_file_stats(files: &[FileStats]) -> Self {
        let total_loc = files.iter().map(|f| f.loc).sum();
        let total_lines = files.iter().map(|f| f.lines).sum();
        let total_files = files.len();
        let blank_lines = files.iter().map(|f| f.blank_lines).sum();
        let comment_lines = files.iter().map(|f| f.comment_lines).sum();
        let code_lines = files.iter().map(|f| f.code_lines).sum();

        // Aggregate by language
        let mut lang_map: HashMap<String, LanguageStats> = HashMap::new();
        for file in files {
            let entry = lang_map.entry(file.language.clone()).or_insert_with(|| LanguageStats {
                files: 0,
                loc: 0,
                lines: 0,
                blank_lines: 0,
                comment_lines: 0,
                code_lines: 0,
                percentage: 0.0,
            });
            entry.files += 1;
            entry.loc += file.loc;
            entry.lines += file.lines;
            entry.blank_lines += file.blank_lines;
            entry.comment_lines += file.comment_lines;
            entry.code_lines += file.code_lines;
        }

        // Calculate percentages
        for stats in lang_map.values_mut() {
            if total_loc > 0 {
                stats.percentage = (stats.loc as f64 / total_loc as f64) * 100.0;
            }
        }

        // Get largest files
        let mut sorted_files = files.to_vec();
        sorted_files.sort_by(|a, b| b.loc.cmp(&a.loc));
        let largest_files: Vec<_> = sorted_files.into_iter().take(20).collect();

        // Get most common extensions
        let mut ext_counts: HashMap<String, usize> = HashMap::new();
        for file in files {
            *ext_counts.entry(file.extension.clone()).or_insert(0) += 1;
        }
        let mut most_common_extensions: Vec<_> = ext_counts.into_iter().collect();
        most_common_extensions.sort_by(|a, b| b.1.cmp(&a.1));
        let most_common_extensions = most_common_extensions.into_iter().take(10).collect();

        // Count unique directories
        let mut dirs = std::collections::HashSet::new();
        for file in files {
            if let Some(parent) = std::path::Path::new(&file.path).parent() {
                dirs.insert(parent.to_string_lossy().to_string());
            }
        }

        Self {
            total_loc,
            total_lines,
            total_files,
            total_directories: dirs.len(),
            blank_lines,
            comment_lines,
            code_lines,
            languages: lang_map,
            largest_files,
            most_common_extensions,
        }
    }
}

/// Complete codebase statistics.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeStats {
    pub summary: SummaryStats,
    pub files: Vec<FileStats>,
    pub by_directory: HashMap<String, DirectoryStats>,
    pub generated_at: chrono::DateTime<chrono::Utc>,
    pub repo_name: String,
    pub commit_hash: Option<String>,
    pub branch: Option<String>,
}

impl CodeStats {
    pub fn new(repo_name: String) -> Self {
        Self {
            summary: SummaryStats {
                total_loc: 0,
                total_lines: 0,
                total_files: 0,
                total_directories: 0,
                blank_lines: 0,
                comment_lines: 0,
                code_lines: 0,
                languages: HashMap::new(),
                largest_files: vec![],
                most_common_extensions: vec![],
            },
            files: vec![],
            by_directory: HashMap::new(),
            generated_at: chrono::Utc::now(),
            repo_name,
            commit_hash: None,
            branch: None,
        }
    }
}
