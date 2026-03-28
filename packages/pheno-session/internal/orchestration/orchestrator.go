package orchestration

import (
	"fmt"
	"time"

	"github.com/KooshaPari/pheno-session/internal/adapter"
	"github.com/KooshaPari/pheno-session/internal/sqlite"
)

// OrchestratorConfig holds configuration for the orchestrator
type OrchestratorConfig struct {
	MaxConcurrentTasks int
	EnableAutoRetry   bool
	RetryAttempts     int
	TaskTimeout       int
}

// Orchestrator manages tasks, delegation, and audit
type Orchestrator struct {
	store     *sqlite.UnifiedStore
	messaging *MessagingService
	adapters  map[string]adapter.HarnessAdapter
	config    OrchestratorConfig
}

// AuditReport represents a comprehensive audit report
type AuditReport struct {
	TotalSessions        int
	RunningAgents        int
	PendingTasks         int
	CompletedTasks       int
	FailedTasks          int
	MessagesSent         int
	CompletionStates     map[string]int
	HarnessDistribution map[string]int
	GeneratedAt          time.Time
}

// NewOrchestrator creates a new orchestrator
func NewOrchestrator(store *sqlite.UnifiedStore, messaging *MessagingService, adapters map[string]adapter.HarnessAdapter, config OrchestratorConfig) *Orchestrator {
	if adapters == nil {
		adapters = make(map[string]adapter.HarnessAdapter)
	}
	return &Orchestrator{
		store:     store,
		messaging: messaging,
		adapters:  adapters,
		config:    config,
	}
}

// GetAllTasks returns all tasks from the store
func (o *Orchestrator) GetAllTasks() ([]sqlite.Task, error) {
	return o.store.ListTasks("", "")
}

// DelegateTask delegates a task to an agent
func (o *Orchestrator) DelegateTask(task sqlite.Task) (*sqlite.Task, error) {
	// Set initial task state
	task.State = "pending"
	task.CreatedAt = time.Now()
	task.UpdatedAt = time.Now()

	// Save to store
	err := o.store.CreateTask(task)
	if err != nil {
		return nil, fmt.Errorf("failed to create task: %w", err)
	}

	// Send notification to agent if messaging is available
	if o.messaging != nil && task.AssignedAgent != "" {
		_, _ = o.messaging.SendMessage(
			"orchestrator",
			task.AssignedAgent,
			MessageTypeTask,
			fmt.Sprintf("New task: %s", task.Title),
			task.Description,
			task.Priority,
		)
	}

	return &task, nil
}

// CancelTask cancels a task
func (o *Orchestrator) CancelTask(taskID string) error {
	tasks, err := o.store.ListTasks("", "")
	if err != nil {
		return err
	}

	for _, task := range tasks {
		if task.TaskID == taskID {
			task.State = "cancelled"
			task.UpdatedAt = time.Now()
			return o.store.UpdateTask(task)
		}
	}

	return fmt.Errorf("task not found: %s", taskID)
}

// CompleteTask marks a task as completed
func (o *Orchestrator) CompleteTask(taskID string, result string) error {
	tasks, err := o.store.ListTasks("", "")
	if err != nil {
		return err
	}

	for _, task := range tasks {
		if task.TaskID == taskID {
			task.State = "completed"
			task.UpdatedAt = time.Now()
			return o.store.UpdateTask(task)
		}
	}

	return fmt.Errorf("task not found: %s", taskID)
}

// GenerateAuditReport generates a comprehensive audit report
func (o *Orchestrator) GenerateAuditReport() (*AuditReport, error) {
	report := &AuditReport{
		CompletionStates:     make(map[string]int),
		HarnessDistribution: make(map[string]int),
		GeneratedAt:         time.Now(),
	}

	// Get all sessions
	sessions, err := o.store.ListSessions(sqlite.SessionFilter{All: true, Limit: 10000})
	if err != nil {
		return nil, fmt.Errorf("failed to get sessions: %w", err)
	}
	report.TotalSessions = len(sessions)

	// Count completion states
	for _, s := range sessions {
		report.CompletionStates[s.CompletionState]++
		report.HarnessDistribution[s.Harness]++
	}

	// Get running agents
	agents, err := o.store.GetRunningAgents()
	if err == nil {
		report.RunningAgents = len(agents)
	}

	// Get task stats
	tasks, err := o.store.ListTasks("", "")
	if err == nil {
		report.PendingTasks = 0
		report.CompletedTasks = 0
		report.FailedTasks = 0

		for _, t := range tasks {
			switch t.State {
			case "pending", "assigned", "in_progress":
				report.PendingTasks++
			case "completed":
				report.CompletedTasks++
			case "failed", "cancelled":
				report.FailedTasks++
			}
		}
	}

	// Get message stats
	messages, err := o.messaging.GetMessages("")
	if err == nil {
		report.MessagesSent = len(messages)
	}

	return report, nil
}

// ResolveIssue attempts to resolve an issue by delegating to appropriate agents
func (o *Orchestrator) ResolveIssue(issue string) error {
	// Get available agents
	agents, err := o.store.GetRunningAgents()
	if err != nil || len(agents) == 0 {
		return fmt.Errorf("no agents available for resolution")
	}

	// Create resolution task
	task := sqlite.Task{
		TaskID:        fmt.Sprintf("issue-%d", time.Now().UnixNano()),
		Title:         fmt.Sprintf("Resolve: %s", truncate(issue, 50)),
		Description:   issue,
		Priority:      1, // High priority
		State:         "pending",
		AssignedAgent: agents[0].AgentID,
		CreatedAt:     time.Now(),
		UpdatedAt:     time.Now(),
	}

	_, err = o.DelegateTask(task)
	return err
}

// HealthCheck checks the health of all connected harnesses
func (o *Orchestrator) HealthCheck() map[string]string {
	health := make(map[string]string)

	for name, a := range o.adapters {
		if a == nil {
			health[name] = "unknown"
			continue
		}
		// Try to list sessions as a health check
		_, err := a.ListSessions()
		if err != nil {
			health[name] = "unhealthy"
		} else {
			health[name] = "healthy"
		}
	}

	return health
}

// GetStats returns quick statistics
func (o *Orchestrator) GetStats() (map[string]int, error) {
	stats := make(map[string]int)

	sessions, err := o.store.ListSessions(sqlite.SessionFilter{All: true, Limit: 10000})
	if err == nil {
		stats["total_sessions"] = len(sessions)
		for _, s := range sessions {
			stats["session_"+s.CompletionState]++
		}
	}

	agents, err := o.store.GetRunningAgents()
	if err == nil {
		stats["running_agents"] = len(agents)
	}

	tasks, err := o.store.ListTasks("", "")
	if err == nil {
		stats["total_tasks"] = len(tasks)
		for _, t := range tasks {
			stats["task_"+t.State]++
		}
	}

	return stats, nil
}

func truncate(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen-3] + "..."
}
