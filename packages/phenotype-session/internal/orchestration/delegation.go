package orchestration

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"

	"github.com/KooshaPari/phenotype-session/internal/adapter"
	"github.com/KooshaPari/phenotype-session/internal/monitor"
	"github.com/KooshaPari/phenotype-session/internal/sqlite"
)

// Task represents a task that can be delegated to an agent
type Task struct {
	ID              string            `json:"id"`
	Title           string            `json:"title"`
	Description     string            `json:"description"`
	Priority        int               `json:"priority"` // 1-5, 1 is highest
	State           string            `json:"state"`    // pending, assigned, in_progress, completed, failed
	AssignedAgent   string            `json:"assigned_agent"`
	Harness         string            `json:"harness"`
	CreatedAt       time.Time        `json:"created_at"`
	StartedAt       time.Time        `json:"started_at"`
	CompletedAt     time.Time        `json:"completed_at"`
	Result          string            `json:"result"`
	Error           string            `json:"error"`
	DelegationChain []string          `json:"delegation_chain"` // List of agents that have worked on this
	Metadata        map[string]interface{} `json:"metadata"`
}

// DelegationService handles task delegation across harnesses
type DelegationService struct {
	store    *sqlite.UnifiedStore
	registry *adapter.AdapterRegistry
	monitor  *monitor.HeartbeatMonitor
}

// NewDelegationService creates a new delegation service
func NewDelegationService(store *sqlite.UnifiedStore) *DelegationService {
	return &DelegationService{
		store:    store,
		registry: adapter.NewAdapterRegistry(),
	}
}

// CreateTask creates a new task
func (s *DelegationService) CreateTask(title, description string, priority int, harness string) (*Task, error) {
	if priority < 1 || priority > 5 {
		priority = 3 // Default to medium
	}
	
	task := &Task{
		ID:              uuid.New().String(),
		Title:           title,
		Description:     description,
		Priority:        priority,
		State:           "pending",
		Harness:         harness,
		CreatedAt:       time.Now(),
		DelegationChain: []string{},
		Metadata:        make(map[string]interface{}),
	}
	
	// Store in database
	dbTask := sqlite.Task{
		TaskID:      task.ID,
		Title:       task.Title,
		Description: task.Description,
		Priority:    task.Priority,
		State:       task.State,
		CreatedAt:   task.CreatedAt,
	}
	
	if err := s.store.CreateTask(dbTask); err != nil {
		return nil, fmt.Errorf("failed to create task: %w", err)
	}
	
	// Log event
	s.logEvent("task_created", task.ID, "", map[string]interface{}{
		"title":    title,
		"priority": priority,
		"harness": harness,
	})
	
	return task, nil
}

// DelegateTask assigns a task to an available agent
func (s *DelegationService) DelegateTask(taskID, harness string, params map[string]interface{}) (*Task, error) {
	// Get task
	tasks, err := s.store.ListTasks("", "")
	if err != nil {
		return nil, err
	}
	
	var task *Task
	var dbTask sqlite.Task
	for _, t := range tasks {
		if t.TaskID == taskID {
			task = &Task{
				ID:            t.TaskID,
				Title:         t.Title,
				Description:   t.Description,
				Priority:      t.Priority,
				State:         t.State,
				AssignedAgent: t.AssignedAgent,
				CreatedAt:     t.CreatedAt,
			}
			dbTask = t
			break
		}
	}
	
	if task == nil {
		return nil, fmt.Errorf("task not found: %s", taskID)
	}
	
	// Find available agent in target harness
	availableAgents := s.registry.ListAvailable()
	
	var targetAgent string
	for _, agentHarness := range availableAgents {
		if harness == "" || string(agentHarness) == harness {
			// Get agents for this harness
			harnessAdapter := s.registry.Get(agentHarness)
			agents, err := harnessAdapter.ListAgents()
			if err == nil && len(agents) > 0 {
				targetAgent = agents[0].ID
				break
			}
		}
	}
	
	if targetAgent == "" {
		// Create a new session/agent for the task
		h := adapter.HarnessType(harness)
		if h == "" {
			h = adapter.HarnessForge
		}
		harnessAdapter := s.registry.Get(h)
		
		startParams := adapter.StartParams{
			Name:     task.Title,
			Provider: harness,
		}
		
		session, err := harnessAdapter.StartSession(startParams)
		if err != nil {
			return nil, fmt.Errorf("failed to start session: %w", err)
		}
		
		targetAgent = session.ID
		// task.SessionID = session.ID - SessionID not in Task struct
	}
	
	// Update task state
	task.State = "assigned"
	task.AssignedAgent = targetAgent
	task.DelegationChain = append(task.DelegationChain, targetAgent)
	
	// Update in database
	dbTask.State = task.State
	dbTask.AssignedAgent = task.AssignedAgent
	dbTask.StartedAt = time.Now()
	
	if err := s.store.UpdateTask(dbTask); err != nil {
		return nil, fmt.Errorf("failed to update task: %w", err)
	}
	
	// Send task to agent
	if err := s.sendTaskToAgent(targetAgent, task); err != nil {
		// Log but don't fail
		fmt.Printf("Warning: failed to send task to agent: %v\n", err)
	}
	
	// Log event
	s.logEvent("task_delegated", task.ID, targetAgent, map[string]interface{}{
		"harness": harness,
		"agent":   targetAgent,
	})
	
	return task, nil
}

