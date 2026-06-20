// SPDX-License-Identifier: MIT OR Apache-2.0
use clap::{Parser, Subcommand};
use std::env;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::net::TcpStream;
use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode, Stdio};
use std::thread;
use std::time::Duration;

/// CLI for starting and managing Tracera development services.
#[derive(Parser)]
#[command(name = "rtm-services")]
#[command(version = "0.1.0")]
#[command(about = "Manage Tracera local infrastructure and application services", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: ServiceCommand,
}

#[derive(Subcommand)]
enum ServiceCommand {
    /// Start PostgreSQL database
    Postgres,
    /// Start Dragonfly cache runtime (Redis-compatible)
    Dragonfly,
    /// Start Dragonfly cache runtime (Redis-compatible) - alias for Dragonfly
    Redis,
    /// Start NATS message broker with JetStream
    Nats,
    /// Start Neo4j graph database
    Neo4j,
    /// Start MinIO S3-compatible storage
    Minio,
    /// Start Temporal workflow server
    Temporal,
    /// Install + start all infrastructure via Homebrew
    BrewInfra,
    /// Start Go backend with air (hot reload)
    GoBackend,
    /// Start Python backend with uvicorn (hot reload)
    PythonBackend,
    /// Start frontend web app with Vite
    Frontend,
    /// Start all dependencies (PostgreSQL, Dragonfly, NATS)
    Deps,
    /// Stop all running services
    Stop,
}

fn print_info(msg: &str) {
    println!("\x1b[0;34mℹ️  {}\x1b[0m", msg);
}

fn print_success(msg: &str) {
    println!("\x1b[0;32m✅ {}\x1b[0m", msg);
}

fn print_warning(msg: &str) {
    println!("\x1b[1;33m⚠️  {}\x1b[0m", msg);
}

fn print_error(msg: &str) {
    eprintln!("\x1b[0;31m❌ {}\x1b[0m", msg);
}

fn is_port_open(port: u16) -> bool {
    TcpStream::connect_timeout(
        &format!("127.0.0.1:{}", port).parse().unwrap(),
        Duration::from_millis(150),
    )
    .is_ok()
}

fn find_repo_root() -> Result<PathBuf, String> {
    let mut dir = env::current_dir().map_err(|e| format!("Failed to get current directory: {}", e))?;
    loop {
        if dir.join("frontend").is_dir() && dir.join("backend").is_dir() {
            return Ok(dir);
        }
        if let Some(parent) = dir.parent() {
            dir = parent.to_path_buf();
        } else {
            break;
        }
    }
    // Also check standard location
    let standard = PathBuf::from("/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera");
    if standard.is_dir() {
        return Ok(standard);
    }
    Err("Could not find Tracera repository root (must contain backend/ and frontend/)".to_string())
}

fn start_postgres() -> bool {
    print_info("Starting PostgreSQL...");

    if is_port_open(5432) {
        print_success("PostgreSQL is already running");
        return true;
    }

    // Try starting PostgreSQL via Homebrew
    let mut started = false;
    if Command::new("brew").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_ok() {
        for formula in &["postgresql@17", "postgresql@14", "postgresql"] {
            if Command::new("brew")
                .args(["services", "start", formula])
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .status()
                .is_ok()
            {
                started = true;
                break;
            }
        }
    }

    if !started {
        // Fallback to pg_ctl directly
        let _ = Command::new("pg_ctl")
            .args(["-D", "/opt/homebrew/var/postgresql@17", "start"])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();
    }

    thread::sleep(Duration::from_secs(2));

    if is_port_open(5432) {
        print_success("PostgreSQL started");
        true
    } else {
        print_error("Failed to start PostgreSQL");
        false
    }
}

fn start_nats() -> bool {
    print_info("Starting NATS...");

    if is_port_open(4222) {
        print_success("NATS is already running on port 4222");
        return true;
    }

    let spawn_res = Command::new("nats-server")
        .args(["-js", "-D"])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn();

    if let Err(e) = spawn_res {
        print_error(&format!("Failed to spawn nats-server: {}", e));
        return false;
    }

    thread::sleep(Duration::from_secs(3));

    if is_port_open(4222) {
        print_success("NATS started with JetStream");
        true
    } else {
        print_error("Failed to start NATS");
        false
    }
}

