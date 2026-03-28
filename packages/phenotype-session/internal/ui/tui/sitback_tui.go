package tui

import (
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/KooshaPari/phenotype-session/internal/sqlite"
)

// Styles
var (
	headerStyle   = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#FFFFFF")).Background(lipgloss.Color("#1E3A5F")).Padding(0, 1)
	selectedStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#FFFFFF")).Background(lipgloss.Color("#2D5A87")).Padding(0, 1)
	normalStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("#CCCCCC")).Padding(0, 1)
	successStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#50FA7B"))
	errorStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color("#FF5555"))
	warningStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#FFB86C"))
	infoStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color("#8BE9FD"))
)

// Tab represents a view tab
type Tab int

const (
	TabAgents Tab = iota
	TabSessions
	TabTasks
	TabHarnesses
	TabHelp
)

// Model represents the sitback TUI state
type Model struct {
	Store     *sqlite.UnifiedStore
	Tab       Tab
	Cursor    int
	Agents    []sqlite.RunningAgent
	Sessions  []sqlite.Session
	Tasks     []sqlite.Task
	Harnesses []sqlite.HarnessSync
	Width     int
	Height    int
	Quitting  bool
	Error     error
}

// NewSitbackModel creates a new sitback TUI model
func NewSitbackModel() Model {
	store, err := sqlite.NewUnifiedStore("")
	if err != nil {
		return Model{Error: err}
	}

	return Model{
		Store:  store,
		Tab:    TabAgents,
		Cursor: 0,
	}
}

// Init initializes the TUI
func (m Model) Init() tea.Cmd {
	return nil
}

// Update handles TUI events
func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			m.Quitting = true
			return m, tea.Quit

		case "1":
			m.Tab = TabAgents
			m.Cursor = 0
		case "2":
			m.Tab = TabSessions
			m.Cursor = 0
		case "3":
			m.Tab = TabTasks
			m.Cursor = 0
		case "4":
			m.Tab = TabHarnesses
			m.Cursor = 0
		case "5":
			m.Tab = TabHelp
			m.Cursor = 0

		case "up", "k":
			if m.Cursor > 0 {
				m.Cursor--
			}
		case "down", "j":
			max := m.getMaxItems()
			if m.Cursor < max-1 {
				m.Cursor++
			}

		case "r":
			m.refreshData()

		case "?":
			m.Tab = TabHelp
		}

	case tea.WindowSizeMsg:
		m.Width = msg.Width
		m.Height = msg.Height
	}

	return m, nil
}

// getMaxItems returns the max items for current tab
func (m Model) getMaxItems() int {
	switch m.Tab {
	case TabAgents:
		return len(m.Agents)
	case TabSessions:
		return len(m.Sessions)
	case TabTasks:
		return len(m.Tasks)
	case TabHarnesses:
		return len(m.Harnesses)
	default:
		return 0
	}
}

// refreshData fetches fresh data from the store
func (m *Model) refreshData() {
	if m.Store == nil {
		return
	}

	// Get agents
	if agents, err := m.Store.ListRunningAgents(""); err == nil {
		m.Agents = agents
	}

	// Get sessions
	if sessions, err := m.Store.ListSessions(sqlite.SessionFilter{Limit: 100}); err == nil {
		m.Sessions = sessions
	}

	// Get tasks
	if tasks, err := m.Store.ListTasks("", ""); err == nil {
		m.Tasks = tasks
	}

	// Get harness sync status
	if harnesses, err := m.Store.GetHarnessSyncStatus(""); err == nil {
		m.Harnesses = harnesses
	}

	// Ensure cursor is valid
	max := m.getMaxItems()
	if m.Cursor >= max && max > 0 {
		m.Cursor = max - 1
	}
}

// View renders the TUI
func (m Model) View() string {
	if m.Error != nil {
		return fmt.Sprintf("Error: %v\n", m.Error)
	}

	m.refreshData()

	var b strings.Builder

	// Header
	b.WriteString(headerStyle.Render(" SITBACK - Session Orchestrator "))
	b.WriteString(fmt.Sprintf(" [%s]\n\n", time.Now().Format("15:04:05")))

	// Tabs
	tabs := []string{"[1] Agents", "[2] Sessions", "[3] Tasks", "[4] Harnesses", "[5] Help"}
	for i, tab := range tabs {
		if Tab(i) == m.Tab {
			b.WriteString(selectedStyle.Render(" " + tab + " "))
		} else {
			b.WriteString(normalStyle.Render(" " + tab + " "))
		}
	}
	b.WriteString("\n\n")

	// Content
	switch m.Tab {
	case TabAgents:
		m.renderAgents(&b)
	case TabSessions:
		m.renderSessions(&b)
	case TabTasks:
		m.renderTasks(&b)
	case TabHarnesses:
		m.renderHarnesses(&b)
	case TabHelp:
		m.renderHelp(&b)
	}

	// Footer
	b.WriteString("\n" + infoStyle.Render(" [r] Refresh  ") + infoStyle.Render(" [q] Quit  ") + infoStyle.Render(" [?] Help") + "\n")

	return b.String()
}

