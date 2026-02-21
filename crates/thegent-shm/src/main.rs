//! BKM-05: thegent-shm CLI binary.
//!
//! Provides subprocess access to SHM state for any Python interpreter.
//! Output: JSON to stdout.
//!
//! Usage:
//!   thegent-shm --path /path/to/state.shm <command> [args]
//!
//! Commands:
//!   init                              - Initialize SHM file
//!   xp                                - Get XP state
//!   xp-award <amount>                 - Award XP
//!   health                            - Get health score
//!   health-set <score>                - Set health score
//!   provider <name>                   - Get provider metrics
//!   provider-update <name> <req> <ok> <ms>  - Update provider
//!   failure <target> <category>       - Record failure
//!   router                            - Get router metrics
//!   router-update <lif> <thg> <chg> <hyst>  - Update router metrics

use clap::{Parser, Subcommand};
use serde_json::json;
use std::path::PathBuf;
use thegent_shm::SHMInterface;
use std::io;

#[derive(Parser)]
#[command(name = "thegent-shm", version, about = "BKM-05: SHM state binary")]
struct Cli {
    /// Path to SHM file
    #[arg(short, long, default_value = "state.shm")]
    path: PathBuf,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize SHM file
    Init,
    /// Get XP state
    Xp,
    /// Award XP
    XpAward { amount: u64 },
    /// Get health score
    Health,
    /// Set health score
    HealthSet { score: f64 },
    /// Get provider metrics
    Provider { name: String },
    /// Update provider stats
    ProviderUpdate { name: String, requests: u64, successes: u64, latency_ms: u32 },
    /// Record a failure
    Failure { target: String, category: i32 },
    /// Get router metrics
    Router,
    /// Update router metrics
    RouterUpdate { lifecycle: u64, thegent: u64, changes: u64, hysteresis: u64 },
    /// Record resource usage
    Resource { pid: u32, cpu: f32, memory_kb: u64 },
}

fn main() -> io::Result<()> {
    let cli = Cli::parse();

    // Handle init specially (does not need existing SHM)
    if matches!(cli.command, Commands::Init) {
        SHMInterface::open(&cli.path)?;
        println!("{}", json!({"status": "initialized", "path": cli.path.to_string_lossy()}));
        return Ok(());
    }

    // For all other commands, open existing SHM
    let mut shm = SHMInterface::open(&cli.path)?;

    let result = match cli.command {
        Commands::Init => unreachable!(),
        Commands::Xp => {
            let state = shm.do_get_xp_state();
            json!({"total_xp": state.total_xp, "level": state.level})
        }
        Commands::XpAward { amount } => {
            shm.do_award_xp(amount)?;
            let state = shm.do_get_xp_state();
            json!({"total_xp": state.total_xp, "level": state.level})
        }
        Commands::Health => {
            let score = shm.do_get_health_score();
            json!({"health_score": score})
        }
        Commands::HealthSet { score } => {
            shm.do_set_health_score(score)?;
            json!({"health_score": score})
        }
        Commands::Provider { name } => {
            if let Some(provider) = shm.do_get_provider_metrics(&name) {
                json!({
                    "name": name,
                    "request_count": provider.request_count,
                    "success_count": provider.success_count,
                    "failure_count": provider.failure_count,
                    "latency_ms": provider.latency_p50_ms,
                    "success_rate": provider.success_rate,
                    "last_updated": provider.last_updated,
                })
            } else {
                json!({"error": "provider not found"})
            }
        }
        Commands::ProviderUpdate { name, requests, successes, latency_ms } => {
            shm.do_update_provider(name.clone(), requests, successes, latency_ms)?;
            json!({"status": "updated", "name": name})
        }
        Commands::Failure { target, category } => {
            shm.do_record_failure(target.clone(), category)?;
            json!({"status": "recorded", "target": target})
        }
        Commands::Router => {
            let m = shm.do_get_router_metrics();
            json!({
                "total_decisions": m.total_decisions,
                "lifecycle_count": m.lifecycle_count,
                "thegent_count": m.thegent_count,
                "route_changes": m.route_changes,
                "hysteresis_activations": m.hysteresis_activations,
            })
        }
        Commands::RouterUpdate { lifecycle, thegent, changes, hysteresis } => {
            shm.do_update_router_metrics(lifecycle, thegent, changes, hysteresis)?;
            let m = shm.do_get_router_metrics();
            json!({"status": "updated", "total_decisions": m.total_decisions})
        }
        Commands::Resource { pid, cpu, memory_kb } => {
            shm.do_record_resource_usage(pid, cpu, memory_kb)?;
            json!({"status": "recorded", "pid": pid})
        }
    };

    println!("{}", serde_json::to_string_pretty(&result)?);
    Ok(())
}
