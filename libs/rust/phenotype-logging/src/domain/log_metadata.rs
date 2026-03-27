//! LogMetadata - Metadata associated with log entries.
//!
//! Pure domain type with no external dependencies.

/// Metadata about where a log was generated.
#[derive(Debug, Clone)]
pub struct LogMetadata {
    /// Source file name
    pub file: Option<String>,
    /// Source line number
    pub line: Option<u32>,
    /// Source module path
    pub module_path: Option<String>,
}

impl LogMetadata {
    /// Create new, empty metadata.
    pub fn new() -> Self {
        Self {
            file: None,
            line: None,
            module_path: None,
        }
    }

    /// Set the file location.
    pub fn with_file(mut self, file: impl Into<String>) -> Self {
        self.file = Some(file.into());
        self
    }

    /// Set the line number.
    pub fn with_line(mut self, line: u32) -> Self {
        self.line = Some(line);
        self
    }

    /// Set the module path.
    pub fn with_module_path(mut self, module_path: impl Into<String>) -> Self {
        self.module_path = Some(module_path.into());
        self
    }
}

impl Default for LogMetadata {
    fn default() -> Self {
        Self::new()
    }
}