fn start_neo4j() -> bool {
    print_info("Starting Neo4j...");

    if is_port_open(7687) {
        print_success("Neo4j is already running on port 7687");
        return true;
    }

    // Try starting via neo4j CLI first (prefers over brew to avoid launchctl hang)
    let mut cli_started = false;
    let neo4j_cmd = if Command::new("neo4j").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_ok() {
        Some("neo4j".to_string())
    } else if let Ok(output) = Command::new("brew").args(["--prefix", "neo4j"]).output() {
        let prefix = String::from_utf8_lossy(&output.stdout).trim().to_string();
        let path = Path::new(&prefix).join("bin").join("neo4j");
        if path.exists() {
            Some(path.to_string_lossy().to_string())
        } else {
            None
        }
    } else {
        None
    };

    if let Some(cmd) = neo4j_cmd {
        print_info(&format!("Starting Neo4j via CLI ({} start)...", cmd));
        if Command::new(&cmd).arg("start").stdout(Stdio::null()).stderr(Stdio::null()).status().is_ok() {
            cli_started = true;
            for _ in 0..90 {
                thread::sleep(Duration::from_millis(500));
                if is_port_open(7687) {
                    print_success("Neo4j started (port 7687)");
                    return true;
                }
            }
        }
    }

    if !cli_started {
        // Fallback to brew services start neo4j
        print_info("Trying brew services start neo4j...");
        let _ = Command::new("brew")
            .args(["services", "start", "neo4j"])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn();

        for _ in 0..60 {
            thread::sleep(Duration::from_millis(500));
            if is_port_open(7687) {
                print_success("Neo4j started (port 7687)");
                return true;
            }
        }
    }

    print_error("Neo4j did not become ready in time.");
    println!("\n  Start manually:  neo4j start");
    println!("  Or see startup errors with:  neo4j console");
    false
}

fn start_minio() -> bool {
    print_info("Starting MinIO (S3-compatible object storage)...");

    if Command::new("brew").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_err() {
        print_error("Homebrew required to manage MinIO. Install from https://brew.sh");
        return false;
    }

    // Install minio if missing
    if Command::new("minio").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_err() {
        print_info("Installing MinIO (brew install minio)...");
        let _ = Command::new("brew").args(["install", "minio"]).status();
    }

    let _ = Command::new("brew")
        .args(["services", "start", "minio"])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();

    let port = env::var("MINIO_PORT").unwrap_or_else(|_| "9000".to_string());
    let url = format!("http://127.0.0.1:{}", port);

    let mut ready = false;
    for _ in 0..30 {
        thread::sleep(Duration::from_millis(500));
        if is_port_open(port.parse().unwrap_or(9000)) {
            ready = true;
            break;
        }
    }

    if !ready {
        print_error("MinIO did not become ready. Check: brew services info minio");
        return false;
    }

    print_success(&format!("MinIO is up at {}", url));

    // Append S3 env vars to root .env if missing
    if let Ok(root) = find_repo_root() {
        let env_file = root.join(".env");
        if env_file.exists() {
            if let Ok(content) = fs::read_to_string(&env_file) {
                if !content.contains("S3_ENDPOINT=") {
                    print_info("Adding S3 vars to .env...");
                    if let Ok(mut file) = OpenOptions::new().append(true).open(&env_file) {
                        let block = "\n# MinIO (local) - added by rtm-services minio\nS3_ENDPOINT=http://127.0.0.1:9000\nS3_ACCESS_KEY_ID=minioadmin\nS3_SECRET_ACCESS_KEY=minioadmin\nS3_BUCKET=tracertm\nS3_REGION=us-east-1\n";
                        let _ = file.write_all(block.as_bytes());
                        print_success("S3 vars appended to .env");
                    }
                }
            }
        }

        // Create bucket via Go cmd if present
        let go_main = root.join("backend/cmd/create-minio-bucket/main.go");
        if go_main.exists() {
            print_info("Creating bucket 'tracertm'...");
            let mut cmd = Command::new("go");
            cmd.args(["run", "./cmd/create-minio-bucket/"])
                .current_dir(root.join("backend"));
            
            // Set required S3 env vars
            cmd.env("S3_ENDPOINT", "http://127.0.0.1:9000")
               .env("S3_ACCESS_KEY_ID", "minioadmin")
               .env("S3_SECRET_ACCESS_KEY", "minioadmin")
               .env("S3_BUCKET", "tracertm")
               .env("S3_REGION", "us-east-1");

            if cmd.status().is_ok() {
                print_success("Bucket created");
            } else {
                print_warning("Bucket creation skipped or failed");
            }
        }
    }

    println!("\nMinIO ready. API: http://127.0.0.1:9000  Console: http://127.0.0.1:9001 (minioadmin / minioadmin)");
    true
}

