//! Affected Tests Detection
//!
//! This module provides intelligent test selection based on code changes.
//! It uses three strategies:
//! 1. Pattern-based: Detect changed file patterns (e.g., src/foo.rs → tests/test_foo.rs)
//! 2. Import-based: Parse imports to find dependent tests
//! 3. Coverage-based: Use coverage maps to identify affected tests

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

/// Coverage-based test detection using coverage maps (e.g., from lcov, coverage.json).
///
/// This detector parses coverage data to identify which tests cover which source files,
/// enabling precise test selection based on actual coverage relationships.
pub struct CoverageDetector {
    /// Map of source files to tests that cover them
    coverage_map: HashMap<String, Vec<String>>,
    /// Map of test files to source files they cover
    test_to_sources: HashMap<String, Vec<String>>,
    /// Whether coverage data is available
    has_coverage_data: bool,
}

impl CoverageDetector {
    pub fn new() -> Self {
        Self {
            coverage_map: HashMap::new(),
            test_to_sources: HashMap::new(),
            has_coverage_data: false,
        }
    }

    /// Load coverage data from various formats.
    ///
    /// Supports:
    /// - lcov.info files
    /// - coverage.json (istanbul/nyc format)
    /// - tarpaulin output (coverage.json)
    pub fn load_coverage(&mut self, project_dir: &Path) -> Result<()> {
        // Try lcov.info first
        let lcov_path = project_dir.join("coverage").join("lcov.info");
        if lcov_path.exists() {
            self.parse_lcov(&lcov_path)?;
            self.has_coverage_data = true;
            return Ok(());
        }

        // Try coverage.json (istanbul/nyc format)
        let coverage_json = project_dir.join("coverage").join("coverage-final.json");
        if coverage_json.exists() {
            self.parse_istanbul(&coverage_json)?;
            self.has_coverage_data = true;
            return Ok(());
        }

        // Try tarpaulin coverage
        let tarpaulin_json = project_dir.join("tarpaulin-report.json");
        if tarpaulin_json.exists() {
            self.parse_tarpaulin(&tarpaulin_json)?;
            self.has_coverage_data = true;
            return Ok(());
        }

        // Try pytest-cov coverage
        let pytest_cov = project_dir.join(".coverage");
        if pytest_cov.exists() {
            // .coverage is a binary format; we'd need to run `coverage xml` or `coverage json`
            // For now, check for the XML export
            let coverage_xml = project_dir.join("coverage.xml");
            if coverage_xml.exists() {
                self.parse_cobertura(&coverage_xml)?;
                self.has_coverage_data = true;
                return Ok(());
            }
        }

        // No coverage data available
        self.has_coverage_data = false;
        Ok(())
    }

    /// Parse lcov.info format
    fn parse_lcov(&mut self, path: &Path) -> Result<()> {
        let content = fs::read_to_string(path)?;
        let mut current_file: Option<String> = None;
        let mut current_test: Option<String> = None;

        for line in content.lines() {
            if line.starts_with("SF:") {
                // Source file
                current_file = Some(line[3..].to_string());
            } else if line.starts_with("TN:") {
                // Test name (optional in lcov)
                current_test = Some(line[3..].to_string());
            } else if line.starts_with("DA:") && current_file.is_some() {
                // Line data - indicates this file was covered
                if let Some(ref source) = current_file {
                    // Map source to test (if test name available)
                    if let Some(ref test) = current_test {
                        self.coverage_map
                            .entry(source.clone())
                            .or_insert_with(Vec::new)
                            .push(test.clone());
                        self.test_to_sources
                            .entry(test.clone())
                            .or_insert_with(Vec::new)
                            .push(source.clone());
                    } else {
                        // No test name - assume generic coverage
                        self.coverage_map
                            .entry(source.clone())
                            .or_insert_with(Vec::new);
                    }
                }
            } else if line == "end_of_record" {
                current_file = None;
                current_test = None;
            }
        }

        Ok(())
    }

