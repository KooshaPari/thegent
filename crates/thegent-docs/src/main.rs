//! thegent-docs CLI: Markdown frontmatter processor and documentation tools

use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use std::path::{Path, PathBuf};
use thegent_docs::*;

#[derive(Parser)]
#[command(name = "thegent-docs")]
#[command(about = "Markdown frontmatter/backmatter processor")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Audit markdown files for structure (frontmatter, H1, See also)
    Audit {
        /// Directory to audit
        #[arg(default_value = "docs")]
        dir: PathBuf,
    },
    /// Normalize markdown files (add frontmatter, See also sections)
    Normalize {
        /// Directory to normalize
        #[arg(default_value = "docs")]
        dir: PathBuf,
    },
    /// Extract frontmatter from markdown file
    Extract {
        /// Markdown file to process
        file: PathBuf,
    },
    /// Add frontmatter to markdown file
    AddFrontmatter {
        /// Markdown file
        file: PathBuf,
        /// Title
        #[arg(long)]
        title: Option<String>,
        /// Description
        #[arg(long)]
        description: Option<String>,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Audit { dir } => {
            audit_command(&dir)?;
        }
        Commands::Normalize { dir } => {
            normalize_command(&dir)?;
        }
        Commands::Extract { file } => {
            extract_command(&file)?;
        }
        Commands::AddFrontmatter {
            file,
            title,
            description,
        } => {
            add_frontmatter_command(&file, title, description)?;
        }
    }

    Ok(())
}

fn audit_command(dir: &Path) -> Result<()> {
    println!("📚 Auditing markdown files in: {}", dir.display());
    println!();

    let files = find_markdown_files(dir)?;
    println!("Found {} markdown files\n", files.len());

    let mut missing_h1 = Vec::new();
    let mut missing_see_also = Vec::new();

    for file in &files {
        match audit_markdown(file) {
            Ok(audit) => {
                if !audit.has_frontmatter && !audit.has_h1 {
                    missing_h1.push(audit.clone());
                }
                if !audit.has_see_also {
                    missing_see_also.push(audit.clone());
                }
            }
            Err(e) => {
                eprintln!("⚠️  Error auditing {}: {}", file.display(), e);
            }
        }
    }

    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!("📊 Audit Results");
    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!();

    if missing_h1.is_empty() {
        println!("✅ All files have frontmatter or H1");
    } else {
        println!("⚠️  Missing frontmatter/H1 ({} files):", missing_h1.len());
        for audit in missing_h1.iter().take(20) {
            println!("   - {}", audit.path.display());
        }
    }
    println!();

    if missing_see_also.is_empty() {
        println!("✅ All files have 'See also' section");
    } else {
        println!(
            "⚠️  Missing 'See also' section ({} files):",
            missing_see_also.len()
        );
        for audit in missing_see_also.iter().take(20) {
            println!("   - {}", audit.path.display());
        }
    }
    println!();

    Ok(())
}

fn normalize_command(dir: &Path) -> Result<()> {
    println!("📚 Normalizing markdown files in: {}", dir.display());
    println!();

    let files = find_markdown_files(dir)?;
    println!("Found {} markdown files\n", files.len());

    for file in &files {
        match load_markdown(file) {
            Ok(doc) => {
                // Check if needs frontmatter
                if doc.frontmatter.is_none() && !has_h1(&doc.body) {
                    println!("⚠️  {} needs frontmatter or H1", file.display());
                }
                // Check if needs See also
                if !has_see_also(&doc.body) {
                    println!("⚠️  {} needs 'See also' section", file.display());
                }
            }
            Err(e) => {
                eprintln!("⚠️  Error processing {}: {}", file.display(), e);
            }
        }
    }

    println!("\n✅ Normalization check complete");
    Ok(())
}

fn extract_command(file: &Path) -> Result<()> {
    let doc = load_markdown(file).with_context(|| format!("Failed to load {}", file.display()))?;

    if let Some(ref fm) = doc.frontmatter {
        println!("Frontmatter:");
        println!("{}", serde_yaml::to_string(fm)?);
    } else {
        println!("No frontmatter found");
    }

    let has_fm = doc.frontmatter.is_some();
    if let Some(title) = extract_title(&format!(
        "{}\n{}",
        if has_fm { "---\n---\n" } else { "" },
        doc.body
    )) {
        println!("\nTitle: {}", title);
    }

    Ok(())
}

fn add_frontmatter_command(
    file: &PathBuf,
    title: Option<String>,
    description: Option<String>,
) -> Result<()> {
    let content = std::fs::read_to_string(file)
        .with_context(|| format!("Failed to read {}", file.display()))?;

    let (existing_fm, body) = parse_markdown(&content)?;

    let mut frontmatter = existing_fm.unwrap_or_else(|| Frontmatter {
        title: None,
        description: None,
        date: None,
        author: None,
        tags: None,
        category: None,
        status: None,
        extra: std::collections::HashMap::new(),
    });

    if let Some(t) = title {
        frontmatter.title = Some(t);
    }
    if let Some(d) = description {
        frontmatter.description = Some(d);
    }

    let new_content = add_frontmatter(&body, &frontmatter)?;
    std::fs::write(file, new_content)
        .with_context(|| format!("Failed to write {}", file.display()))?;

    println!("✅ Added frontmatter to {}", file.display());
    Ok(())
}
