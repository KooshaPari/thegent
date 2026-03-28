package cmd

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbletea"
	"github.com/spf13/cobra"

	"github.com/KooshaPari/phenotype-session/internal/sqlite"
	"github.com/KooshaPari/phenotype-session/internal/ui/tui"
)

// Profile types for sitback command
type Profile string

const (
	ProfileLight  Profile = "light"  // Monitor only - read operations
	ProfileMedium Profile = "medium" // Audit + monitor
	ProfileFull   Profile = "full"   // Autonomous - can take actions
)

var (
	sitbackProfile Profile
	sitbackHarness string
	sitbackWatch   bool
	sitbackAudit   bool
)

// HarnessDiscovery discovers available harnesses
type HarnessDiscovery struct {
	Harness   string    `json:"harness"`
	PID       int       `json:"pid"`
	SessionID string    `json:"session_id"`
	Status    string    `json:"status"`
	Model     string    `json:"model"`
	Provider  string    `json:"provider"`
	StartedAt time.Time `json:"started_at"`
}

// discoverRunningHarnesses discovers all running harnesses
func discoverRunningHarnesses() ([]HarnessDiscovery, error) {
	var harnesses []HarnessDiscovery

	// Check common harness processes
	processes := []struct {
		name    string
		pattern []string
	}{
		{"forge", []string{"forge", "forge-"}},
		{"codex", []string{"codex", "codex-"}},
		{"cursor", []string{"cursor", "cursor-"}},
		{"claude", []string{"claude", "claude-code"}},
		{"factory-droid", []string{"droid", "factory-droid"}},
	}

	for _, p := range processes {
		// Simple process check - in production would use actual process discovery
		// For now, return placeholder
		harnesses = append(harnesses, HarnessDiscovery{
			Harness: p.name,
			Status:  "unknown",
		})
	}

	return harnesses, nil
}

// TUI Model for sitback dashboard
type SitbackModel struct {
	Profile     Profile
	Store      *sqlite.UnifiedStore
	Agents     []sqlite.RunningAgent
	Sessions   []sqlite.Session
	Tasks      []sqlite.Task
	Harnesses  []HarnessDiscovery
	SelectedTab int
	Quit       bool
	Err        error
	Width      int
	Height     int
}

func NewSitbackModel(profile Profile) (*SitbackModel, error) {
	store, err := sqlite.NewUnifiedStore("")
	if err != nil {
		return nil, err
	}

	// Load initial data
	agents, _ := store.ListRunningAgents("")
	sessions, _ := store.ListSessions(sqlite.SessionFilter{Limit: 50})
	tasks, _ := store.GetPendingTasks()
	harnesses, _ := discoverRunningHarnesses()

	return &SitbackModel{
		Profile:    profile,
		Store:      store,
		Agents:     agents,
		Sessions:   sessions,
		Tasks:      tasks,
		Harnesses: harnesses,
	}, nil
}

func (m *SitbackModel) Init() tea.Cmd {
	// Perform initial audit log entry
	if m.Profile == ProfileMedium || m.Profile == ProfileFull {
		m.logEvent("sitback_started", map[string]interface{}{
			"profile": m.Profile,
			"agents_count": len(m.Agents),
			"sessions_count": len(m.Sessions),
		})
	}
	return nil
}

func (m *SitbackModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			m.Quit = true
			return m, tea.Quit
		case "tab":
			m.SelectedTab = (m.SelectedTab + 1) % 4
			return m, nil
		case "1":
			m.SelectedTab = 0
			return m, nil
		case "2":
			m.SelectedTab = 1
			return m, nil
		case "3":
			m.SelectedTab = 2
			return m, nil
		case "4":
			m.SelectedTab = 3
			return m, nil
		case "r":
			// Refresh data
			m.Agents, _ = m.Store.ListRunningAgents("")
			m.Sessions, _ = m.Store.ListSessions(sqlite.SessionFilter{Limit: 50})
			m.Tasks, _ = m.Store.GetPendingTasks()
			m.Harnesses, _ = discoverRunningHarnesses()
			return m, nil
		case "a":
			if m.Profile == ProfileFull {
				// Audit all sessions
				m.runAudit()
				return m, nil
			}
		}
	}
	return m, nil
}

