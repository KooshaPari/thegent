//! thegent-tui binary entry point.
//!
//! Launches the default CompositApp with sample data.

use thegent_tui::app::{run, AgentRunRow, CompositApp};
use thegent_tui::widgets::CommandRegistry;

fn main() -> anyhow::Result<()> {
    let registry = CommandRegistry::new(vec![
        "run".to_string(),
        "stop".to_string(),
        "status".to_string(),
        "start".to_string(),
        "restart".to_string(),
        "logs".to_string(),
        "agents".to_string(),
        "queue".to_string(),
        "history".to_string(),
        "help".to_string(),
        "quit".to_string(),
    ]);

    let mut app = CompositApp::new(registry);

    // Seed with sample agent run history.
    app.set_runs(vec![
        AgentRunRow {
            id: "run-010".to_string(),
            model: "claude-opus-4-6".to_string(),
            status: "done".to_string(),
            duration_s: 42,
            tokens: 8_200,
        },
        AgentRunRow {
            id: "run-009".to_string(),
            model: "claude-sonnet-4-6".to_string(),
            status: "error".to_string(),
            duration_s: 12,
            tokens: 1_100,
        },
        AgentRunRow {
            id: "run-008".to_string(),
            model: "gpt-5-mini".to_string(),
            status: "done".to_string(),
            duration_s: 7,
            tokens: 500,
        },
    ]);

    app.timeline.info("Application ready");
    app.timeline.success("Database connected");
    app.timeline.warn("Rate limit at 80%");
    app.timeline.info("3 runs loaded");

    run(app)?;
    Ok(())
}
