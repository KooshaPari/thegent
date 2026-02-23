//! Chart widgets for thegent TUI — Phase 3.
//!
//! Provides:
//! - `SparklineWidget` — horizontal sparkline for the last N numeric values
//! - `BarChartWidget` — vertical bar chart for labelled metric values

use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Color, Style};
use ratatui::widgets::{BarChart, Block, Borders, Sparkline, Widget};

// ---------------------------------------------------------------------------
// SparklineWidget
// ---------------------------------------------------------------------------

/// Horizontal sparkline showing the last `capacity` values.
///
/// Values are stored as `u64` (ratatui `Sparkline` requires unsigned integers).
/// Push floating-point values with [`SparklineWidget::push_value`]; they are
/// scaled to the nearest `u64`.
pub struct SparklineWidget {
    /// Ring-buffer of recent values (oldest first, newest last).
    values: Vec<u64>,
    /// Maximum number of data points to retain.
    capacity: usize,
    /// Widget title shown in the surrounding block.
    pub title: String,
    /// Bar colour.
    pub bar_color: Color,
}

impl SparklineWidget {
    /// Create a new sparkline that retains the last `capacity` values.
    pub fn new(capacity: usize) -> Self {
        Self {
            values: Vec::with_capacity(capacity),
            capacity,
            title: " Sparkline ".to_string(),
            bar_color: Color::Cyan,
        }
    }

    /// Push a new data point.  When the buffer is full the oldest value is
    /// evicted (FIFO ring-buffer semantics).
    pub fn push_value(&mut self, value: f64) {
        let quantised = value.max(0.0).round() as u64;
        if self.values.len() >= self.capacity {
            self.values.remove(0);
        }
        self.values.push(quantised);
    }

    /// Number of data points currently stored.
    pub fn len(&self) -> usize {
        self.values.len()
    }

    /// Whether the buffer is empty.
    pub fn is_empty(&self) -> bool {
        self.values.is_empty()
    }

    /// The most recently pushed value, or `None` if the buffer is empty.
    pub fn latest(&self) -> Option<u64> {
        self.values.last().copied()
    }

    /// The maximum value currently in the buffer, or `0` if empty.
    pub fn max_value(&self) -> u64 {
        self.values.iter().copied().max().unwrap_or(0)
    }

    /// Snapshot of all values (oldest first).
    pub fn values(&self) -> &[u64] {
        &self.values
    }

    /// Render the sparkline into `buf` at `area`.
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let block = Block::default()
            .borders(Borders::ALL)
            .title(self.title.clone());

        let sparkline = Sparkline::default()
            .block(block)
            .data(&self.values)
            .style(Style::default().fg(self.bar_color));

        sparkline.render(area, buf);
    }
}

// ---------------------------------------------------------------------------
// BarChartWidget
// ---------------------------------------------------------------------------

/// Vertical bar chart for labelled resource metrics (CPU%, memory%, cost, …).
pub struct BarChartWidget {
    /// Current data: (label, value) pairs.
    data: Vec<(String, u64)>,
    /// Widget title shown in the surrounding block.
    pub title: String,
    /// Bar colour.
    pub bar_color: Color,
    /// Width of each bar in terminal columns.
    pub bar_width: u16,
    /// Gap between bars in terminal columns.
    pub bar_gap: u16,
}

impl BarChartWidget {
    /// Create a new `BarChartWidget` with default styling.
    pub fn new() -> Self {
        Self {
            data: Vec::new(),
            title: " Bar Chart ".to_string(),
            bar_color: Color::Green,
            bar_width: 5,
            bar_gap: 1,
        }
    }

    /// Replace the current data set.
    ///
    /// Each tuple is `(label, value)`.  Labels are capped at 10 bytes to keep
    /// bar annotations readable.
    pub fn set_data(&mut self, data: Vec<(&str, u64)>) {
        self.data = data
            .into_iter()
            .map(|(label, value)| (label.to_string(), value))
            .collect();
    }

    /// Number of bars currently held.
    pub fn bar_count(&self) -> usize {
        self.data.len()
    }

    /// The maximum value among all bars, or `0` if empty.
    pub fn max_value(&self) -> u64 {
        self.data.iter().map(|(_, v)| *v).max().unwrap_or(0)
    }

    /// Render the bar chart into `buf` at `area`.
    pub fn render(&self, area: Rect, buf: &mut Buffer) {
        let block = Block::default()
            .borders(Borders::ALL)
            .title(self.title.clone());

        // Build owned string storage so we can create `(&str, u64)` slices.
        let owned: Vec<(String, u64)> = self.data.clone();
        let bar_data: Vec<(&str, u64)> = owned
            .iter()
            .map(|(label, v)| (label.as_str(), *v))
            .collect();

        let chart = BarChart::default()
            .block(block)
            .data(&bar_data)
            .bar_width(self.bar_width)
            .bar_gap(self.bar_gap)
            .bar_style(Style::default().fg(self.bar_color))
            .value_style(Style::default().fg(Color::White).bg(self.bar_color));

        chart.render(area, buf);
    }
}