func (m *SitbackModel) View() string {
	var b strings.Builder

	// Header
	b.WriteString(fmt.Sprintf("\n  SITBACK (%s mode) | Press q to quit, 1-4 tabs, r refresh\n", m.Profile))
	b.WriteString("  " + strings.Repeat("─", 70) + "\n")

	// Tab indicators
	tabs := []string{"Agents", "Sessions", "Tasks", "Harnesses"}
	for i, tab := range tabs {
		if m.SelectedTab == i {
			b.WriteString(fmt.Sprintf("  [ %d. %s ]", i+1, tab))
		} else {
			b.WriteString(fmt.Sprintf("  ( %d. %s )", i+1, tab))
		}
	}
	b.WriteString("\n\n")

	// Tab content
	switch m.SelectedTab {
	case 0:
		m.viewAgents(&b)
	case 1:
		m.viewSessions(&b)
	case 2:
		m.viewTasks(&b)
	case 3:
		m.viewHarnesses(&b)
	}

	// Footer with stats
	b.WriteString("\n  " + strings.Repeat("─", 70) + "\n")
	b.WriteString(fmt.Sprintf("  Agents: %d | Sessions: %d | Tasks: %d | Harnesses: %d",
		len(m.Agents), len(m.Sessions), len(m.Tasks), len(m.Harnesses)))
	
	if m.Err != nil {
		b.WriteString(fmt.Sprintf("\n  Error: %v", m.Err))
	}

	return b.String()
}

func (m *SitbackModel) viewAgents(b *strings.Builder) {
	if len(m.Agents) == 0 {
		b.WriteString("  No running agents found.\n")
		return
	}

	b.WriteString(fmt.Sprintf("  %-20s %-10s %-15s %-20s %-10s\n", "AGENT ID", "HARNESS", "STATUS", "SESSION", "UPTIME"))
	b.WriteString("  " + strings.Repeat("─", 80) + "\n")

	for _, agent := range m.Agents {
		uptime := time.Since(agent.StartedAt).Round(time.Second)
		session := agent.SessionID
		if session == "" {
			session = "-"
		} else if len(session) > 18 {
			session = session[:18]
		}
		b.WriteString(fmt.Sprintf("  %-20s %-10s %-15s %-20s %-10s\n",
			truncate(agent.AgentID, 20),
			truncate(agent.Harness, 10),
			agent.Status,
			session,
			uptime,
		))
	}
}

func (m *SitbackModel) viewSessions(b *strings.Builder) {
	if len(m.Sessions) == 0 {
		b.WriteString("  No sessions found.\n")
		return
	}

	b.WriteString(fmt.Sprintf("  %-8s %-10s %-12s %-15s %-20s %s\n", "STATE", "HARNESS", "MODEL", "COMPLETION", "UPDATED", "SUMMARY"))
	b.WriteString("  " + strings.Repeat("─", 90) + "\n")

	for _, session := range m.Sessions {
		completion := session.CompletionState
		if completion == "" {
			completion = "unknown"
		}
		updated := session.LastActivityAt.Format("2006-01-02 15:04")
		if session.LastActivityAt.IsZero() {
			updated = "-"
		}
		summary := session.Summary
		if summary == "" {
			summary = "-"
		}
		b.WriteString(fmt.Sprintf("  %-8s %-10s %-12s %-15s %-20s %s\n",
			session.State,
			truncate(session.Harness, 10),
			truncate(session.Model, 12),
			truncate(completion, 15),
			updated,
			truncate(summary, 30),
		))
	}
}

func (m *SitbackModel) viewTasks(b *strings.Builder) {
	if len(m.Tasks) == 0 {
		b.WriteString("  No pending tasks.\n")
		return
	}

	b.WriteString(fmt.Sprintf("  %-8s %-30s %-10s %-15s\n", "PRIORITY", "TITLE", "STATE", "AGENT"))
	b.WriteString("  " + strings.Repeat("─", 70) + "\n")

	for _, task := range m.Tasks {
		agent := task.AssignedAgent
		if agent == "" {
			agent = "-"
		}
		b.WriteString(fmt.Sprintf("  %-8d %-30s %-10s %-15s\n",
			task.Priority,
			truncate(task.Title, 30),
			task.State,
			truncate(agent, 15),
		))
	}
}

