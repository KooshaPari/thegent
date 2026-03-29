//! Task Executor Module
//!
//! Handles parallel execution of tasks with dependency-aware scheduling.

use std::collections::{HashMap, HashSet};
use std::process::Stdio;
use std::sync::Arc;
use std::time::Instant;

use futures::StreamExt;
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command;
use tokio::sync::mpsc;
use tokio::task::JoinSet;
use parking_lot::RwLock;

use crate::graph::{TaskGraph, TaskId};
use crate::{ForgeError, ForgeState, ForgeStatus, Result, TaskEvent, TaskResult};

/// Parallel task executor with configurable worker count
pub struct Executor {
    max_workers: usize,
}

impl Executor {
    pub fn new(max_workers: usize) -> Self {
        Self { max_workers: max_workers.max(1) }
    }

    pub async fn execute(
        &self,
        graph: &TaskGraph,
        targets: Vec<String>,
        event_tx: mpsc::Sender<TaskEvent>,
    ) -> Result<ForgeStatus> {
        let state = Arc::new(ForgeState::new());

        let targets = if targets.is_empty() {
            graph.execution_order()
        } else {
            for target in &targets {
                if !graph.tasks().contains_key(&TaskId::new(target)) {
                    return Err(ForgeError::TaskNotFound(target.clone()));
                }
            }
            targets.into_iter().map(TaskId::new).collect()
        };

        let required = graph.required_tasks(&targets.iter().map(|t| t.to_string()).collect::<Vec<_>>())?;

        let mut pending: HashMap<TaskId, usize> = required
            .iter()
            .map(|id| (id.clone(), graph.dependencies(id).map(|deps| deps.len()).unwrap_or(0)))
            .collect();

        let completed_deps: Arc<RwLock<HashMap<TaskId, HashSet<TaskId>>>> = Arc::new(RwLock::new(
            required.iter().cloned().map(|id| (id, HashSet::new())).collect()
        ));

        let (complete_tx, mut complete_rx) = mpsc::channel::<TaskId>(required.len());

        let mut join_set = JoinSet::new();
        let mut active_count = 0;
        let mut all_started = false;

        loop {
            tokio::select! {
                _ = async {}, if active_count < self.max_workers => {
                    let ready: Vec<TaskId> = pending.iter().filter(|(_, &count)| count == 0).map(|(id, _)| id.clone()).collect();

                    if let Some(id) = ready.into_iter().next() {
                        pending.remove(&id);
                        let task = graph.get(&id).unwrap().clone();
                        let state_clone = Arc::clone(&state);
                        let complete_tx = complete_tx.clone();
                        let event_tx = event_tx.clone();

                        join_set.spawn(async move {
                            let start = Instant::now();
                            let _ = event_tx.send(TaskEvent::Started(id.clone())).await;
                            state_clone.mark_running(&id);

                            let result = execute_task(&task).await;

                            let duration = start.elapsed();
                            let task_result = TaskResult {
                                success: result.is_ok(),
                                duration,
                                stdout: result.as_ref().map(|r| r.stdout.clone()).unwrap_or_default(),
                                stderr: result.as_ref().map(|r| r.stderr.clone()).unwrap_or_default(),
                            };

                            if result.is_ok() {
                                state_clone.mark_completed(&id, task_result);
                            } else {
                                let err = result.unwrap_err();
                                state_clone.mark_failed(&id, task_result);
                                let _ = event_tx.send(TaskEvent::Failed(id.clone(), err.to_string())).await;
                            }

                            let _ = complete_tx.send(id).await;
                        });

                        active_count += 1;
                    } else {
                        all_started = true;
                    }
                }

                completed_id = complete_rx.recv() => {
                    if let Some(id) = completed_id {
                        active_count -= 1;

                        {
                            let mut guard = completed_deps.write();
                            for (_, deps) in guard.iter_mut() {
                                deps.insert(id.clone());
                            }
                        }

                        if let Some(dependents) = graph.dependents(&id) {
                            for dep in dependents {
                                if let Some(count) = pending.get_mut(dep) {
                                    *count = count.saturating_sub(1);
                                }
                            }
                        }
                    }
                }

                _ = join_set.join_next(), if active_count > 0 => {}

                _ = async {}, if pending.is_empty() && active_count == 0 && all_started => {
                    break;
                }
            }
        }

        while join_set.join_next().await.is_some() {}

        let status = state.status();

        if status.failed > 0 {
            return Err(ForgeError::TaskFailed(format!("{} task(s) failed", status.failed), String::new()));
        }

        Ok(status)
    }
}