// renderAgents renders the agents tab
func (m Model) renderAgents(b *strings.Builder) {
	b.WriteString(headerStyle.Render(" RUNNING AGENTS ") + fmt.Sprintf(" (%d)\n\n", len(m.Agents)))

	if len(m.Agents) == 0 {
		b.WriteString(warningStyle.Render(" No running agents detected\n"))
		b.WriteString(" Run `pheno-session sync` to discover agents\n")
		return
	}

	b.WriteString(fmt.Sprintf("%-20s %-10s %-10s %-20s\n", "AGENT ID", "HARNESS", "STATUS", "LAST HEARTBEAT"))
	b.WriteString(strings.Repeat("-", 65) + "\n")

	for i, agent := range m.Agents {
		prefix := "  "
		if i == m.Cursor {
			prefix = "> "
		}
		status := successStyle.Render("active")
		if agent.Status != "active" {
			status = warningStyle.Render(agent.Status)
		}
		b.WriteString(fmt.Sprintf("%s%-20s %-10s %v %-20s\n",
			prefix, truncate(agent.AgentID, 20), agent.Harness, status, agent.LastHeartbeat.Format("15:04:05")))
	}
}

// renderSessions renders the sessions tab
func (m Model) renderSessions(b *strings.Builder) {
	b.WriteString(headerStyle.Render(" SESSIONS ") + fmt.Sprintf(" (%d)\n\n", len(m.Sessions)))

	if len(m.Sessions) == 0 {
		b.WriteString(warningStyle.Render(" No sessions found\n"))
		b.WriteString(" Run `pheno-session sync` to import sessions\n")
		return
	}

	b.WriteString(fmt.Sprintf("%-36s %-10s %-10s %-15s %-12s\n", "SESSION ID", "HARNESS", "MODEL", "COMPLETION", "LAST ACTIVITY"))
	b.WriteString(strings.Repeat("-", 85) + "\n")

	for i, session := range m.Sessions {
		prefix := "  "
		if i == m.Cursor {
			prefix = "> "
		}
		completion := getCompletionColor(session.CompletionState)
		b.WriteString(fmt.Sprintf("%s%-36s %-10s %-10s %v %-12s\n",
			prefix, truncate(session.ID, 36), session.Harness, truncate(session.Model, 10), completion, session.LastActivityAt.Format("15:04:05")))
	}
}

// renderTasks renders the tasks tab
func (m Model) renderTasks(b *strings.Builder) {
	b.WriteString(headerStyle.Render(" PENDING TASKS ") + fmt.Sprintf(" (%d)\n\n", len(m.Tasks)))

	if len(m.Tasks) == 0 {
		b.WriteString(warningStyle.Render(" No pending tasks\n"))
		b.WriteString(" Run `pheno-session delegate` to create tasks\n")
		return
	}

	b.WriteString(fmt.Sprintf("%-20s %-10s %-10s %-40s\n", "TASK ID", "AGENT", "STATUS", "TITLE"))
	b.WriteString(strings.Repeat("-", 80) + "\n")

	for i, task := range m.Tasks {
		prefix := "  "
		if i == m.Cursor {
			prefix = "> "
		}
		status := getTaskStatusColor(task.State)
		title := task.Title
		if len(title) > 40 {
			title = title[:37] + "..."
		}
		b.WriteString(fmt.Sprintf("%s%-20s %-10s %v %-40s\n",
			prefix, truncate(task.TaskID, 20), truncate(task.AssignedAgent, 10), status, title))
	}
}

// renderHarnesses renders the harnesses tab
func (m Model) renderHarnesses(b *strings.Builder) {
	b.WriteString(headerStyle.Render(" HARNESS STATUS ") + fmt.Sprintf(" (%d)\n\n", len(m.Harnesses)))

	if len(m.Harnesses) == 0 {
		b.WriteString(warningStyle.Render(" No harness data\n"))
		b.WriteString(" Run `pheno-session sync` to discover harnesses\n")
		return
	}

	b.WriteString(fmt.Sprintf("%-12s %-10s %-10s %-20s\n", "HARNESS", "STATUS", "SESSIONS", "LAST SYNC"))
	b.WriteString(strings.Repeat("-", 55) + "\n")

	for i, h := range m.Harnesses {
		prefix := "  "
		if i == m.Cursor {
			prefix = "> "
		}
		status := successStyle.Render("ok")
		if h.Status != "success" {
			status = errorStyle.Render(h.Status)
		}
		lastSync := "-"
		if !h.LastSyncAt.IsZero() {
			lastSync = h.LastSyncAt.Format("15:04:05")
		}
		b.WriteString(fmt.Sprintf("%s%-12s %v %-10d %-20s\n",
			prefix, h.Harness, status, h.SessionCount, lastSync))
	}
}

// renderHelp renders the help tab
func (m Model) renderHelp(b *strings.Builder) {
	b.WriteString(headerStyle.Render(" KEYBOARD SHORTCUTS ") + "\n\n")
	shortcuts := []struct{ key, desc string }{
		{"1-5", "Switch tabs"}, {"↑/k", "Move up"}, {"↓/j", "Move down"},
		{"r", "Refresh data"}, {"?", "Show this help"}, {"q", "Quit"},
	}
	for _, s := range shortcuts {
		b.WriteString(fmt.Sprintf("  %-8s %s\n", infoStyle.Render(s.key), s.desc))
	}
}

// Helper functions
func truncate(s string, max int) string {
	if len(s) <= max {
		return s
	}
	return s[:max-3] + "..."
}

func getCompletionColor(state string) lipgloss.Style {
	switch state {
	case "completed":
		return successStyle
	case "in_progress":
		return warningStyle
	case "failed":
		return errorStyle
	default:
		return normalStyle
	}
}

func getTaskStatusColor(status string) lipgloss.Style {
	switch status {
	case "completed":
		return successStyle
	case "pending":
		return warningStyle
	case "failed":
		return errorStyle
	default:
		return normalStyle
	}
}

// RunSitback launches the sitback TUI
func RunSitback() error {
	m := NewSitbackModel()
	p := tea.NewProgram(m)
	_, err := p.Run()
	return err
}