func (m *SitbackModel) viewHarnesses(b *strings.Builder) {
	if len(m.Harnesses) == 0 {
		b.WriteString("  No harnesses detected.\n")
		return
	}

	b.WriteString(fmt.Sprintf("  %-15s %-10s %-15s %-20s\n", "HARNESS", "PID", "STATUS", "SESSION"))
	b.WriteString("  " + strings.Repeat("─", 65) + "\n")

	for _, h := range m.Harnesses {
		session := h.SessionID
		if session == "" {
			session = "-"
		}
		b.WriteString(fmt.Sprintf("  %-15s %-10d %-15s %-20s\n",
			h.Harness,
			h.PID,
			h.Status,
			truncate(session, 20),
		))
	}
}

func (m *SitbackModel) runAudit() {
	// Audit all sessions for completion state
	for _, session := range m.Sessions {
		if session.CompletionState == "" || session.CompletionState == "unknown" {
			// Log as audit finding
			m.logEvent("audit_session", map[string]interface{}{
				"session_id": session.ID,
				"harness": session.Harness,
				"state": session.State,
				"completion_state": session.CompletionState,
			})
		}
	}

	// Audit all agents
	for _, agent := range m.Agents {
		// Check heartbeat age
		age := time.Since(agent.LastHeartbeat)
		if age > 5*time.Minute {
			m.logEvent("stale_agent", map[string]interface{}{
				"agent_id": agent.AgentID,
				"last_heartbeat": age.String(),
			})
		}
	}

	m.logEvent("audit_complete", map[string]interface{}{
		"sessions_audited": len(m.Sessions),
		"agents_audited": len(m.Agents),
	})
}

func (m *SitbackModel) logEvent(eventType string, details map[string]interface{}) {
	detailsJSON, _ := json.Marshal(details)
	entry := sqlite.AuditLogEntry{
		AuditID:    fmt.Sprintf("audit-%d", time.Now().UnixNano()),
		Timestamp:  time.Now(),
		AgentID:    "",
		SessionID:  "",
		EventType:  eventType,
		DetailsJSON: string(detailsJSON),
	}
	_ = m.Store.CreateAuditEntry(entry)
}

func truncate(s string, max int) string {
	if len(s) > max {
		return s[:max-2] + ".."
	}
	return s
}

var sitbackCmd = &cobra.Command{
	Use:   "sitback",
	Short: "Autonomous orchestration dashboard for all agents and sessions",
	Long: `Sitback provides an overview of all running agents and past sessions
across all harnesses (forge, codex, cursor, claude, factory-droid).

Profiles:
  light  - Read-only monitoring
  medium - Audit + monitoring  
  full   - Autonomous actions and delegation

Examples:
  pheno-session sitback                    # Start with light profile
  pheno-session sitback --profile medium   # Medium profile with audit
  pheno-session sitback --profile full    # Full autonomous mode`,
	RunE: func(cmd *cobra.Command, args []string) error {
		// Handle non-TUI modes first
		if sitbackAudit {
			return runSitbackAudit()
		}

		// Launch TUI from package
		return tui.RunSitback()
	},
}

