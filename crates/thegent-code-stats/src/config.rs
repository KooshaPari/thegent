//! Configuration for code statistics analysis.

use serde::{Deserialize, Serialize};

/// Configuration for code statistics analysis.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalyzeConfig {
    /// Maximum depth to traverse (None = unlimited)
    pub max_depth: Option<usize>,

    /// Use git ls-files to get tracked files (faster, respects .gitignore)
    pub use_git_files: bool,

    /// Fast mode uses memory-mapped file reading
    pub fast_mode: bool,

    /// Patterns to exclude (gitignore-style)
    pub exclude_patterns: Vec<String>,

    /// Patterns to include (if empty, all files are included)
    pub include_patterns: Vec<String>,

    /// Minimum file size to process (bytes)
    pub min_file_size: Option<u64>,

    /// Maximum file size to process (bytes)
    pub max_file_size: Option<u64>,

    /// Include hidden files
    pub include_hidden: bool,

    /// Output format
    pub format: OutputFormat,

    /// Show progress bar
    pub show_progress: bool,
}

impl Default for AnalyzeConfig {
    fn default() -> Self {
        Self {
            max_depth: Some(50),
            use_git_files: true,
            fast_mode: true,
            exclude_patterns: vec![
                "**/node_modules/**".to_string(),
                "**/target/**".to_string(),
                "**/.git/**".to_string(),
                "**/__pycache__/**".to_string(),
                "**/.venv/**".to_string(),
                "**/venv/**".to_string(),
                "**/.next/**".to_string(),
                "**/dist/**".to_string(),
                "**/build/**".to_string(),
                "**/coverage/**".to_string(),
                "**/*.min.js".to_string(),
                "**/*.bundle.js".to_string(),
            ],
            include_patterns: vec![],
            min_file_size: None,
            max_file_size: Some(10 * 1024 * 1024), // 10MB
            include_hidden: false,
            format: OutputFormat::Json,
            show_progress: false,
        }
    }
}

/// Output format for statistics.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum OutputFormat {
    Json,
    Markdown,
    Mermaid,
    Csv,
}

impl Default for OutputFormat {
    fn default() -> Self {
        Self::Json
    }
}

impl std::str::FromStr for OutputFormat {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "json" => Ok(OutputFormat::Json),
            "markdown" | "md" => Ok(OutputFormat::Markdown),
            "mermaid" | "mmd" => Ok(OutputFormat::Mermaid),
            "csv" => Ok(OutputFormat::Csv),
            _ => Err(format!("unknown format: {}", s)),
        }
    }
}

/// Tree generation configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TreeConfig {
    /// Maximum depth for tree visualization
    pub max_depth: usize,

    /// Sort by (loc, name, files)
    pub sort_by: TreeSortBy,

    /// Show percentages
    pub show_percentages: bool,

    /// Show progress bars
    pub show_bars: bool,

    /// Bar width in characters
    pub bar_width: usize,
}

impl Default for TreeConfig {
    fn default() -> Self {
        Self {
            max_depth: 10,
            sort_by: TreeSortBy::Loc,
            show_percentages: true,
            show_bars: true,
            bar_width: 40,
        }
    }
}

/// Sort criteria for tree output.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TreeSortBy {
    Loc,
    Name,
    Files,
    Language,
}

impl Default for TreeSortBy {
    fn default() -> Self {
        Self::Loc
    }
}
