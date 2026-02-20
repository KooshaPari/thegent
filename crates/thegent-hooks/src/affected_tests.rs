//! Affected Tests Detection
//!
//! This module provides intelligent test selection based on code changes.
//! It uses three strategies:
//! 1. Pattern-based: Detect changed file patterns (e.g., src/foo.rs → tests/test_foo.rs)
//! 2. Import-based: Parse imports to find dependent tests
//! 3. Coverage-based: Use coverage maps to identify affected tests (future)

use std::collections::{HashMap, HashSet, VecDeque};
use std::fs;
use std::path::Path;
use regex::Regex;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AffectedTestsError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Invalid regex: {0}")]
    Regex(#[from] regex::Error),
    #[error("Failed to parse file: {0}")]
    ParseError(String),
}

pub type Result<T> = std::result::Result<T, AffectedTestsError>;

/// Represents a single test file with metadata
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct TestFile {
    /// Relative path to test file
    pub path: String,
    /// The module/file this test is testing
    pub target_module: Option<String>,
    /// Tests in this file
    pub tests: Vec<String>,
}

/// Strategies for detecting affected tests
#[derive(Debug, Clone, Copy)]
pub enum DetectionStrategy {
    /// Pattern-based detection (fastest, most reliable)
    Pattern,
    /// Import-based detection (accurate, slower)
    Import,
    /// Coverage-based detection (requires coverage data)
    Coverage,
    /// All strategies combined
    All,
}

/// Analyzes imports in a file
#[derive(Debug, Default)]
struct ImportAnalyzer {
    imports: HashSet<String>,
}

impl ImportAnalyzer {
    fn new() -> Self {
        Self::default()
    }

    /// Parse Python imports
    fn parse_python(&mut self, content: &str) -> Result<()> {
        // Match: import x, from x import y
        let import_re = Regex::new(r"(?:from\s+([\w\.]+)\s+)?import\s+([\w\.\*,\s]+)")?;

        for cap in import_re.captures_iter(content) {
            if let Some(module) = cap.get(1) {
                self.imports.insert(module.as_str().to_string());
            } else if let Some(items) = cap.get(2) {
                // from direct imports
                let parts: Vec<&str> = items.as_str().split(',').collect();
                for part in parts {
                    let normalized = part.trim().split_whitespace().next().unwrap_or("");
                    if !normalized.is_empty() && normalized != "*" {
                        self.imports.insert(normalized.to_string());
                    }
                }
            }
        }

        Ok(())
    }

    /// Parse TypeScript/JavaScript imports
    fn parse_typescript(&mut self, content: &str) -> Result<()> {
        // Match: import { x } from "y", import x from "y"
        let import_re = Regex::new(
            r#"import\s+(?:[\w\{\}\s,]+\s+)?from\s+['"]([\w\./\-@]+)['"]"#,
        )?;

        for cap in import_re.captures_iter(content) {
            if let Some(module) = cap.get(1) {
                self.imports.insert(module.as_str().to_string());
            }
        }

        Ok(())
    }

    /// Parse Rust imports
    fn parse_rust(&mut self, content: &str) -> Result<()> {
        // Match: use crate::path::to::module, use super::module
        let use_re = Regex::new(r"use\s+(?:crate|super|[\w:]+)::([\w:]+)")?;

        for cap in use_re.captures_iter(content) {
            if let Some(module) = cap.get(1) {
                self.imports.insert(module.as_str().to_string());
            }
        }

        Ok(())
    }

    fn get_imports(&self) -> Vec<String> {
        let mut imports: Vec<_> = self.imports.iter().cloned().collect();
        imports.sort();
        imports
    }
}

/// Pattern-based test detection
pub struct PatternDetector {
    test_patterns: Vec<(Regex, String)>,
}

impl PatternDetector {
    pub fn new() -> Result<Self> {
        let test_patterns = vec![
            // Python: src/foo.py → tests/test_foo.py or tests/foo_test.py
            (
                Regex::new(r"^src/([\w/]+)\.py$")?,
                String::new(),
            ),
            // Python: thegent/foo.py → tests/test_foo.py
            (
                Regex::new(r"^thegent/([\w/]+)\.py$")?,
                String::new(),
            ),
            // Rust: src/lib.rs or src/main.rs → tests/integration_tests.rs or src/main.rs tests
            (
                Regex::new(r"^src/(lib|main)\.rs$")?,
                String::new(),
            ),
            // Rust: src/foo.rs → tests/foo_test.rs
            (
                Regex::new(r"^src/([\w/]+)\.rs$")?,
                String::new(),
            ),
            // TypeScript: src/foo.ts → src/foo.test.ts or tests/foo.test.ts
            (
                Regex::new(r"^src/([\w/]+)\.ts(?:x)?$")?,
                String::new(),
            ),
        ];

        Ok(PatternDetector { test_patterns })
    }

