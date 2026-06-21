// SPDX-License-Identifier: MIT OR Apache-2.0
use clap::{Parser, ValueEnum};
use serde_json;
use std::collections::HashMap;
use std::io::{self, Write};

use thegent_tool_detect::ToolDetector;

#[derive(Parser)]
#[command(name = "thegent-tool-detect")]
#[command(about = "Fast tool detection with intelligent caching", long_about = None)]
#[command(version)]
struct Cli {
    /// Tool name to detect (if not provided, detects all tools)
    tool: Option<String>,

    /// Output format
    #[arg(short, long, value_enum, default_value = "human")]
    format: OutputFormat,

    /// Clear cache before detection
    #[arg(short, long)]
    clear_cache: bool,

    /// Show cache statistics
    #[arg(long)]
    cache_stats: bool,
}

#[derive(Clone, ValueEnum)]
enum OutputFormat {
    Human,
    Json,
    Shell,
}

fn main() {
    let cli = Cli::parse();
    let detector = ToolDetector::new();

    // Show cache stats if requested
    if cli.cache_stats {
        let stats = detector.cache_stats();
        if stats.exists {
            println!("Cache Statistics:");
            println!("  Tools cached: {}", stats.tool_count);
            println!("  Age: {} seconds", stats.age_seconds);
            println!("  Valid: {}", if stats.is_valid { "yes" } else { "no (expired)" });
        } else {
            println!("No cache found");
        }
        return;
    }

    // Clear cache if requested
    if cli.clear_cache {
        match detector.clear_cache() {
            Ok(_) => eprintln!("Cache cleared"),
            Err(e) => {
                eprintln!("Warning: Failed to clear cache: {}", e);
            }
        }
    }

    // Detect tools
    if let Some(tool_name) = &cli.tool {
        // Single tool detection
        match detector.detect_one(tool_name) {
            Some(path) => {
                match cli.format {
                    OutputFormat::Json => {
                        let json = serde_json::json!({ tool_name: path });
                        println!("{}", serde_json::to_string_pretty(&json).unwrap());
                    }
                    OutputFormat::Shell => {
                        let var_name = tool_name.to_uppercase() + "_CMD";
                        println!("export {}=\"{}\"", var_name, path);
                    }
                    OutputFormat::Human => {
                        println!("{}", path);
                    }
                }
            }
            None => {
                eprintln!("Tool '{}' not found in PATH", tool_name);
                std::process::exit(1);
            }
        }
    } else {
        // Detect all tools
        let tools = detector.detect_all();

        match cli.format {
            OutputFormat::Json => {
                println!("{}", serde_json::to_string_pretty(&tools).unwrap());
            }
            OutputFormat::Shell => {
                for (key, path) in &tools {
                    let var_name = key.to_uppercase() + "_CMD";
                    println!("export {}=\"{}\"", var_name, path);
                }
            }
            OutputFormat::Human => {
                if tools.is_empty() {
                    println!("No tools detected.");
                } else {
                    println!("Detected {} tools:", tools.len());
                    let mut sorted: Vec<_> = tools.iter().collect();
                    sorted.sort_by_key(|(k, _)| *k);
                    for (key, path) in sorted {
                        println!("  {}: {}", key, path);
                    }
                }
            }
        }
    }
}