    /// Parse istanbul/nyc coverage.json format
    fn parse_istanbul(&mut self, path: &Path) -> Result<()> {
        let content = fs::read_to_string(path)?;
        let coverage: serde_json::Value = serde_json::from_str(&content)
            .map_err(|e| AffectedTestsError::ParseError(format!("Invalid JSON: {}", e)))?;

        if let Some(files) = coverage.as_object() {
            for (file_path, data) in files {
                // Normalize the file path
                let normalized = self.normalize_path(file_path);

                // Check if this file has any covered lines
                if let Some(coverage_data) = data.as_object() {
                    if let Some(lines) = coverage_data.get("l").and_then(|l| l.as_object()) {
                        // If any line has count > 0, this file is covered
                        let has_coverage = lines.values().any(|v| {
                            v.as_u64().unwrap_or(0) > 0
                        });

                        if has_coverage {
                            // Try to determine test from the path pattern
                            if let Some(test_file) = self.infer_test_file(&normalized) {
                                self.coverage_map
                                    .entry(normalized.clone())
                                    .or_insert_with(Vec::new)
                                    .push(test_file.clone());
                                self.test_to_sources
                                    .entry(test_file)
                                    .or_insert_with(Vec::new)
                                    .push(normalized);
                            } else {
                                self.coverage_map
                                    .entry(normalized)
                                    .or_insert_with(Vec::new);
                            }
                        }
                    }
                }
            }
        }

        Ok(())
    }

    /// Parse tarpaulin JSON output
    fn parse_tarpaulin(&mut self, path: &Path) -> Result<()> {
        let content = fs::read_to_string(path)?;
        let coverage: serde_json::Value = serde_json::from_str(&content)
            .map_err(|e| AffectedTestsError::ParseError(format!("Invalid JSON: {}", e)))?;

        if let Some(files) = coverage.as_object() {
            for (file_path, data) in files {
                let normalized = self.normalize_path(file_path);

                // Tarpaulin format has covered lines info
                if let Some(obj) = data.as_object() {
                    if let Some(covered) = obj.get("covered").and_then(|c| c.as_u64()) {
                        if covered > 0 {
                            // File has coverage - map to test
                            if let Some(test_file) = self.infer_test_file(&normalized) {
                                self.coverage_map
                                    .entry(normalized.clone())
                                    .or_insert_with(Vec::new)
                                    .push(test_file.clone());
                                self.test_to_sources
                                    .entry(test_file)
                                    .or_insert_with(Vec::new)
                                    .push(normalized);
                            } else {
                                self.coverage_map
                                    .entry(normalized)
                                    .or_insert_with(Vec::new);
                            }
                        }
                    }
                }
            }
        }

        Ok(())
    }

