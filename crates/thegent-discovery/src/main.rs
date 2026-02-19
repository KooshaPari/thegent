use serde::{Serialize, Deserialize};
use sysinfo::{ProcessExt, System, SystemExt, CpuExt, Signal};
use std::time::{SystemTime, UNIX_EPOCH};
use clap::Parser;

#[derive(Parser, Debug)]
#[command(author, version, about = "Native process discovery and session reaper for thegent", long_about = None)]
struct Args {
    /// Output snapshot as JSON (default)
    #[arg(short, long, default_value_t = true)]
    json: bool,

    /// Reap zombie/orphan agent processes
    #[arg(short, long)]
    reap: bool,

    /// Dry run: show what would be reaped without killing
    #[arg(short, long)]
    dry_run: bool,

    /// Minimum runtime in seconds to consider for reaping (default 2 hours)
    #[arg(short, long, default_value_t = 7200)]
    min_runtime: u64,
}

#[derive(Serialize, Deserialize, Debug)]
struct ProcessMetrics {
    pid: u32,
    name: String,
    cmd: Vec<String>,
    cpu_usage: f32,
    memory_kb: u64,
    virtual_memory_kb: u64,
    run_time_s: u64,
    parent_pid: Option<u32>,
}

#[derive(Serialize, Deserialize, Debug)]
struct SystemMetrics {
    total_memory_kb: u64,
    available_memory_kb: u64,
    cpu_usage_avg: f32,
    load_avg_1m: f64,
    load_avg_5m: f64,
    load_avg_15m: f64,
    uptime_s: u64,
}

#[derive(Serialize, Deserialize, Debug)]
struct DiscoverySnapshot {
    timestamp: f64,
    system: SystemMetrics,
    agents: Vec<ProcessMetrics>,
    clode_sessions: Vec<ProcessMetrics>,
    dex_sessions: Vec<ProcessMetrics>,
    mcp_servers: Vec<ProcessMetrics>,
    cursor_processes: Vec<ProcessMetrics>,
    zombie_candidates: Vec<u32>,
    reaped_count: usize,
}

fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    let mut sys = System::new_all();
    sys.refresh_all();
    
    std::thread::sleep(std::time::Duration::from_millis(100));
    sys.refresh_all();

    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs_f64();

    let load = sys.load_average();
    let system_metrics = SystemMetrics {
        total_memory_kb: sys.total_memory(),
        available_memory_kb: sys.available_memory(),
        cpu_usage_avg: sys.global_cpu_info().cpu_usage(),
        load_avg_1m: load.one,
        load_avg_5m: load.five,
        load_avg_15m: load.fifteen,
        uptime_s: sys.uptime(),
    };

    let mut snapshot = DiscoverySnapshot {
        timestamp: now,
        system: system_metrics,
        agents: Vec::new(),
        clode_sessions: Vec::new(),
        dex_sessions: Vec::new(),
        mcp_servers: Vec::new(),
        cursor_processes: Vec::new(),
        zombie_candidates: Vec::new(),
        reaped_count: 0,
    };

    for (pid, process) in sys.processes() {
        let name = process.name().to_string();
        let cmd = process.cmd().to_vec();
        let cmd_str = cmd.join(" ");

        let metrics = ProcessMetrics {
            pid: pid.as_u32(),
            name: name.clone(),
            cmd: cmd.clone(),
            cpu_usage: process.cpu_usage(),
            memory_kb: process.memory(),
            virtual_memory_kb: process.virtual_memory(),
            run_time_s: process.run_time(),
            parent_pid: process.parent().map(|p| p.as_u32()),
        };

        if cmd_str.contains("thegent") && (cmd_str.contains("serve") || cmd_str.contains("mcp")) {
            snapshot.mcp_servers.push(metrics);
        } else if cmd_str.contains("clode") || (cmd_str.contains("thegent") && cmd_str.contains("flash")) {
            snapshot.clode_sessions.push(metrics);
        } else if cmd_str.contains("dex") || (cmd_str.contains("thegent") && cmd_str.contains("run")) {
            snapshot.dex_sessions.push(metrics);
        } else if name.contains("agent") || cmd_str.contains("agent") {
            snapshot.agents.push(metrics);
        } else if name.contains("Cursor") || cmd_str.contains("Cursor") || name.contains("cursor-shell") {
            snapshot.cursor_processes.push(metrics);
        }
    }

    // Zombie detection and reaping
    for p in &snapshot.cursor_processes {
        // Candidate if low CPU and long runtime
        if p.cpu_usage < 0.1 && p.run_time_s > args.min_runtime {
            snapshot.zombie_candidates.push(p.pid);
            
            if args.reap {
                if args.dry_run {
                    eprintln!("DRY RUN: Would kill zombie candidate PID {}", p.pid);
                } else {
                    if let Some(proc) = sys.process(sysinfo::Pid::from(p.pid as usize)) {
                        if proc.kill_with(Signal::Term).is_some() {
                            snapshot.reaped_count += 1;
                        } else {
                            // Fallback to Kill if Term fails
                            proc.kill_with(Signal::Kill);
                            snapshot.reaped_count += 1;
                        }
                    }
                }
            }
        }
    }

    if args.json {
        println!("{}", serde_json::to_string_pretty(&snapshot).unwrap());
    } else {
        println!("Reaped {} processes", snapshot.reaped_count);
        println!("Identified {} zombie candidates", snapshot.zombie_candidates.len());
    }

    Ok(())
}
