//! Pareto Frontier Visualization TUI Panel — WL-031.
//!
//! Reads routing audit records from `~/.thegent/routing_audit.jsonl` and
//! renders a live dashboard with:
//! - `BarChartWidget`: cost / latency metrics for providers in recent records
//! - `SparklineWidget`: sliding window cost trend (last 10 records)
//! - Current provider / model / latency / cost from the latest audit entry
//!
//! Key bindings:
//! - `o` — open model override `ConfirmDialog`
//! - `r` — refresh (reload audit records from disk)

use std::path::PathBuf;

use crossterm::event::{KeyCode, KeyEvent};
use ratatui::buffer::Buffer;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Paragraph, Widget};
use serde_json::Value;

use crate::themes::Theme;
use crate::widgets::{BarChartWidget, ConfirmDialog, SparklineWidget};

// ---------------------------------------------------------------------------
// AuditRecord (parsed from JSONL)
// ---------------------------------------------------------------------------

/// A parsed audit record loaded from routing_audit.jsonl.
///
/// Uses `serde_json::Value` for the full payload so the panel does not need
/// to depend on the thegent-router crate's `AuditRecord` struct directly.
/// Only the fields the panel needs are extracted at parse time.
#[derive(Debug, Clone)]
pub struct AuditRecord {
    /// ISO-8601 UTC timestamp.
    pub timestamp: String,
    /// Unique decision identifier.
    pub decision_id: String,
    /// Provider name (e.g. "lifecycle", "thegent").
    pub provider: String,
    /// Model name (e.g. "gemini-3-flash", "claude-sonnet-4.6").
    pub model: String,
    /// Execution latency in milliseconds.
    pub latency_ms: u64,
    /// Estimated cost in USD.
    pub cost: f64,
}

impl AuditRecord {
    /// Parse an `AuditRecord` from a `serde_json::Value`.
    ///
    /// Returns `None` if any required field is absent or has the wrong type.
    pub fn from_value(v: &Value) -> Option<Self> {
        Some(Self {
            timestamp: v["timestamp"].as_str()?.to_string(),
            decision_id: v["decision_id"].as_str()?.to_string(),
            provider: v["provider"].as_str()?.to_string(),
            model: v["model"].as_str()?.to_string(),
            latency_ms: v["latency_ms"].as_u64()?,
            cost: v["cost"].as_f64()?,
        })
    }
}

// ---------------------------------------------------------------------------
// ParetoAction
// ---------------------------------------------------------------------------

/// Actions that the panel can return to the host application.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ParetoAction {
    /// User confirmed a model override; contains the new model identifier.
    Override(String),
    /// User pressed `r` to force a refresh of audit data.
    Refresh,
}

// ---------------------------------------------------------------------------
// ParetoFrontierState
// ---------------------------------------------------------------------------

/// Mutable state for the `ParetoFrontierPanel`.
pub struct ParetoFrontierState {
    /// Last `N` audit records loaded from disk (chronological order).
    pub audit_records: Vec<AuditRecord>,
    /// Currently selected row index in the records list.
    pub selected_idx: usize,
    /// Active model override dialog, if any.
    pub override_dialog: Option<ConfirmDialog>,
}

impl ParetoFrontierState {
    /// Create an empty state.
    pub fn new() -> Self {
        Self {
            audit_records: Vec::new(),
            selected_idx: 0,
            override_dialog: None,
        }
    }

    /// Load the last `limit` records from `path`.
    ///
    /// # Errors
    ///
    /// Returns `Err` if the file exists but cannot be read, or if any line
    /// is non-empty and fails JSON parsing.  An absent file is treated as an
    /// empty log (returns `Ok(())`).
    pub fn load_from_path(&mut self, path: &PathBuf, limit: usize) -> Result<(), String> {
        if !path.exists() {
            self.audit_records.clear();
            return Ok(());
        }

        let content = std::fs::read_to_string(path)
            .map_err(|e| format!("Failed to read audit file {}: {}", path.display(), e))?;

        let mut records: Vec<AuditRecord> = Vec::new();
        for (lineno, line) in content.lines().enumerate() {
            let trimmed = line.trim();
            if trimmed.is_empty() {
                continue;
            }
            let v: Value = serde_json::from_str(trimmed)
                .map_err(|e| format!("Malformed JSON at line {}: {}", lineno + 1, e))?;
            if let Some(rec) = AuditRecord::from_value(&v) {
                records.push(rec);
            }
        }

        // Keep only the most recent `limit` records.
        let start = records.len().saturating_sub(limit);
        self.audit_records = records[start..].to_vec();
        self.selected_idx = self
            .selected_idx
            .min(self.audit_records.len().saturating_sub(1));
        Ok(())
    }