// sendTaskToAgent sends a task message to an agent
func (s *DelegationService) sendTaskToAgent(agentID string, task *Task) error {
	// Extract harness from agent ID
	harness := extractHarness(agentID)
	adapter := s.registry.Get(adapter.HarnessType(harness))
	
	// Send message with task details
	message := fmt.Sprintf("TASK: %s\n\n%s\n\nPriority: %d",
		task.Title, task.Description, task.Priority)
	
	return adapter.SendMessage(agentID, message)
}

// extractHarness extracts harness type from agent ID
func extractHarness(agentID string) string {
	parts := strings.Split(agentID, "-")
	if len(parts) > 0 {
		return parts[0]
	}
	return "forge"
}

// CompleteTask marks a task as completed
func (s *DelegationService) CompleteTask(taskID string, result string) error {
	tasks, err := s.store.ListTasks("", "")
	if err != nil {
		return err
	}
	
	for _, t := range tasks {
		if t.TaskID == taskID {
			t.State = "completed"
			t.CompletedAt = time.Now()
			t.ResultJSON = result
			
			if err := s.store.UpdateTask(t); err != nil {
				return err
			}
			
			s.logEvent("task_completed", taskID, "", map[string]interface{}{
				"result": result,
			})
			
			return nil
		}
	}
	
	return fmt.Errorf("task not found: %s", taskID)
}

// FailTask marks a task as failed
func (s *DelegationService) FailTask(taskID string, errMsg string) error {
	tasks, err := s.store.ListTasks("", "")
	if err != nil {
		return err
	}
	
	for _, t := range tasks {
		if t.TaskID == taskID {
			t.State = "failed"
			t.CompletedAt = time.Now()
			t.ErrorMessage = errMsg
			
			if err := s.store.UpdateTask(t); err != nil {
				return err
			}
			
			s.logEvent("task_failed", taskID, "", map[string]interface{}{
				"error": errMsg,
			})
			
			return nil
		}
	}
	
	return fmt.Errorf("task not found: %s", taskID)
}

// GetTasks returns all tasks
func (s *DelegationService) GetTasks(state, agentID string) ([]Task, error) {
	tasks, err := s.store.ListTasks(state, agentID)
	if err != nil {
		return nil, err
	}
	
	result := make([]Task, len(tasks))
	for i, t := range tasks {
		result[i] = Task{
			ID:            t.TaskID,
			Title:         t.Title,
			Description:   t.Description,
			Priority:      t.Priority,
			State:         t.State,
			AssignedAgent: t.AssignedAgent,
			CreatedAt:     t.CreatedAt,
			StartedAt:     t.StartedAt,
			CompletedAt:   t.CompletedAt,
			Result:        t.ResultJSON,
			Error:         t.ErrorMessage,
		}
	}
	
	return result, nil
}

// ReDelegateTask re-delegates a failed or stalled task
func (s *DelegationService) ReDelegateTask(taskID, newHarness string) (*Task, error) {
	tasks, err := s.store.ListTasks("", "")
	if err != nil {
		return nil, err
	}
	
	var task *Task
	for _, t := range tasks {
		if t.TaskID == taskID {
			task = &Task{
				ID:            t.TaskID,
				Title:         t.Title,
				Description:   t.Description,
				Priority:      t.Priority,
				State:         t.State,
				AssignedAgent: t.AssignedAgent,
				CreatedAt:     t.CreatedAt,
			}
			break
		}
	}
	
	if task == nil {
		return nil, fmt.Errorf("task not found: %s", taskID)
	}
	
	// Reset state and delegate to new harness
	task.State = "pending"
	return s.DelegateTask(taskID, newHarness, nil)
}

// logEvent logs an event to the audit log
func (s *DelegationService) logEvent(eventType, taskID, agentID string, details map[string]interface{}) {
	detailsJSON, _ := json.Marshal(details)
	
	entry := sqlite.AuditLogEntry{
		AuditID:     fmt.Sprintf("%s-%s-%d", eventType, taskID, time.Now().UnixNano()),
		Timestamp:   time.Now(),
		AgentID:     agentID,
		SessionID:  taskID,
		EventType:  eventType,
		DetailsJSON: string(detailsJSON),
	}
	
	_ = s.store.CreateAuditEntry(entry)
}

// Task with session ID helper
func (t *Task) SetSessionID(sessionID string) {
	t.Metadata["session_id"] = sessionID
}

// DelegationChain returns a formatted delegation chain
func (t *Task) DelegationChainString() string {
	return strings.Join(t.DelegationChain, " → ")
}
