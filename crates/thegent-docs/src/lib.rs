//! thegent-docs: Markdown frontmatter/backmatter processor
//!
//! Provides fast, type-safe processing of markdown files with YAML frontmatter
//! and backmatter support.

use anyhow::Result;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use thiserror::Error;

/// Frontmatter metadata extracted from markdown
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Frontmatter {
    pub title: Option<String>,
    pub description: Option<String>,
    pub date: Option<String>,
    pub author: Option<String>,
    pub tags: Option<Vec<String>>,
    pub category: Option<String>,
    pub status: Option<String>,
    #[serde(flatten)]
    pub extra: HashMap<String, serde_yaml::Value>,
}

/// Parsed markdown document with frontmatter and body
#[derive(Debug, Clone)]
pub struct MarkdownDoc {
    pub frontmatter: Option<Frontmatter>,
    pub body: String,
    pub path: PathBuf,
}

#[derive(Error, Debug)]
pub enum DocsError {
    #[error("Failed to read file: {0}")]
    ReadError(#[from] std::io::Error),
    #[error("Failed to parse YAML frontmatter: {0}")]
    YamlError(#[from] serde_yaml::Error),
    #[error("Invalid frontmatter delimiter")]
    InvalidDelimiter,
    #[error("File not found: {0}")]
    NotFound(PathBuf),
}

/// Extract frontmatter and body from markdown content
pub fn parse_markdown(content: &str) -> Result<(Option<Frontmatter>, String), DocsError> {
    // Check for frontmatter delimiter
    if !content.starts_with("---\n") {
        return Ok((None, content.to_string()));
    }

    // Find closing delimiter
    let end_delimiter = content[4..]
        .find("\n---\n")
        .or_else(|| content[4..].find("\n---"))
        .ok_or(DocsError::InvalidDelimiter)?;

    let frontmatter_text = &content[4..end_delimiter + 4];
    let body = &content[end_delimiter + 9..];

    // Parse YAML frontmatter
    let frontmatter: Frontmatter = serde_yaml::from_str(frontmatter_text)?;

    Ok((Some(frontmatter), body.to_string()))
}

/// Extract title from markdown (frontmatter or first H1)
pub fn extract_title(content: &str) -> Option<String> {
    // Try frontmatter first
    if let Ok((Some(fm), _)) = parse_markdown(content) {
        if let Some(title) = fm.title {
            return Some(title);
        }
    }

    // Try first H1
    let h1_regex = Regex::new(r"^#\s+(.+)$").ok()?;
    for line in content.lines() {
        if let Some(caps) = h1_regex.captures(line) {
            return Some(caps.get(1)?.as_str().trim().to_string());
        }
    }

    None
}

/// Check if markdown has frontmatter
pub fn has_frontmatter(content: &str) -> bool {
    content.starts_with("---\n")
}

/// Check if markdown has H1 heading
pub fn has_h1(content: &str) -> bool {
    let h1_regex = Regex::new(r"^#\s+").ok().unwrap();
    content.lines().any(|line| h1_regex.is_match(line))
}

/// Check if markdown has "See also" section
pub fn has_see_also(content: &str) -> bool {
    let see_also_regex = Regex::new(r"(?i)^##\s+(See\s+also|References|Related)")
        .ok()
        .unwrap();
    content.lines().any(|line| see_also_regex.is_match(line))
}

/// Load and parse markdown file
pub fn load_markdown(path: &Path) -> Result<MarkdownDoc, DocsError> {
    let content = std::fs::read_to_string(path).map_err(DocsError::from)?;

    let (frontmatter, body) = parse_markdown(&content)?;

    Ok(MarkdownDoc {
        frontmatter,
        body,
        path: path.to_path_buf(),
    })
}

/// Add or update frontmatter in markdown content
pub fn add_frontmatter(content: &str, frontmatter: &Frontmatter) -> Result<String> {
    let (_, body) = parse_markdown(content)?;

    let yaml = serde_yaml::to_string(frontmatter)?;
    Ok(format!("---\n{}\n---\n\n{}", yaml.trim_end(), body))
}

/// Generate "See also" section from related files
pub fn generate_see_also_section(related_paths: &[PathBuf]) -> String {
    if related_paths.is_empty() {
        return String::new();
    }

    let mut section = String::from("## See Also\n\n");
    for path in related_paths {
        let name = path
            .file_stem()
            .and_then(|s| s.to_str())
            .unwrap_or("unknown")
            .replace("_", " ")
            .replace("-", " ");
        section.push_str(&format!("- [{}]({})\n", name, path.display()));
    }
    section.push('\n');

    section
}

/// Audit markdown file structure
#[derive(Debug, Clone)]
pub struct AuditResult {
    pub path: PathBuf,
    pub has_frontmatter: bool,
    pub has_h1: bool,
    pub has_see_also: bool,
    pub title: Option<String>,
}

/// Audit a markdown file
pub fn audit_markdown(path: &Path) -> Result<AuditResult, DocsError> {
    let content = std::fs::read_to_string(path).map_err(DocsError::from)?;

    let (frontmatter, body) = parse_markdown(&content)?;
    let full_content = format!(
        "{}{}",
        if let Some(ref fm) = frontmatter {
            format!(
                "---\n{}\n---\n",
                serde_yaml::to_string(fm).map_err(DocsError::from)?
            )
        } else {
            String::new()
        },
        body
    );

    Ok(AuditResult {
        path: path.to_path_buf(),
        has_frontmatter: frontmatter.is_some(),
        has_h1: has_h1(&full_content),
        has_see_also: has_see_also(&full_content),
        title: extract_title(&full_content),
    })
}

/// Find all markdown files in directory
pub fn find_markdown_files(dir: &Path) -> Result<Vec<PathBuf>> {
    let mut files = Vec::new();

    for entry in walkdir::WalkDir::new(dir)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        if entry.file_type().is_file() {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("md") {
                files.push(path.to_path_buf());
            }
        }
    }

    Ok(files)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_markdown_with_frontmatter() {
        let content = r#"---
title: Test Document
description: A test
---
# Main Content
Hello world!
"#;

        let (fm, body) = parse_markdown(content).unwrap();
        assert!(fm.is_some());
        assert_eq!(
            fm.as_ref().unwrap().title,
            Some("Test Document".to_string())
        );
        assert!(body.contains("Main Content"));
    }

    #[test]
    fn test_parse_markdown_without_frontmatter() {
        let content = "# Main Content\nHello world!";
        let (fm, body) = parse_markdown(content).unwrap();
        assert!(fm.is_none());
        assert_eq!(body, content);
    }

    #[test]
    fn test_extract_title_from_h1() {
        let content = "# My Title\nContent here";
        assert_eq!(extract_title(content), Some("My Title".to_string()));
    }

    #[test]
    fn test_has_see_also() {
        let content = "Content\n## See Also\n- Link";
        assert!(has_see_also(content));
    }
}