    /// The latest audit record, if any.
    pub fn latest(&self) -> Option<&AuditRecord> {
        self.audit_records.last()
    }
}

impl Default for ParetoFrontierState {
    fn default() -> Self {
        Self::new()
    }
}

// ---------------------------------------------------------------------------
// ParetoFrontierPanel
// ---------------------------------------------------------------------------

/// Number of recent audit records to display.
const WINDOW_SIZE: usize = 10;

/// Pareto Frontier Visualization Panel.
///
/// Renders a three-region layout:
/// ```text
/// ┌─ Status ──────────────────────────────────────┐
/// │ Provider: thegent  Model: claude-sonnet-4.6   │
/// │ Latency: 42 ms     Cost: $0.000042            │
/// └───────────────────────────────────────────────┘
/// ┌─ Provider Metrics (Bar) ─┐  ┌─ Cost Trend ───┐
/// │  [lifecycle] [thegent]   │  │  ▄▅▆▇█▅▄▃▅▇   │
/// └──────────────────────────┘  └────────────────┘
/// ```
pub struct ParetoFrontierPanel {
    /// Path to the routing_audit.jsonl file.
    audit_path: PathBuf,
}

impl ParetoFrontierPanel {
    /// Create a panel reading from the default audit path
    /// (`~/.thegent/routing_audit.jsonl`).
    pub fn new() -> Self {
        let path = directories::UserDirs::new()
            .map(|d| d.home_dir().join(".thegent").join("routing_audit.jsonl"))
            .unwrap_or_else(|| PathBuf::from(".thegent/routing_audit.jsonl"));
        Self { audit_path: path }
    }

    /// Create a panel reading from a custom audit path.
    pub fn with_path(path: PathBuf) -> Self {
        Self { audit_path: path }
    }

    /// The configured audit path.
    pub fn audit_path(&self) -> &PathBuf {
        &self.audit_path
    }

    /// Handle a key event.
    ///
    /// - `o` → opens the model override `ConfirmDialog` in `state`
    /// - `r` → returns `ParetoAction::Refresh`
    ///
    /// When the override dialog is open, key events are forwarded to it.
    /// Once answered `Some(true)` (Yes), a `ParetoAction::Override` is
    /// returned with the model from the latest audit record.
    pub fn handle_key_event(
        &self,
        state: &mut ParetoFrontierState,
        key: KeyEvent,
    ) -> Option<ParetoAction> {
        // If the override dialog is active, route all keys to it.
        if let Some(dialog) = state.override_dialog.as_mut() {
            dialog.handle_key(key.code);
            if dialog.is_answered() {
                let confirmed = dialog.answer == Some(true);
                let model_id = state
                    .latest()
                    .map(|r| r.model.clone())
                    .unwrap_or_else(|| "unknown".to_string());
                state.override_dialog = None;
                if confirmed {
                    return Some(ParetoAction::Override(model_id));
                }
            }
            return None;
        }

        match key.code {
            KeyCode::Char('o') => {
                let model = state
                    .latest()
                    .map(|r| r.model.clone())
                    .unwrap_or_else(|| "unknown".to_string());
                state.override_dialog = Some(ConfirmDialog::new(format!(
                    "Override model to '{}'?",
                    model
                )));
                None
            }
            KeyCode::Char('r') => Some(ParetoAction::Refresh),
            _ => None,
        }
    }