impl Default for BarChartWidget {
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
    use ratatui::backend::TestBackend;
    use ratatui::Terminal;

    // -----------------------------------------------------------------------
    // SparklineWidget tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_sparkline_push_increases_len() {
        let mut s = SparklineWidget::new(10);
        assert_eq!(s.len(), 0);
        s.push_value(5.0);
        assert_eq!(s.len(), 1);
        s.push_value(10.0);
        assert_eq!(s.len(), 2);
    }

    #[test]
    fn test_sparkline_evicts_oldest_when_full() {
        let mut s = SparklineWidget::new(3);
        s.push_value(1.0);
        s.push_value(2.0);
        s.push_value(3.0);
        assert_eq!(s.len(), 3);
        s.push_value(4.0);
        // Length stays at capacity
        assert_eq!(s.len(), 3);
        // Oldest (1) evicted; values should be [2, 3, 4]
        assert_eq!(s.values(), &[2, 3, 4]);
    }

    #[test]
    fn test_sparkline_latest_returns_last_pushed() {
        let mut s = SparklineWidget::new(10);
        s.push_value(7.0);
        s.push_value(42.0);
        assert_eq!(s.latest(), Some(42));
    }

    #[test]
    fn test_sparkline_latest_empty_returns_none() {
        let s = SparklineWidget::new(10);
        assert_eq!(s.latest(), None);
    }

    #[test]
    fn test_sparkline_max_value() {
        let mut s = SparklineWidget::new(10);
        s.push_value(3.0);
        s.push_value(99.0);
        s.push_value(12.0);
        assert_eq!(s.max_value(), 99);
    }

    #[test]
    fn test_sparkline_max_value_empty() {
        let s = SparklineWidget::new(10);
        assert_eq!(s.max_value(), 0);
    }

    #[test]
    fn test_sparkline_negative_clamped_to_zero() {
        let mut s = SparklineWidget::new(5);
        s.push_value(-10.0);
        assert_eq!(s.values(), &[0]);
    }

    #[test]
    fn test_sparkline_fractional_rounds() {
        let mut s = SparklineWidget::new(5);
        s.push_value(3.7);
        assert_eq!(s.values(), &[4]);
        s.push_value(3.2);
        assert_eq!(s.values(), &[4, 3]);
    }

    #[test]
    fn test_sparkline_is_empty() {
        let s = SparklineWidget::new(5);
        assert!(s.is_empty());
    }

    #[test]
    fn test_sparkline_render_does_not_panic() {
        let mut s = SparklineWidget::new(10);
        for i in 0..10 {
            s.push_value(i as f64 * 5.0);
        }
        let backend = TestBackend::new(40, 5);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                s.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    // -----------------------------------------------------------------------
    // BarChartWidget tests
    // -----------------------------------------------------------------------

    #[test]
    fn test_barchart_set_data_stores_entries() {
        let mut b = BarChartWidget::new();
        b.set_data(vec![("cpu", 70), ("mem", 45), ("cost", 12)]);
        assert_eq!(b.bar_count(), 3);
    }

    #[test]
    fn test_barchart_set_data_overwrites_previous() {
        let mut b = BarChartWidget::new();
        b.set_data(vec![("a", 1), ("b", 2)]);
        b.set_data(vec![("x", 99)]);
        assert_eq!(b.bar_count(), 1);
        assert_eq!(b.max_value(), 99);
    }

    #[test]
    fn test_barchart_max_value_empty() {
        let b = BarChartWidget::new();
        assert_eq!(b.max_value(), 0);
    }

    #[test]
    fn test_barchart_max_value() {
        let mut b = BarChartWidget::new();
        b.set_data(vec![("a", 10), ("b", 80), ("c", 55)]);
        assert_eq!(b.max_value(), 80);
    }

    #[test]
    fn test_barchart_default_bar_count_zero() {
        let b = BarChartWidget::default();
        assert_eq!(b.bar_count(), 0);
    }

    #[test]
    fn test_barchart_render_does_not_panic_empty() {
        let b = BarChartWidget::new();
        let backend = TestBackend::new(40, 10);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                b.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }

    #[test]
    fn test_barchart_render_does_not_panic_with_data() {
        let mut b = BarChartWidget::new();
        b.set_data(vec![("CPU", 75), ("MEM", 50), ("DISK", 30)]);
        let backend = TestBackend::new(60, 10);
        let mut terminal = Terminal::new(backend).unwrap();
        terminal
            .draw(|frame| {
                b.render(frame.area(), frame.buffer_mut());
            })
            .unwrap();
    }
}
