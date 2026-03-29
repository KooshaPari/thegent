//! BKM-02: thegent-parser CLI binary.
//!
//! Provides subprocess access to parsing functions for any Python interpreter.
//! Output: JSON to stdout.

use clap::{Parser, Subcommand};
use std::io::{self, Read};

#[derive(Parser)]
#[command(name = "thegent-parser", version, about = "BKM-02: Parser binary")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Extract XML tags from text (reads from stdin)
    XmlTags {
        /// Comma-separated list of allowed tags (optional)
        #[arg(short, long)]
        tags: Option<String>,
        /// Case sensitive matching
        #[arg(short, long)]
        case_sensitive: bool,
    },
    /// Remove think blocks from text (reads from stdin)
    StripThink,
    /// Strip noise from text (reads from stdin)
    StripNoise {
        /// Profile: plain, jsonl, or leading
        #[arg(short, long, default_value = "plain")]
        profile: String,
    },
    /// Parse a JSONL file
    ParseJsonl {
        /// Path to JSONL file
        path: String,
    },
}

fn main() -> io::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::XmlTags {
            tags,
            case_sensitive,
        } => {
            let mut input = String::new();
            io::stdin().read_to_string(&mut input)?;

            let allowed: Option<Vec<&str>> = tags
                .as_ref()
                .map(|t| t.split(',').map(|s| s.trim()).collect());

            // Simple XML tag extraction (inline to avoid lib dependency)
            let result = extract_xml_tags_simple(&input, allowed.as_deref(), case_sensitive);
            println!("{}", serde_json::to_string_pretty(&result)?);
        }
        Commands::StripThink => {
            let mut input = String::new();
            io::stdin().read_to_string(&mut input)?;
            let result = strip_think_blocks_simple(&input);
            print!("{}", result);
        }
        Commands::StripNoise { profile } => {
            let mut input = String::new();
            io::stdin().read_to_string(&mut input)?;
            let result = strip_noise_simple(&input, &profile);
            print!("{}", result);
        }
        Commands::ParseJsonl { path } => {
            let content = std::fs::read_to_string(&path)?;
            let results: Vec<serde_json::Value> = content
                .lines()
                .filter(|l| !l.trim().is_empty())
                .filter_map(|l| serde_json::from_str(l).ok())
                .collect();
            println!("{}", serde_json::to_string_pretty(&results)?);
        }
    }

    Ok(())
}

// Simple implementations (duplicated to avoid lib dependency issues)
fn extract_xml_tags_simple(
    text: &str,
    allowed_tags: Option<&[&str]>,
    case_sensitive: bool,
) -> serde_json::Value {
    use regex::Regex;
    let re = Regex::new(r"<([A-Za-z0-9_\-]+)>").unwrap();
    let mut tags = serde_json::Map::new();
    let mut search_start = 0;

    while let Some(cap) = re.captures(&text[search_start..]) {
        let key = cap.get(1).map(|m| m.as_str()).unwrap_or("");
        let open_full = cap.get(0).unwrap();
        let content_start = search_start + open_full.end();
        let closing = format!("</{}>", key);

        if let Some(close_pos) = text[content_start..].find(&closing) {
            let val = text[content_start..content_start + close_pos].trim();
            let include = match allowed_tags {
                None => true,
                Some(t) => {
                    if case_sensitive {
                        t.contains(&key)
                    } else {
                        t.iter().any(|tag| tag.eq_ignore_ascii_case(key))
                    }
                }
            };
            if include {
                tags.insert(key.to_string(), serde_json::Value::String(val.to_string()));
            }
            search_start = content_start + close_pos + closing.len();
        } else {
            search_start = content_start;
        }
    }
    serde_json::Value::Object(tags)
}

fn strip_think_blocks_simple(text: &str) -> String {
    use regex::Regex;
    let re = Regex::new(r"(?s)<think.*?>.*?</think\s*>").unwrap();
    re.replace_all(text, "").trim().to_string()
}

fn strip_noise_simple(text: &str, profile: &str) -> String {
    use regex::Regex;
    let patterns = [
        (Regex::new(r"^\[TIME CONSTRAINT").ok(), "leading"),
        (
            Regex::new(r"^You have approximately \d+ tool calls").ok(),
            "leading",
        ),
        (Regex::new(r"^\s*OK\s*$").ok(), "leading"),
        (
            Regex::new(r#"^\s*\{\s*"type"\s*:\s*"turn\.(completed|started)"#).ok(),
            "jsonl",
        ),
        (
            Regex::new(r#"^\s*\{\s*"type"\s*:\s*"thread\.started"#).ok(),
            "jsonl",
        ),
        (Regex::new(r"^Total usage est:").ok(), "plain"),
        (Regex::new(r"^Total duration \(API\):").ok(), "plain"),
        (Regex::new(r"^Usage by model:").ok(), "plain"),
    ];

    text.lines()
        .filter(|line| {
            let trimmed = line.trim();
            if trimmed.is_empty() {
                return true;
            }

            for (re, pat_profile) in &patterns {
                if let Some(regex) = re {
                    let matches_profile = match *pat_profile {
                        "leading" => profile == "leading" || profile == "plain",
                        "jsonl" => profile == "jsonl" || profile == "plain",
                        "plain" => profile == "plain",
                        _ => false,
                    };
                    if matches_profile && regex.is_match(trimmed) {
                        return false;
                    }
                }
            }
            true
        })
        .collect::<Vec<_>>()
        .join("\n")
}