fn start_temporal() -> bool {
    print_info("Starting Temporal (workflow server)...");

    if Command::new("brew").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_err() {
        print_error("Homebrew required to manage Temporal. Install from https://brew.sh");
        return false;
    }

    if Command::new("temporal").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_err() {
        print_info("Installing Temporal CLI (brew install temporal)...");
        let _ = Command::new("brew").args(["install", "temporal"]).status();
    }

    if is_port_open(7233) {
        print_success("Temporal is already running on port 7233");
        return true;
    }

    if let Ok(root) = find_repo_root() {
        let temporal_dir = root.join(".temporal");
        let _ = fs::create_dir_all(&temporal_dir);
        let db_file = temporal_dir.join("dev.db");

        print_info(&format!("Starting Temporal server (dev mode, db: {})...", db_file.display()));
        
        let spawn_res = Command::new("temporal")
            .args(["server", "start-dev", "--db-filename", &db_file.to_string_lossy()])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn();

        if let Err(e) = spawn_res {
            print_error(&format!("Failed to start Temporal server: {}", e));
            return false;
        }

        let mut ready = false;
        for _ in 0..30 {
            thread::sleep(Duration::from_millis(500));
            if is_port_open(7233) {
                ready = true;
                break;
            }
        }

        if !ready {
            print_error("Temporal did not become ready.");
            return false;
        }

        print_success("Temporal started, gRPC: 127.0.0.1:7233");

        // Add TEMPORAL_HOST and namespace to .env if missing
        let env_file = root.join(".env");
        if env_file.exists() {
            if let Ok(content) = fs::read_to_string(&env_file) {
                let mut env_updates = String::new();
                if !content.contains("TEMPORAL_HOST=") {
                    env_updates.push_str("TEMPORAL_HOST=127.0.0.1:7233\n");
                }
                if !content.contains("TEMPORAL_NAMESPACE=") {
                    env_updates.push_str("TEMPORAL_NAMESPACE=default\n");
                }
                if !env_updates.is_empty() {
                    print_info("Adding Temporal vars to .env...");
                    if let Ok(mut file) = OpenOptions::new().append(true).open(&env_file) {
                        let _ = file.write_all(env_updates.as_bytes());
                        print_success("Temporal vars appended to .env");
                    }
                }
            }
        }

        // Ensure namespace exists
        let namespace = "default";
        let check_ns = Command::new("temporal")
            .args(["operator", "namespace", "describe", "--namespace", namespace])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();

        if !check_ns.is_ok_and(|s| s.success()) {
            print_info(&format!("Creating Temporal namespace: {}", namespace));
            let create_ns = Command::new("temporal")
                .args([
                    "operator",
                    "namespace",
                    "create",
                    "--namespace",
                    namespace,
                    "--description",
                    "TraceRTM dev namespace",
                ])
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .status();

            if create_ns.is_ok_and(|s| s.success()) {
                print_success("Temporal namespace created");
            } else {
                print_warning("Failed to create namespace automatically");
            }
        }

        println!("\nTemporal ready. gRPC: 127.0.0.1:7233  (run 'temporal workflow list' to verify)");
        return true;
    }

    false
}

