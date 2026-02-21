use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub(crate) struct HookInput {
    pub(crate) tool_name: Option<String>,
    pub(crate) tool_input: Option<serde_json::Value>,
    pub(crate) session_id: Option<String>,
    pub(crate) project_dir: Option<String>,
    pub(crate) cwd: Option<String>,
}

#[derive(Clone, Copy, PartialEq)]
pub(crate) enum Mode {
    Pretool,
    Posttool,
    Stop,
    SessionStart,
    PromptSubmit,
    SubagentStart,
    SubagentStop,
    PreCompact,
    SessionEnd,
    TaskCompleted,
    TeammateIdle,
    PostAgentRun,
}