    /// Render the full panel into `frame` at `area` using `theme`.
    pub fn render(&self, state: &ParetoFrontierState, area: Rect, buf: &mut Buffer, theme: &Theme) {
        // Split vertically: status row (3 lines), then charts.
        let rows = Layout::default()
            .direction(Direction::Vertical)
            .constraints([Constraint::Length(4), Constraint::Min(5)])
            .split(area);

        self.render_status(state, rows[0], buf, theme);
        self.render_charts(state, rows[1], buf, theme);

        // Render the override dialog on top if active.
        if let Some(dialog) = &state.override_dialog {
            dialog.render(area, buf);
        }
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    fn render_status(
        &self,
        state: &ParetoFrontierState,
        area: Rect,
        buf: &mut Buffer,
        theme: &Theme,
    ) {
        let accent = theme.accent.to_ratatui();
        let fg = theme.fg.to_ratatui();
        let border = theme.border.to_ratatui();

        let block = Block::default()
            .borders(Borders::ALL)
            .border_style(Style::default().fg(border))
            .title(Span::styled(
                " Pareto Frontier — Router Status ",
                Style::default().fg(accent).add_modifier(Modifier::BOLD),
            ));

        let inner = block.inner(area);
        block.render(area, buf);

        if inner.height == 0 {
            return;
        }

        let (provider, model, latency, cost) = match state.latest() {
            Some(r) => (
                r.provider.clone(),
                r.model.clone(),
                format!("{} ms", r.latency_ms),
                format!("${:.6}", r.cost),
            ),
            None => (
                "—".to_string(),
                "—".to_string(),
                "—".to_string(),
                "—".to_string(),
            ),
        };

        let lines = vec![
            Line::from(vec![
                Span::styled(
                    "Provider: ",
                    Style::default().fg(fg).add_modifier(Modifier::BOLD),
                ),
                Span::styled(provider, Style::default().fg(accent)),
                Span::raw("   "),
                Span::styled(
                    "Model: ",
                    Style::default().fg(fg).add_modifier(Modifier::BOLD),
                ),
                Span::styled(model, Style::default().fg(accent)),
            ]),
            Line::from(vec![
                Span::styled(
                    "Latency: ",
                    Style::default().fg(fg).add_modifier(Modifier::BOLD),
                ),
                Span::styled(latency, Style::default().fg(Color::Cyan)),
                Span::raw("   "),
                Span::styled(
                    "Cost: ",
                    Style::default().fg(fg).add_modifier(Modifier::BOLD),
                ),
                Span::styled(cost, Style::default().fg(Color::Yellow)),
            ]),
        ];
        Paragraph::new(lines).render(inner, buf);
    }

    fn render_charts(
        &self,
        state: &ParetoFrontierState,
        area: Rect,
        buf: &mut Buffer,
        theme: &Theme,
    ) {
        // Split horizontally: bar chart (60%) | sparkline (40%).
        let cols = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Percentage(60), Constraint::Percentage(40)])
            .split(area);

        self.render_bar_chart(state, cols[0], buf, theme);
        self.render_sparkline(state, cols[1], buf, theme);
    }

    fn render_bar_chart(
        &self,
        state: &ParetoFrontierState,
        area: Rect,
        buf: &mut Buffer,
        theme: &Theme,
    ) {
        // Aggregate average cost_usd * 1_000_000 (µUSD) per provider across records.
        let mut provider_costs: std::collections::HashMap<String, (u64, u64)> =
            std::collections::HashMap::new();
        for rec in &state.audit_records {
            let entry = provider_costs.entry(rec.provider.clone()).or_insert((0, 0));
            entry.0 += (rec.cost * 1_000_000.0).round() as u64; // sum µUSD
            entry.1 += 1; // count
        }

        let mut bar_data: Vec<(String, u64)> = provider_costs
            .into_iter()
            .map(|(provider, (sum, count))| {
                let avg = if count == 0 { 0 } else { sum / count };
                (provider, avg)
            })
            .collect();
        bar_data.sort_by(|a, b| a.0.cmp(&b.0));

        let mut chart = BarChartWidget::new();
        chart.title = " Provider Cost (avg µUSD) ".to_string();
        chart.bar_color = theme.accent.to_ratatui();
        chart.bar_width = 7;
        chart.bar_gap = 1;
        chart.set_data(
            bar_data
                .iter()
                .map(|(label, val)| (label.as_str(), *val))
                .collect(),
        );
        chart.render(area, buf);
    }

    fn render_sparkline(
        &self,
        state: &ParetoFrontierState,
        area: Rect,
        buf: &mut Buffer,
        theme: &Theme,
    ) {
        let mut sparkline = SparklineWidget::new(WINDOW_SIZE);
        sparkline.title = " Cost Trend (µUSD) ".to_string();
        sparkline.bar_color = theme.success.to_ratatui();

        for rec in &state.audit_records {
            sparkline.push_value(rec.cost * 1_000_000.0);
        }
        sparkline.render(area, buf);
    }
}