    /// Find test files matching changed file patterns
    pub fn find_test_candidates(&self, changed_file: &str) -> Vec<String> {
        let mut candidates = Vec::new();

        for (pattern, _) in &self.test_patterns {
            if let Some(caps) = pattern.captures(changed_file) {
                if let Some(name) = caps.get(1) {
                    let name = name.as_str();

                    // Generate candidate paths
                    match changed_file {
                        f if f.ends_with(".py") => {
                            candidates.push(format!("tests/test_{}.py", name));
                            candidates.push(format!("tests/{}_test.py", name));
                        }
                        f if f.ends_with(".rs") => {
                            candidates.push(format!("tests/{}_test.rs", name));
                            if name == "lib" || name == "main" {
                                candidates.push("tests/integration_tests.rs".to_string());
                            }
                        }
                        f if f.ends_with(".ts") || f.ends_with(".tsx") => {
                            candidates.push(format!("src/{}.test.ts", name));
                            candidates.push(format!("src/{}.test.tsx", name));
                            candidates.push(format!("tests/{}.test.ts", name));
                            candidates.push(format!("tests/{}.test.tsx", name));
                        }
                        _ => {}
                    }
                }
            }
        }

        candidates
    }
}

impl Default for PatternDetector {
    fn default() -> Self {
        Self::new().expect("Failed to create PatternDetector")
    }
}

/// Import-based test detection
pub struct ImportDetector {
    /// Map of files to their imports
    file_imports: HashMap<String, Vec<String>>,
    /// Reverse index: module → files that import it
    import_map: HashMap<String, Vec<String>>,
}

impl ImportDetector {
    pub fn new() -> Self {
        Self {
            file_imports: HashMap::new(),
            import_map: HashMap::new(),
        }
    }

    /// Build import graph from project
    pub fn build_graph(&mut self, project_dir: &Path) -> Result<()> {
        self.scan_directory(project_dir)?;
        self.build_reverse_index();
        Ok(())
    }

    fn scan_directory(&mut self, dir: &Path) -> Result<()> {
        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_dir() {
                let dir_name = path.file_name().unwrap().to_string_lossy();
                // Skip common exclusions
                if matches!(
                    dir_name.as_ref(),
                    ".git" | "node_modules" | ".venv" | "target" | "dist"
                ) {
                    continue;
                }
                self.scan_directory(&path)?;
            } else if path.is_file() {
                self.analyze_file(&path)?;
            }
        }
        Ok(())
    }

    fn analyze_file(&mut self, path: &Path) -> Result<()> {
        let content = fs::read_to_string(path)?;
        let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");

        let mut analyzer = ImportAnalyzer::new();

        match ext {
            "py" => analyzer.parse_python(&content)?,
            "ts" | "tsx" | "js" | "jsx" => analyzer.parse_typescript(&content)?,
            "rs" => analyzer.parse_rust(&content)?,
            _ => return Ok(()),
        }

        let rel_path = path.to_string_lossy().to_string();
        let imports = analyzer.get_imports();

        self.file_imports.insert(rel_path, imports);

        Ok(())
    }

    fn build_reverse_index(&mut self) {
        for (file, imports) in &self.file_imports {
            for import in imports {
                self.import_map
                    .entry(import.clone())
                    .or_insert_with(Vec::new)
                    .push(file.clone());
            }
        }
    }

    /// Find tests that import from changed modules
    pub fn find_dependent_tests(&self, changed_modules: &[String]) -> Vec<String> {
        let mut affected = HashSet::new();

        for module in changed_modules {
            if let Some(dependents) = self.import_map.get(module) {
                for dependent in dependents {
                    // Is it a test file?
                    if self.is_test_file(dependent) {
                        affected.insert(dependent.clone());
                    }
                }
            }
        }

        let mut result: Vec<_> = affected.into_iter().collect();
        result.sort();
        result
    }

    fn is_test_file(&self, path: &str) -> bool {
        path.contains("test") || path.contains("spec")
    }
}

impl Default for ImportDetector {
    fn default() -> Self {
        Self::new()
    }
}

/// Main affected tests analyzer
pub struct AffectedTestsAnalyzer {
    pattern_detector: PatternDetector,
    import_detector: ImportDetector,
}

impl AffectedTestsAnalyzer {
    pub fn new() -> Result<Self> {
        Ok(Self {
            pattern_detector: PatternDetector::new()?,
            import_detector: ImportDetector::new(),
        })
    }