fn start_dragonfly() -> bool {
    print_info("Starting Dragonfly cache runtime...");

    // Check if redis is already running
    if is_port_open(6379) {
        print_success("Cache runtime (Dragonfly/Redis) is already running");
        return true;
    }

    if Command::new("dragonfly").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_ok() {
        let spawn_res = Command::new("dragonfly")
            .args(["--port", "6379", "--dir", ".dragonfly"])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn();
        
        if spawn_res.is_ok() {
            thread::sleep(Duration::from_secs(3));
            if is_port_open(6379) {
                print_success("Dragonfly started");
                return true;
            }
        }
    }

    // Try Docker fallback
    if Command::new("docker").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_ok() {
        if let Ok(root) = find_repo_root() {
            let df_dir = root.join(".dragonfly");
            let _ = fs::create_dir_all(&df_dir);

            print_info("Spawning Dragonfly via Docker...");
            let spawn_res = Command::new("docker")
                .args([
                    "run",
                    "--rm",
                    "--name",
                    "tracera-dragonfly",
                    "-p",
                    "6379:6379",
                    "-v",
                    &format!("{}:/data", df_dir.to_string_lossy()),
                    "docker.dragonflydb.io/dragonflydb/dragonfly:latest",
                    "--dir",
                    "/data",
                ])
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .spawn();

            if spawn_res.is_ok() {
                thread::sleep(Duration::from_secs(3));
                if is_port_open(6379) {
                    print_success("Dragonfly started in Docker");
                    return true;
                }
            }
        }
    }

    print_error("Failed to start Dragonfly or Docker Dragonfly");
    false
}

fn run_brew_infra() -> bool {
    print_info("Installing and starting TraceRTM infra via Homebrew...");

    if Command::new("brew").arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().is_err() {
        print_error("Homebrew required. Install from https://brew.sh");
        return false;
    }

    let _ = Command::new("brew")
        .args(["tap", "minio/minio"])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();

    // Install postgres
    let mut pg_installed = false;
    for formula in &["postgresql@17", "postgresql@14", "postgresql"] {
        if Command::new("brew")
            .args(["list", formula])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok_and(|s| s.success())
        {
            pg_installed = true;
            break;
        }
    }
    if !pg_installed {
        print_info("Installing postgresql@17...");
        let _ = Command::new("brew").args(["install", "postgresql@17"]).status();
    }

    // Install other formulas
    for formula in &["nats-server", "neo4j", "temporal", "minio"] {
        if !Command::new("brew")
            .args(["list", formula])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok_and(|s| s.success())
        {
            print_info(&format!("Installing {}...", formula));
            let _ = Command::new("brew").args(["install", formula]).status();
        }
    }

    print_info("Starting all brew services...");
    let _ = Command::new("brew").args(["services", "start", "postgresql@17"]).status();
    let _ = Command::new("brew").args(["services", "start", "nats-server"]).status();
    let _ = Command::new("brew").args(["services", "start", "neo4j"]).status();
    let _ = Command::new("brew").args(["services", "start", "temporal"]).status();
    let _ = Command::new("brew").args(["services", "start", "minio"]).status();

    print_success("Brew services started. Verifying ports...");
    for _ in 0..30 {
        thread::sleep(Duration::from_millis(500));
        if is_port_open(5432) && is_port_open(6379) && is_port_open(4222) && is_port_open(7687) {
            print_success("PostgreSQL, Dragonfly, NATS, Neo4j are ready.");
            break;
        }
    }

    true
}

fn start_go_backend() -> bool {
    print_info("Starting Go Backend...");

    if let Ok(root) = find_repo_root() {
        let go_dir = root.join("backend");
        if !go_dir.join(".env").exists() {
            print_error("Go backend .env not found. Run setup-env.sh first");
            return false;
        }

        print_info("Starting with air (hot reload)...");
        print_warning("Press Ctrl+C to stop");

        // Ensure air is installed
        if Command::new("air").arg("-v").stdout(Stdio::null()).stderr(Stdio::null()).status().is_err() {
            print_warning("air not found. Installing...");
            let _ = Command::new("go")
                .args(["install", "github.com/air-verse/air@latest"])
                .status();
        }

        let mut child = Command::new("air")
            .current_dir(go_dir)
            .spawn()
            .expect("Failed to start air");

        let _ = child.wait();
        return true;
    }
    false
}

