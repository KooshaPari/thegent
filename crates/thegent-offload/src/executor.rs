use anyhow::{Result, Context};
use std::path::{Path, PathBuf};
use std::process::Stdio;
use tokio::process::Command;
use tracing::{info, error};
use crate::{ExecutionRequest, ExecutionResponse, ExecutionStatus, SyncState, IsolationLevel};
use uuid::Uuid;
use chrono::Utc;
use std::collections::HashMap;

pub struct Executor {
    base_dir: PathBuf,
}

impl Executor {
    pub fn new(base_dir: PathBuf) -> Self {
        Self { base_dir }
    }

    pub async fn execute(&self, req: ExecutionRequest) -> Result<ExecutionResponse> {
        let start_time = std::time::Instant::now();
        let task_id = req.id;
        
        info!("Executing task {} in {}", task_id, req.cwd);

        let work_dir = match req.options.isolation_level {
            IsolationLevel::Worktree => {
                self.setup_worktree(&req).await.context("Failed to setup worktree")?
            }
            _ => {
                // For Process isolation, just use the base_dir + req.cwd
                self.base_dir.join(&req.cwd)
            }
        };

        if !work_dir.exists() {
            return Ok(ExecutionResponse {
                request_id: task_id,
                status: ExecutionStatus::Failed(format!("CWD does not exist: {:?}", work_dir)),
                stdout: None,
                stderr: None,
                exit_code: Some(1),
                duration_ms: start_time.elapsed().as_millis() as u64,
                metrics: None,
            });
        }

        let mut cmd = Command::new("thegent");
        cmd.arg("run")
           .arg(&req.prompt)
           .current_dir(&work_dir)
           .stdout(Stdio::piped())
           .stderr(Stdio::piped());

        // Inject environment variables
        for (k, v) in &req.env_vars {
            cmd.env(k, v);
        }

        let output = cmd.output().await.context("Failed to execute thegent")?;
        
        let duration = start_time.elapsed().as_millis() as u64;

        // Cleanup worktree if needed
        if let IsolationLevel::Worktree = req.options.isolation_level {
            let _ = self.cleanup_worktree(&work_dir).await;
        }

        Ok(ExecutionResponse {
            request_id: task_id,
            status: if output.status.success() { ExecutionStatus::Completed } else { ExecutionStatus::Failed("Process exited with non-zero code".to_string()) },
            stdout: Some(String::from_utf8_lossy(&output.stdout).to_string()),
            stderr: Some(String::from_utf8_lossy(&output.stderr).to_string()),
            exit_code: output.status.code(),
            duration_ms: duration,
            metrics: None,
        })
    }

    async fn setup_worktree(&self, req: &ExecutionRequest) -> Result<PathBuf> {
        let worktree_path = self.base_dir.join(format!("shadow-{}", req.id));
        
        // 1. git worktree add <path> <commit>
        let commit = req.sync_state.as_ref().map(|s| s.base_commit.as_str()).unwrap_or("HEAD");
        
        let output = Command::new("git")
            .arg("worktree")
            .arg("add")
            .arg(&worktree_path)
            .arg(commit)
            .current_dir(&self.base_dir)
            .output()
            .await?;

        if !output.status.success() {
            let err = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("git worktree add failed: {}", err));
        }

        // 2. Apply patch if provided
        if let Some(sync_state) = &req.sync_state {
            if let Some(patch) = &sync_state.patch {
                // For simplicity, we assume patch is a raw diff string
                let mut patch_cmd = Command::new("git");
                patch_cmd.arg("apply")
                         .current_dir(&worktree_path)
                         .stdin(Stdio::piped());
                
                let mut child = patch_cmd.spawn()?;
                let mut stdin = child.stdin.take().unwrap();
                use tokio::io::AsyncWriteExt;
                stdin.write_all(patch.as_bytes()).await?;
                drop(stdin);
                
                let patch_output = child.wait().await?;
                if !patch_output.success() {
                    error!("Failed to apply patch to worktree");
                }
            }
        }

        Ok(worktree_path)
    }

    async fn cleanup_worktree(&self, path: &Path) -> Result<()> {
        info!("Cleaning up worktree: {:?}", path);
        let output = Command::new("git")
            .arg("worktree")
            .arg("remove")
            .arg("--force")
            .arg(path)
            .current_dir(&self.base_dir)
            .output()
            .await?;

        if !output.status.success() {
            let err = String::from_utf8_lossy(&output.stderr);
            error!("git worktree remove failed: {}", err);
        }
        Ok(())
    }
}