    /// Analyze changed files and return affected tests
    pub fn analyze(
        &mut self,
        project_dir: &Path,
        changed_files: &[String],
        strategy: DetectionStrategy,
    ) -> Result<Vec<TestFile>> {
        // Build import graph if needed
        if matches!(strategy, DetectionStrategy::Import | DetectionStrategy::All) {
            self.import_detector.build_graph(project_dir)?;
        }

        let mut affected_tests = HashSet::new();

        match strategy {
            DetectionStrategy::Pattern => {
                for changed in changed_files {
                    let candidates = self.pattern_detector.find_test_candidates(changed);
                    for candidate in candidates {
                        if (project_dir.as_ref() as &Path).join(&candidate).exists() {
                            affected_tests.insert(candidate);
                        }
                    }
                }
            }
            DetectionStrategy::Import => {
                let module_names = self.extract_module_names(changed_files);
                let tests = self.import_detector.find_dependent_tests(&module_names);
                affected_tests.extend(tests);
            }
            DetectionStrategy::All => {
                // Pattern-based
                for changed in changed_files {
                    let candidates = self.pattern_detector.find_test_candidates(changed);
                    for candidate in candidates {
                        if (project_dir.as_ref() as &Path).join(&candidate).exists() {
                            affected_tests.insert(candidate);
                        }
                    }
                }

                // Import-based
                let module_names = self.extract_module_names(changed_files);
                let tests = self.import_detector.find_dependent_tests(&module_names);
                affected_tests.extend(tests);
            }
            DetectionStrategy::Coverage => {
                // TODO: Implement coverage-based detection
                eprintln!("Coverage-based detection not yet implemented");
            }
        }

        // Convert to TestFile objects
        let mut result: Vec<TestFile> = affected_tests
            .into_iter()
            .map(|path| TestFile {
                path,
                target_module: None,
                tests: Vec::new(),
            })
            .collect();

        result.sort_by(|a, b| a.path.cmp(&b.path));
        Ok(result)
    }

    fn extract_module_names(&self, changed_files: &[String]) -> Vec<String> {
        changed_files
            .iter()
            .filter_map(|f| {
                let path = Path::new(f);
                path.file_stem()
                    .and_then(|stem| stem.to_str())
                    .map(|s| s.to_string())
            })
            .collect()
    }

    /// Find tests that transitively depend on changed files
    pub fn find_transitive_tests(
        &self,
        changed_files: &[String],
    ) -> Result<Vec<String>> {
        let mut affected = HashSet::new();
        let mut queue = VecDeque::new();

        // Initial affected tests from pattern matching
        for changed in changed_files {
            let candidates = self.pattern_detector.find_test_candidates(changed);
            for candidate in candidates {
                queue.push_back(candidate.clone());
                affected.insert(candidate);
            }
        }

        // BFS to find transitive dependencies
        while let Some(test_file) = queue.pop_front() {
            if let Some(imports) = self.import_detector.file_imports.get(&test_file) {
                for import in imports {
                    if let Some(dependents) = self.import_detector.import_map.get(import) {
                        for dependent in dependents {
                            if affected.insert(dependent.clone()) {
                                queue.push_back(dependent.clone());
                            }
                        }
                    }
                }
            }
        }

        let mut result: Vec<_> = affected.into_iter().collect();
        result.sort();
        Ok(result)
    }
}

impl Default for AffectedTestsAnalyzer {
    fn default() -> Self {
        Self::new().expect("Failed to create AffectedTestsAnalyzer")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pattern_detector_python() {
        let detector = PatternDetector::new().unwrap();
        let candidates = detector.find_test_candidates("src/config.py");

        assert!(candidates.contains(&"tests/test_config.py".to_string()));
        assert!(candidates.contains(&"tests/config_test.py".to_string()));
    }

    #[test]
    fn test_pattern_detector_rust() {
        let detector = PatternDetector::new().unwrap();
        let candidates = detector.find_test_candidates("src/lib.rs");

        assert!(candidates.contains(&"tests/integration_tests.rs".to_string()));
    }

    #[test]
    fn test_pattern_detector_typescript() {
        let detector = PatternDetector::new().unwrap();
        let candidates = detector.find_test_candidates("src/auth.ts");

        assert!(candidates.contains(&"src/auth.test.ts".to_string()));
        assert!(candidates.contains(&"tests/auth.test.ts".to_string()));
    }

    #[test]
    fn test_import_analyzer_python() -> Result<()> {
        let mut analyzer = ImportAnalyzer::new();
        let content = r#"
import os
from pathlib import Path
from src.config import Config
        "#;

        analyzer.parse_python(content)?;
        let imports = analyzer.get_imports();

        assert!(imports.contains(&"os".to_string()));
        assert!(imports.contains(&"pathlib".to_string()));
        assert!(imports.contains(&"src.config".to_string()));

        Ok(())
    }

    #[test]
    fn test_import_analyzer_typescript() -> Result<()> {
        let mut analyzer = ImportAnalyzer::new();
        let content = r#"
import { Config } from './config';
import * as fs from 'fs';
        "#;

        analyzer.parse_typescript(content)?;
        let imports = analyzer.get_imports();

        assert!(imports.contains(&"./config".to_string()));
        assert!(imports.contains(&"fs".to_string()));

        Ok(())
    }

    #[test]
    fn test_import_analyzer_rust() -> Result<()> {
        let mut analyzer = ImportAnalyzer::new();
        let content = r#"
use crate::config::Config;
use super::utils;
        "#;

        analyzer.parse_rust(content)?;
        let imports = analyzer.get_imports();

        assert!(imports.contains(&"config::Config".to_string()));

        Ok(())
    }
}