impl Default for ParetoFrontierPanel {
    fn default() -> Self {
        Self::new()
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};
    use ratatui::backend::TestBackend;
    use ratatui::Terminal;
    use std::io::Write;
    use tempfile::NamedTempFile;

    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------

    fn make_key(code: KeyCode) -> KeyEvent {
        KeyEvent::new(code, KeyModifiers::NONE)
    }

    fn sample_record_json(provider: &str, model: &str, latency_ms: u64, cost: f64) -> String {
        format!(
            r#"{{"timestamp":"2026-02-20T00:00:00Z","decision_id":"test-id","provider":"{provider}","model":"{model}","latency_ms":{latency_ms},"cost":{cost},"prev_hash":"","hash":"abc123"}}"#
        )
    }

    fn write_audit_file(records: &[String]) -> NamedTempFile {
        let mut f = NamedTempFile::new().unwrap();
        for rec in records {
            writeln!(f, "{}", rec).unwrap();
        }
        f
    }

    fn sample_state_with_records() -> ParetoFrontierState {
        let records = vec![
            sample_record_json("lifecycle", "gemini-3-flash", 5, 0.000005),
            sample_record_json("thegent", "claude-sonnet-4.6", 42, 0.000042),
            sample_record_json("lifecycle", "gemini-3-flash", 8, 0.000008),
        ];
        let f = write_audit_file(&records);
        let mut state = ParetoFrontierState::new();
        state.load_from_path(&f.path().to_path_buf(), 10).unwrap();
        state
    }