    /// Parse Cobertura XML format (used by pytest-cov, coverage.py)
    fn parse_cobertura(&mut self, path: &Path) -> Result<()> {
        let content = fs::read_to_string(path)?;

        // Simple XML parsing without full XML parser
        // Look for <class> elements with filename and line coverage
        let class_re = Regex::new(r#"<class[^>]*filename="([^"]+)"[^>]*line-rate="([^"]+)"#)?;

        for cap in class_re.captures_iter(&content) {
            if let (Some(file_match), Some(rate_match)) = (cap.get(1), cap.get(2)) {
                let file_path = file_match.as_str();
                let line_rate: f64 = rate_match.as_str().parse().unwrap_or(0.0);

                if line_rate > 0.0 {
                    let normalized = self.normalize_path(file_path);

                    if let Some(test_file) = self.infer_test_file(&normalized) {
                        self.coverage_map
                            .entry(normalized.clone())
                            .or_insert_with(Vec::new)
                            .push(test_file.clone());
                        self.test_to_sources
                            .entry(test_file)
                            .or_insert_with(Vec::new)
                            .push(normalized);
                    } else {
                        self.coverage_map
                            .entry(normalized)
                            .or_insert_with(Vec::new);
                    }
                }
            }
        }

        Ok(())
    }

    /// Normalize a file path (remove leading ./, convert separators, etc.)
    fn normalize_path(&self, path: &str) -> String {
        let normalized = path.replace('\\', "/");
        let normalized = normalized.trim_start_matches("./").to_string();
        normalized
    }

    /// Infer test file from source file using common conventions
    fn infer_test_file(&self, source_path: &str) -> Option<String> {
        // Extract the base name without extension
        let path = Path::new(source_path);
        let stem = path.file_stem()?.to_str()?;

        // Check common test file patterns
        let parent = path.parent()?.to_str()?;

        // If already in a test directory, it's a test file
        if parent.contains("test") || parent.contains("spec") || parent.contains("__tests__") {
            return Some(source_path.to_string());
        }

        // Generate candidate test paths based on file type
        let ext = path.extension()?.to_str()?;

        match ext {
            "py" => {
                Some(format!("tests/test_{}.py", stem))
            }
            "rs" => {
                Some(format!("tests/{}_test.rs", stem))
            }
            "ts" | "tsx" | "js" | "jsx" => {
                Some(format!("src/{}.test.{}", stem, ext))
            }
            _ => None,
        }
    }

    /// Find tests that cover the changed source files
    pub fn find_covering_tests(&self, changed_files: &[String]) -> Vec<String> {
        let mut affected = HashSet::new();

        for changed in changed_files {
            let normalized = self.normalize_path(changed);

            // Direct match
            if let Some(tests) = self.coverage_map.get(&normalized) {
                affected.extend(tests.clone());
            }

            // Try without leading path components
            let filename = Path::new(&normalized)
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or(&normalized);

            for (source, tests) in &self.coverage_map {
                if source.ends_with(filename) {
                    affected.extend(tests.clone());
                }
            }
        }

        let mut result: Vec<_> = affected.into_iter().collect();
        result.sort();
        result
    }

    /// Check if coverage data is available
    pub fn has_coverage(&self) -> bool {
        self.has_coverage_data
    }

    /// Get all source files with coverage data
    pub fn covered_sources(&self) -> Vec<String> {
        let mut sources: Vec<_> = self.coverage_map.keys().cloned().collect();
        sources.sort();
        sources
    }

    /// Get all tests with coverage data
    pub fn tests_with_coverage(&self) -> Vec<String> {
        let mut tests: Vec<_> = self.test_to_sources.keys().cloned().collect();
        tests.sort();
        tests
    }
}

impl Default for CoverageDetector {
    fn default() -> Self {
        Self::new()
    }
}

/// Main affected tests analyzer
pub struct AffectedTestsAnalyzer {
    pattern_detector: PatternDetector,
    import_detector: ImportDetector,
    coverage_detector: CoverageDetector,
}

impl AffectedTestsAnalyzer {
    pub fn new() -> Result<Self> {
        Ok(Self {
            pattern_detector: PatternDetector::new()?,
            import_detector: ImportDetector::new(),
            coverage_detector: CoverageDetector::new(),
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

        // Load coverage data if needed
        if matches!(strategy, DetectionStrategy::Coverage | DetectionStrategy::All) {
            if let Err(e) = self.coverage_detector.load_coverage(project_dir) {
                eprintln!("Warning: Failed to load coverage data: {}", e);
            }
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
            DetectionStrategy::Coverage => {
                if self.coverage_detector.has_coverage() {
                    let tests = self.coverage_detector.find_covering_tests(changed_files);
                    affected_tests.extend(tests);
                } else {
                    eprintln!("Warning: No coverage data available, falling back to pattern-based detection");
                    for changed in changed_files {
                        let candidates = self.pattern_detector.find_test_candidates(changed);
                        for candidate in candidates {
                            if (project_dir.as_ref() as &Path).join(&candidate).exists() {
                                affected_tests.insert(candidate);
                            }
                        }
                    }
                }
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

                // Coverage-based
                if self.coverage_detector.has_coverage() {
                    let tests = self.coverage_detector.find_covering_tests(changed_files);
                    affected_tests.extend(tests);
                }
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