async fn execute_task(task: &crate::graph::Task) -> Result<CommandOutput> {
    let mut cmd = Command::new("sh");
    cmd.arg("-c")
        .arg(&task.command)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);

    let mut child = cmd.spawn().map_err(|e| ForgeError::TaskFailed(task.id.to_string(), e.to_string()))?;

    let stdout = child.stdout.take();
    let stderr = child.stderr.take();

    let (stdout_tx, stdout_rx) = mpsc::channel::<String>(1000);
    let (stderr_tx, stderr_rx) = mpsc::channel::<String>(1000);

    let stdout_handle = if let Some(stdout) = stdout {
        let mut reader = BufReader::new(stdout).lines();
        let tx = stdout_tx;
        Some(tokio::spawn(async move {
            let mut output = String::new();
            while let Ok(Some(line)) = reader.next_line().await {
                output.push_str(&line);
                output.push('\n');
                let _ = tx.send(line).await;
            }
            output
        }))
    } else {
        None
    };

    let stderr_handle = if let Some(stderr) = stderr {
        let mut reader = BufReader::new(stderr).lines();
        let tx = stderr_tx;
        Some(tokio::spawn(async move {
            let mut output = String::new();
            while let Ok(Some(line)) = reader.next_line().await {
                output.push_str(&line);
                output.push('\n');
                let _ = tx.send(line).await;
            }
            output
        }))
    } else {
        None
    };

    let mut stdout_stream = tokio_stream::wrappers::ReceiverStream::new(stdout_rx);
    let mut stderr_stream = tokio_stream::wrappers::ReceiverStream::new(stderr_rx);

    let mut combined_stdout = String::new();
    let mut combined_stderr = String::new();

    loop {
        tokio::select! {
            line = stdout_stream.next() => {
                if let Some(l) = line {
                    tracing::debug!("[{} stdout] {}", task.id, l);
                    combined_stdout.push_str(&l);
                    combined_stdout.push('\n');
                }
            }
            line = stderr_stream.next() => {
                if let Some(l) = line {
                    tracing::debug!("[{} stderr] {}", task.id, l);
                    combined_stderr.push_str(&l);
                    combined_stderr.push('\n');
                }
            }
            status = child.wait() => {
                if let Some(h) = stdout_handle {
                    let _ = h.await;
                }
                if let Some(h) = stderr_handle {
                    let _ = h.await;
                }

                match status {
                    Ok(exit) => {
                        if exit.success() {
                            return Ok(CommandOutput { stdout: combined_stdout, stderr: combined_stderr });
                        } else {
                            return Err(ForgeError::TaskFailed(task.id.to_string(), format!("Exit code: {:?}", exit.code())));
                        }
                    }
                    Err(e) => {
                        return Err(ForgeError::TaskFailed(task.id.to_string(), e.to_string()));
                    }
                }
            }
        }
    }
}

#[derive(Debug)]
struct CommandOutput {
    stdout: String,
    stderr: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_execute_simple_task() {
        let output = execute_task(&crate::graph::Task {
            id: TaskId::new("test"),
            command: "echo hello".to_string(),
            description: None,
            dependencies: vec![],
            watch: None,
        }).await;

        assert!(output.is_ok());
        assert!(output.unwrap().stdout.contains("hello"));
    }

    #[tokio::test]
    async fn test_execute_failing_task() {
        let output = execute_task(&crate::graph::Task {
            id: TaskId::new("fail"),
            command: "exit 1".to_string(),
            description: None,
            dependencies: vec![],
            watch: None,
        }).await;

        assert!(output.is_err());
    }
}