fn start_python_backend() -> bool {
    print_info("Starting Python Backend...");

    if let Ok(root) = find_repo_root() {
        if !root.join(".env").exists() {
            print_error("Python backend .env not found. Run setup-env.sh first");
            return false;
        }

        if !root.join(".venv").exists() {
            print_warning("Virtual environment not found. Syncing with uv...");
            let _ = Command::new("uv").arg("sync").current_dir(&root).status();
        }

        print_info("Starting with uvicorn (hot reload)...");
        print_warning("Press Ctrl+C to stop");

        let mut child = Command::new("uv")
            .args(["run", "uvicorn", "tracertm.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
            .current_dir(&root)
            .spawn()
            .expect("Failed to start python backend");

        let _ = child.wait();
        return true;
    }
    false
}

fn start_frontend() -> bool {
    print_info("Starting Frontend...");

    if let Ok(root) = find_repo_root() {
        let web_dir = root.join("frontend/apps/web");
        if !web_dir.join(".env.local").exists() {
            print_error("Frontend .env.local not found. Run setup-env.sh first");
            return false;
        }

        if !web_dir.join("node_modules").exists() {
            print_warning("Dependencies not installed. Running bun install...");
            let _ = Command::new("bun").arg("install").current_dir(&web_dir).status();
        }

        print_info("Starting with Vite dev server (hot reload)...");
        print_warning("Press Ctrl+C to stop");

        let mut child = Command::new("bun")
            .args(["run", "dev"])
            .current_dir(&web_dir)
            .spawn()
            .expect("Failed to start frontend");

        let _ = child.wait();
        return true;
    }
    false
}

fn start_deps() -> bool {
    print_info("Starting all dependencies (PostgreSQL, Dragonfly, NATS)...");
    let pg = start_postgres();
    let df = start_dragonfly();
    let nats = start_nats();

    if pg && df && nats {
        print_success("All dependencies started successfully!");
        println!("\nNow start backends and frontend in separate terminals:");
        println!("  Terminal 1: rtm-services go-backend");
        println!("  Terminal 2: rtm-services python-backend");
        println!("  Terminal 3: rtm-services frontend");
        true
    } else {
        print_error("One or more dependencies failed to start");
        false
    }
}

fn stop_all() -> bool {
    print_info("Stopping all services...");

    // Stop Dragonfly/Redis
    if is_port_open(6379) {
        let _ = Command::new("redis-cli")
            .arg("shutdown")
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();
        print_success("Cache runtime stopped");
    }

    // Stop NATS
    let check_nats = Command::new("pgrep")
        .arg("nats-server")
        .stdout(Stdio::null())
        .status();

    if check_nats.is_ok_and(|s| s.success()) {
        let _ = Command::new("pkill").arg("nats-server").status();
        print_success("NATS stopped");
    }

    print_info("PostgreSQL left running (use 'brew services stop postgresql' to stop)");
    print_success("Services stopped");
    true
}

fn main() -> ExitCode {
    let cli = Cli::parse();

    let success = match cli.command {
        ServiceCommand::Postgres => start_postgres(),
        ServiceCommand::Dragonfly => start_dragonfly(),
        ServiceCommand::Redis => start_dragonfly(),
        ServiceCommand::Nats => start_nats(),
        ServiceCommand::Neo4j => start_neo4j(),
        ServiceCommand::Minio => start_minio(),
        ServiceCommand::Temporal => start_temporal(),
        ServiceCommand::BrewInfra => run_brew_infra(),
        ServiceCommand::GoBackend => start_go_backend(),
        ServiceCommand::PythonBackend => start_python_backend(),
        ServiceCommand::Frontend => start_frontend(),
        ServiceCommand::Deps => start_deps(),
        ServiceCommand::Stop => stop_all(),
    };

    if success {
        ExitCode::SUCCESS
    } else {
        ExitCode::from(1)
    }
}