    // -----------------------------------------------------------------------
    // ParetoFrontierState tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_state_with_empty_records_no_panic() {
        let state = ParetoFrontierState::new();
        assert!(state.audit_records.is_empty());
        assert!(state.latest().is_none());
        assert!(state.override_dialog.is_none());
    }

    #[test]
    fn test_state_load_from_absent_path_returns_empty() {
        let mut state = ParetoFrontierState::new();
        let absent = PathBuf::from("/tmp/__nonexistent_audit_wl031__.jsonl");
        state.load_from_path(&absent, 10).unwrap();
        assert!(state.audit_records.is_empty());
    }

    #[test]
    fn test_state_load_records_from_file() {
        let state = sample_state_with_records();
        assert_eq!(state.audit_records.len(), 3);
    }

    #[test]
    fn test_state_latest_returns_last_record() {
        let state = sample_state_with_records();
        let latest = state.latest().unwrap();
        assert_eq!(latest.provider, "lifecycle");
        assert_eq!(latest.model, "gemini-3-flash");
    }

    #[test]
    fn test_state_load_respects_limit() {
        let records: Vec<String> = (0..15)
            .map(|i| sample_record_json("lifecycle", "gemini-3-flash", i, 0.001 * i as f64))
            .collect();
        let f = write_audit_file(&records);
        let mut state = ParetoFrontierState::new();
        state.load_from_path(&f.path().to_path_buf(), 10).unwrap();
        assert_eq!(state.audit_records.len(), 10);
    }

    #[test]
    fn test_state_load_malformed_json_returns_error() {
        let mut f = NamedTempFile::new().unwrap();
        writeln!(f, "{{not valid json}}").unwrap();
        let mut state = ParetoFrontierState::new();
        let result = state.load_from_path(&f.path().to_path_buf(), 10);
        assert!(result.is_err());
    }

    #[test]
    fn test_sparkline_fills_from_audit() {
        let state = sample_state_with_records();
        // Verify cost values are present and ordered.
        // state has 3 records; costs in µUSD: 5, 42, 8
        let costs: Vec<f64> = state.audit_records.iter().map(|r| r.cost).collect();
        assert_eq!(costs.len(), 3);
        assert!((costs[1] - 0.000042).abs() < 1e-9); // middle record is thegent
    }

    // -----------------------------------------------------------------------
    // AuditRecord::from_value tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_audit_record_from_value_ok() {
        let json = sample_record_json("lifecycle", "gemini-3-flash", 10, 0.0001);
        let v: Value = serde_json::from_str(&json).unwrap();
        let rec = AuditRecord::from_value(&v).unwrap();
        assert_eq!(rec.provider, "lifecycle");
        assert_eq!(rec.model, "gemini-3-flash");
        assert_eq!(rec.latency_ms, 10);
        assert!((rec.cost - 0.0001).abs() < 1e-9);
    }

    #[test]
    fn test_audit_record_from_value_missing_field_returns_none() {
        let v = serde_json::json!({"provider": "lifecycle"});
        assert!(AuditRecord::from_value(&v).is_none());
    }

    // -----------------------------------------------------------------------
    // Key binding tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_handle_refresh_key() {
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let mut state = ParetoFrontierState::new();
        let action = panel.handle_key_event(&mut state, make_key(KeyCode::Char('r')));
        assert_eq!(action, Some(ParetoAction::Refresh));
    }

    #[test]
    fn test_handle_override_key_opens_dialog() {
        let state_with_recs = sample_state_with_records();
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let mut state = state_with_recs;
        let action = panel.handle_key_event(&mut state, make_key(KeyCode::Char('o')));
        // 'o' opens the dialog, does not yet return an action
        assert!(action.is_none());
        assert!(state.override_dialog.is_some());
    }

    #[test]
    fn test_handle_override_confirm_yes_returns_action() {
        let state_with_recs = sample_state_with_records();
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let mut state = state_with_recs;

        // Open dialog
        panel.handle_key_event(&mut state, make_key(KeyCode::Char('o')));
        // Confirm with 'y'
        let action = panel.handle_key_event(&mut state, make_key(KeyCode::Char('y')));
        assert!(matches!(action, Some(ParetoAction::Override(_))));
        assert!(state.override_dialog.is_none());
    }

    #[test]
    fn test_handle_override_confirm_no_returns_none() {
        let state_with_recs = sample_state_with_records();
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let mut state = state_with_recs;

        // Open dialog
        panel.handle_key_event(&mut state, make_key(KeyCode::Char('o')));
        // Cancel with 'n'
        let action = panel.handle_key_event(&mut state, make_key(KeyCode::Char('n')));
        assert!(action.is_none());
        assert!(state.override_dialog.is_none());
    }

    #[test]
    fn test_handle_override_key_on_empty_state_still_opens_dialog() {
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let mut state = ParetoFrontierState::new();
        // No audit records, 'o' should still open dialog with "unknown"
        let action = panel.handle_key_event(&mut state, make_key(KeyCode::Char('o')));
        assert!(action.is_none());
        assert!(state.override_dialog.is_some());
    }

    #[test]
    fn test_unrecognised_key_returns_none() {
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let mut state = ParetoFrontierState::new();
        let action = panel.handle_key_event(&mut state, make_key(KeyCode::Char('x')));
        assert!(action.is_none());
    }

    // -----------------------------------------------------------------------
    // Render tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_panel_renders_without_panic_empty_state() {
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let state = ParetoFrontierState::new();
        let theme = Theme::dark();

        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                panel.render(&state, frame.area(), frame.buffer_mut(), &theme);
            })
            .unwrap();
    }

    #[test]
    fn test_panel_renders_without_panic_with_records() {
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let state = sample_state_with_records();
        let theme = Theme::dark();

        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                panel.render(&state, frame.area(), frame.buffer_mut(), &theme);
            })
            .unwrap();
    }

    #[test]
    fn test_panel_renders_with_override_dialog_open() {
        let panel = ParetoFrontierPanel::with_path(PathBuf::from("/dev/null"));
        let mut state = sample_state_with_records();
        let theme = Theme::dark();

        // Open override dialog
        panel.handle_key_event(&mut state, make_key(KeyCode::Char('o')));

        let backend = TestBackend::new(80, 24);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                panel.render(&state, frame.area(), frame.buffer_mut(), &theme);
            })
            .unwrap();
    }
}
