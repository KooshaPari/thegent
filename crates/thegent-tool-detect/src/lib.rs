use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};
use rayon::prelude::*;

#[cfg(all(feature = "python", not(test)))]
use pyo3::prelude::*;

const CACHE_TTL_SECONDS: u64 = 3600;
const CACHE_FILE: &str = "/tmp/thegent-tools-cache.json";

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ToolCache {
    tools: HashMap<String, String>,
    timestamp: u64,
}

/// Fast, cached tool detection with parallel scanning
///
/// # Example
/// ```
/// use thegent_tool_detect::ToolDetector;
///
/// let detector = ToolDetector::new();
/// let tools = detector.detect_all();
/// println!("Found {} tools", tools.len());
/// ```
pub struct ToolDetector {
    cache_file: PathBuf,
}

impl ToolDetector {
    /// Create a new tool detector with default settings
    pub fn new() -> Self {
        Self {
            cache_file: PathBuf::from(CACHE_FILE),
        }
    }

    /// Create with custom cache file location
    pub fn with_cache_file(cache_file: impl Into<PathBuf>) -> Self {
        Self {
            cache_file: cache_file.into(),
        }
    }

    /// Detect all tools with automatic caching
    ///
    /// Returns a map of tool names to their full paths.
    /// Results are cached for 1 hour by default.
    pub fn detect_all(&self) -> HashMap<String, String> {
        // Try cache first (fast path)
        if let Ok(cached) = self.load_cache() {
            if self.is_cache_valid(&cached) {
                return cached.tools;
            }
        }

        // Parallel scan (efficient)
        let tools = self.scan_tools();

        // Save cache (best effort - don't fail on error)
        let _ = self.save_cache(&tools);

        tools
    }

    /// Detect a single tool (bypasses cache for fresh results)
    ///
    /// # Example
    /// ```
    /// let detector = ToolDetector::new();
    /// if let Some(path) = detector.detect_one("jq") {
    ///     println!("Found jq at: {}", path);
    /// }
    /// ```
    pub fn detect_one(&self, name: &str) -> Option<String> {
        use which::which;

        // Try common aliases/variants
        let candidates = self.get_candidates(name);

        for candidate in candidates {
            if let Ok(path) = which(candidate) {
                return Some(path.to_string_lossy().to_string());
            }
        }
        None
    }

    /// Get all known tool candidates for a tool name
    fn get_candidates<'a>(&self, name: &'a str) -> Vec<&'a str> {
        match name {
            "jq" => vec!["jaq", "jq"],
            "fd" => vec!["fd", "fdfind"],
            "timeout" => vec!["gtimeout", "timeout"],
            "hash" => vec!["b3sum", "sha256sum", "shasum"],
            _ => vec![name],
        }
    }

    fn load_cache(&self) -> Result<ToolCache, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(&self.cache_file)?;
        let cache: ToolCache = serde_json::from_str(&content)?;
        Ok(cache)
    }

    fn is_cache_valid(&self, cache: &ToolCache) -> bool {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        now.saturating_sub(cache.timestamp) < CACHE_TTL_SECONDS
    }

    fn scan_tools(&self) -> HashMap<String, String> {
        use which::which;

        // Define tools with their variants (parallel scan)
        let tool_configs = vec![
            ("jq", vec!["jaq", "jq"]),
            ("rg", vec!["rg"]),
            ("fd", vec!["fd", "fdfind"]),
            ("timeout", vec!["gtimeout", "timeout"]),
            ("hash", vec!["b3sum", "sha256sum", "shasum"]),
            ("pgrep", vec!["pgrep"]),
        ];

        tool_configs
            .into_par_iter()
            .filter_map(|(key, candidates)| {
                for candidate in candidates {
                    if let Ok(path) = which(candidate) {
                        return Some((key.to_string(), path.to_string_lossy().to_string()));
                    }
                }
                None
            })
            .collect()
    }

    fn save_cache(&self, tools: &HashMap<String, String>) -> Result<(), Box<dyn std::error::Error>> {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let cache = ToolCache {
            tools: tools.clone(),
            timestamp,
        };

        let content = serde_json::to_string_pretty(&cache)?;

        // Atomic write: write to temp file, then rename (prevents corruption)
        let temp_file = format!("{}.tmp", self.cache_file.to_string_lossy());
        std::fs::write(&temp_file, content)?;
        std::fs::rename(&temp_file, &self.cache_file)?;

        Ok(())
    }

    /// Clear the cache (useful for testing or forced refresh)
    pub fn clear_cache(&self) -> Result<(), Box<dyn std::error::Error>> {
        if self.cache_file.exists() {
            std::fs::remove_file(&self.cache_file)?;
        }
        Ok(())
    }

    /// Get cache statistics
    pub fn cache_stats(&self) -> CacheStats {
        match self.load_cache() {
            Ok(cache) => {
                let age = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs()
                    .saturating_sub(cache.timestamp);
                CacheStats {
                    exists: true,
                    tool_count: cache.tools.len(),
                    age_seconds: age,
                    is_valid: age < CACHE_TTL_SECONDS,
                }
            }
            Err(_) => CacheStats {
                exists: false,
                tool_count: 0,
                age_seconds: 0,
                is_valid: false,
            },
        }
    }
}

#[derive(Debug, Clone)]
pub struct CacheStats {
    pub exists: bool,
    pub tool_count: usize,
    pub age_seconds: u64,
    pub is_valid: bool,
}

impl Default for ToolDetector {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(all(feature = "python", not(test)))]
#[pyfunction]
fn detect_tools() -> PyResult<HashMap<String, String>> {
    let detector = ToolDetector::new();
    Ok(detector.detect_all())
}

#[cfg(all(feature = "python", not(test)))]
#[pyfunction]
fn detect_tool(name: &str) -> PyResult<Option<String>> {
    let detector = ToolDetector::new();
    Ok(detector.detect_one(name))
}

#[cfg(all(feature = "python", not(test)))]
#[pymodule]
fn thegent_tool_detect(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(detect_tools, m)?)?;
    m.add_function(wrap_pyfunction!(detect_tool, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tool_detection() {
        let detector = ToolDetector::new();
        let tools = detector.detect_all();
        // At least some common tools should be found (or we're in CI)
        assert!(!tools.is_empty() || std::env::var("CI").is_ok());
    }

    #[test]
    fn test_single_tool() {
        let detector = ToolDetector::new();
        // Should find at least one common tool
        let found = detector.detect_one("sh").or_else(|| detector.detect_one("bash"));
        assert!(found.is_some() || std::env::var("CI").is_ok());
    }

    #[test]
    fn test_cache_stats() {
        let detector = ToolDetector::new();
        let _ = detector.detect_all(); // Populate cache
        let stats = detector.cache_stats();
        assert!(stats.exists);
    }
}
