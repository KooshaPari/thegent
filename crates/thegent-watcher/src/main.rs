use notify::{Config, RecommendedWatcher, RecursiveMode, Watcher};
use std::path::Path;
use serde::Serialize;
use std::sync::mpsc::channel;
use clap::Parser;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Path to watch
    #[arg(short, long, default_value = ".")]
    path: String,

    /// Recursive watch
    #[arg(short, long, default_value_t = true)]
    recursive: bool,

    /// Exclude patterns (simple contains check for now)
    #[arg(short, long)]
    exclude: Vec<String>,
}

#[derive(Serialize)]
struct WatchEvent {
    path: String,
    kind: String,
}

fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    let (tx, rx) = channel();

    let mut watcher = RecommendedWatcher::new(tx, Config::default())?;

    let path = Path::new(&args.path);
    let mode = if args.recursive {
        RecursiveMode::Recursive
    } else {
        RecursiveMode::NonRecursive
    };

    watcher.watch(path, mode)?;

    println!("Watching: {:?}", path);

    for res in rx {
        match res {
            Ok(event) => {
                for path in event.paths {
                    let path_str = path.to_string_lossy().to_string();
                    
                    // Simple exclude check
                    let mut excluded = false;
                    for pattern in &args.exclude {
                        if path_str.contains(pattern) {
                            excluded = true;
                            break;
                        }
                    }

                    if !excluded {
                        let watch_event = WatchEvent {
                            path: path_str,
                            kind: format!("{:?}", event.kind),
                        };
                        if let Ok(json) = serde_json::to_string(&watch_event) {
                            println!("{}", json);
                        }
                    }
                }
            }
            Err(e) => eprintln!("watch error: {:?}", e),
        }
    }

    Ok(())
}
