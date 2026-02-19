//! Rust replacement for scripts/audit-md-structure.sh
//! Audits markdown files for proper structure (frontmatter, H1, See also)

use anyhow::Result;
use clap::Parser;
use std::path::PathBuf;
use thegent_docs::*;

#[derive(Parser)]
#[command(name = "audit-md-structure")]
#[command(about = "Audit markdown files for structure (frontmatter, H1, See also)")]
struct Args {
    /// Directory to audit
    #[arg(default_value = "docs")]
    dir: PathBuf,
}

fn main() -> Result<()> {
    let args = Args::parse();

    println!("📚 Auditing MD documentation structure...");
    println!();

    let files = find_markdown_files(&args.dir)?;
    let total = files.len();

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
    println!("Total MD files audited: {}", total);
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
        println!("⚠️  Missing 'See also' section ({} files):", missing_see_also.len());
        for audit in missing_see_also.iter().take(20) {
            println!("   - {}", audit.path.display());
        }
    }
    println!();

    println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    println!();
    println!("Next steps:");
    println!("  1. Add frontmatter/H1 to files missing it");
    println!("  2. Add 'See also' sections to files missing them");
    println!("  3. Standardize heading levels");

    Ok(())
}
