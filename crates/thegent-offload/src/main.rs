use anyhow::{Context, Result};
use axum::{
    extract::{Request, State},
    http::StatusCode,
    middleware::{self, Next},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use chrono::Utc;
use clap::{Parser, Subcommand};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use thegent_offload::{
    ExecutionRequest, ExecutionResponse, ExecutionStatus, WorkerInfo, WorkerStatus,
};
use tracing::{error, info, Level};
use tracing_subscriber::FmtSubscriber;
use uuid::Uuid;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Start the remote offload executor (Worker)
    Serve {
        #[arg(long, default_value = "0.0.0.0")]
        host: String,
        #[arg(long, default_value_t = 9000)]
        port: u16,
        #[arg(long)]
        token: Option<String>,
        #[arg(long)]
        allow_worktrees: bool,
    },
    /// Send a task to a remote offload executor (Client)
    Run {
        #[arg(long)]
        worker_url: String,
        #[arg(long)]
        prompt: String,
        #[arg(long)]
        token: Option<String>,
        #[arg(long)]
        cwd: Option<PathBuf>,
        #[arg(long)]
        timeout: Option<u32>,
    },
}

struct AppState {
    token: Option<String>,
    active_tasks: tokio::sync::Mutex<HashMap<Uuid, ExecutionStatus>>,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Setup tracing
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber).expect("setting default subscriber failed");

    let cli = Cli::parse();

    match cli.command {
        Commands::Serve {
            host,
            port,
            token,
            allow_worktrees: _,
        } => {
            info!("Starting thegent offload server on {}:{}", host, port);
            if let Some(ref t) = token {
                info!(
                    "Authentication enabled with token: ****{}",
                    &t[t.len().max(4) - 4..]
                );
            } else {
                info!("Authentication disabled (NOT RECOMMENDED for public tunnels)");
            }

            let state = Arc::new(AppState {
                token,
                active_tasks: tokio::sync::Mutex::new(HashMap::new()),
            });

            let app = Router::new()
                .route("/v1/health", get(health_handler))
                .route("/v1/execute", post(execute_handler))
                .route("/v1/status/:id", get(status_handler))
                .layer(middleware::from_fn_with_state(
                    state.clone(),
                    auth_middleware,
                ))
                .with_state(state);

            let listener = tokio::net::TcpListener::bind(format!("{}:{}", host, port))
                .await
                .context("Failed to bind to address")?;

            axum::serve(listener, app).await.context("Server error")?;
        }
        Commands::Run {
            worker_url,
            prompt,
            token,
            cwd,
            timeout,
        } => {
            info!("Offloading task to worker at {}", worker_url);
            run_client(worker_url, prompt, token, cwd, timeout).await?;
        }
    }

    Ok(())
}

async fn auth_middleware(
    State(state): State<Arc<AppState>>,
    req: Request,
    next: Next,
) -> Result<impl IntoResponse, (StatusCode, &'static str)> {
    if let Some(ref expected_token) = state.token {
        let auth_header = req.headers().get("Authorization");
        match auth_header {
            Some(header_value) => {
                let header_str = header_value
                    .to_str()
                    .map_err(|_| (StatusCode::BAD_REQUEST, "Invalid Auth header"))?;
                if !header_str.starts_with("Bearer ") || &header_str[7..] != expected_token {
                    return Err((StatusCode::UNAUTHORIZED, "Unauthorized"));
                }
            }
            None => return Err((StatusCode::UNAUTHORIZED, "Missing Authorization header")),
        }
    }
    Ok(next.run(req).await)
}

async fn health_handler(State(state): State<Arc<AppState>>) -> Json<WorkerInfo> {
    let tasks = state.active_tasks.lock().await;
    Json(WorkerInfo {
        id: "worker-01".to_string(), // In production, generate or load worker ID
        hostname: gethostname::gethostname().to_string_lossy().to_string(),
        os: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
        capabilities: vec!["git".to_string(), "rust".to_string(), "python".to_string()],
        status: WorkerStatus::Busy(tasks.len() as u32),
    })
}

async fn execute_handler(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<ExecutionRequest>,
) -> Json<ExecutionResponse> {
    let task_id = payload.id;
    info!("Received execution request: {}", task_id);

    // For now, simple synchronous-looking mock execution
    // In production, spawn a background task and return 202 Accepted

    let mut tasks = state.active_tasks.lock().await;
    tasks.insert(task_id, ExecutionStatus::Running);
    drop(tasks);

    // Mock execution
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;

    let mut tasks = state.active_tasks.lock().await;
    tasks.insert(task_id, ExecutionStatus::Completed);

    Json(ExecutionResponse {
        request_id: task_id,
        status: ExecutionStatus::Completed,
        stdout: Some("Mock output from remote worker".to_string()),
        stderr: None,
        exit_code: Some(0),
        duration_ms: 2000,
        metrics: None,
    })
}

async fn status_handler(
    State(state): State<Arc<AppState>>,
    axum::extract::Path(id): axum::extract::Path<Uuid>,
) -> Json<ExecutionStatus> {
    let tasks = state.active_tasks.lock().await;
    let status = tasks
        .get(&id)
        .cloned()
        .unwrap_or(ExecutionStatus::Failed("Task not found".to_string()));
    Json(status)
}

async fn run_client(
    worker_url: String,
    prompt: String,
    token: Option<String>,
    cwd: Option<PathBuf>,
    timeout: Option<u32>,
) -> Result<()> {
    let client = reqwest::Client::new();
    let request_id = Uuid::new_v4();

    let req = ExecutionRequest {
        id: request_id,
        timestamp: Utc::now(),
        prompt,
        cwd: cwd
            .unwrap_or_else(|| std::env::current_dir().unwrap_or_default())
            .to_string_lossy()
            .to_string(),
        env_vars: HashMap::new(),
        timeout_seconds: timeout.unwrap_or(300),
        sync_state: None,
        options: thegent_offload::ExecutionOptions {
            dry_run: false,
            isolation_level: thegent_offload::IsolationLevel::Process,
            stream_output: true,
        },
    };

    let mut builder = client.post(format!("{}/v1/execute", worker_url)).json(&req);
    if let Some(t) = token {
        builder = builder.bearer_auth(t);
    }

    let res = builder
        .send()
        .await
        .context("Failed to send request to worker")?;

    if !res.status().is_success() {
        let err_text = res.text().await?;
        error!("Worker returned error: {}", err_text);
        return Err(anyhow::anyhow!("Worker error: {}", err_text));
    }

    let response: ExecutionResponse = res
        .json()
        .await
        .context("Failed to parse worker response")?;

    info!(
        "Task {} finished with status: {:?}",
        request_id, response.status
    );
    if let Some(stdout) = response.stdout {
        println!("--- STDOUT ---\n{}", stdout);
    }
    if let Some(stderr) = response.stderr {
        eprintln!("--- STDERR ---\n{}", stderr);
    }

    Ok(())
}