func runSitbackAudit() error {
	store, err := sqlite.NewUnifiedStore("")
	if err != nil {
		return fmt.Errorf("failed to open store: %w", err)
	}
	defer store.Close()

	// Get all sessions
	sessions, err := store.ListSessions(sqlite.SessionFilter{Limit: 1000})
	if err != nil {
		return fmt.Errorf("failed to list sessions: %w", err)
	}

	// Get all running agents
	agents, err := store.ListRunningAgents("")
	if err != nil {
		return fmt.Errorf("failed to list agents: %w", err)
	}

	// Get pending tasks
	tasks, err := store.GetPendingTasks()
	if err != nil {
		return fmt.Errorf("failed to get tasks: %w", err)
	}

	// Print audit report
	fmt.Println("\n=== SITBACK AUDIT REPORT ===")
	fmt.Printf("Generated: %s\n\n", time.Now().Format(time.RFC3339))

	fmt.Printf("## SUMMARY\n")
	fmt.Printf("Total Sessions: %d\n", len(sessions))
	fmt.Printf("Running Agents: %d\n", len(agents))
	fmt.Printf("Pending Tasks: %d\n\n", len(tasks))

	// Analyze completion states
	completionStates := make(map[string]int)
	for _, s := range sessions {
		state := s.CompletionState
		if state == "" {
			state = "unknown"
		}
		completionStates[state]++
	}

	fmt.Printf("## COMPLETION STATES\n")
	for state, count := range completionStates {
		fmt.Printf("  %s: %d\n", state, count)
	}
	fmt.Println()

	// Analyze harness distribution
	harnessCounts := make(map[string]int)
	for _, s := range sessions {
		harnessCounts[s.Harness]++
	}

	fmt.Printf("## HARNESS DISTRIBUTION\n")
	for harness, count := range harnessCounts {
		fmt.Printf("  %s: %d sessions\n", harness, count)
	}
	fmt.Println()

	// Identify stale agents
	fmt.Printf("## AGENT STATUS\n")
	staleCount := 0
	for _, a := range agents {
		age := time.Since(a.LastHeartbeat)
		if age > 5*time.Minute {
			fmt.Printf("  [STALE] %s (heartbeat: %s ago)\n", a.AgentID, age.Round(time.Second))
			staleCount++
		} else {
			fmt.Printf("  [OK] %s (%s)\n", a.AgentID, a.Status)
		}
	}
	if staleCount == 0 {
		fmt.Println("  All agents are healthy.")
	}
	fmt.Println()

	// Task analysis
	fmt.Printf("## TASK ANALYSIS\n")
	if len(tasks) > 0 {
		fmt.Printf("  %d tasks pending:\n", len(tasks))
		for _, t := range tasks[:min(10, len(tasks))] {
			fmt.Printf("    - [%d] %s\n", t.Priority, truncate(t.Title, 50))
		}
		if len(tasks) > 10 {
			fmt.Printf("    ... and %d more\n", len(tasks)-10)
		}
	} else {
		fmt.Println("  No pending tasks.")
	}
	fmt.Println()

	// Log audit
	entry := sqlite.AuditLogEntry{
		AuditID:    fmt.Sprintf("audit-%d", time.Now().UnixNano()),
		Timestamp:  time.Now(),
		EventType:  "audit_report",
		DetailsJSON: fmt.Sprintf(`{"sessions":%d,"agents":%d,"tasks":%d}`, len(sessions), len(agents), len(tasks)),
	}
	_ = store.CreateAuditEntry(entry)

	return nil
}

func init() {
	sitbackCmd.Flags().StringVar(&sitbackHarness, "harness", "",
		"Filter by harness (forge, codex, cursor, claude, droid)")
	sitbackCmd.Flags().BoolVarP(&sitbackWatch, "watch", "w", false,
		"Watch mode - continuously update (TUI only)")
	sitbackCmd.Flags().BoolVar(&sitbackAudit, "audit", false,
		"Run audit report and exit (non-interactive)")
	sitbackCmd.Flags().IntVar(&sitbackAuditLimit, "limit", 100,
		"Limit number of sessions to audit")

	// Register profile flag using VarP with stringFlag
	sitbackCmd.Flags().VarP(newStringFlag(ProfileLight), "profile", "p",
		"Profile: light (monitor), medium (audit), full (autonomous)")
}

// StringFlag helper for enum flags
type stringFlag string

func newStringFlag(defaultVal Profile) *stringFlag {
	f := stringFlag(defaultVal)
	return &f
}

func (f *stringFlag) String() string {
	return string(*f)
}

func (f *stringFlag) Set(s string) error {
	switch strings.ToLower(s) {
	case "light", "l":
		*f = stringFlag(ProfileLight)
	case "medium", "m":
		*f = stringFlag(ProfileMedium)
	case "full", "f":
		*f = stringFlag(ProfileFull)
	default:
		return fmt.Errorf("invalid profile: %s (use light, medium, or full)", s)
	}
	return nil
}

func (f *stringFlag) Type() string {
	return "profile"
}
