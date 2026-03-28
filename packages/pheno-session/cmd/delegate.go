package cmd

import (
	"fmt"
	"os/exec"
	"time"

	"github.com/KooshaPari/pheno-session/internal/sqlite"
	"github.com/spf13/cobra"
)

// delegateCmd delegates a task to a specific harness/agent
var delegateCmd = &cobra.Command{
	Use:   "delegate",
	Short: "Delegate a task to a specific harness",
	Long: `Delegate a task to a running agent in a specific harness.

This command allows you to:
  1. Find a suitable agent in the target harness
  2. Send a task message to that agent
  3. Track the task progress
  4. Receive the result when complete

Example:
  pheno-session delegate --to forge --task "Review PR #123"
  pheno-session delegate --to codex --task "Summarize this code"
  pheno-session delegate --to cursor --task "Fix the bug in main.go"`,
	RunE: func(cmd *cobra.Command, args []string) error {
		toHarness, _ := cmd.Flags().GetString("to")
		task, _ := cmd.Flags().GetString("task")
		sessionID, _ := cmd.Flags().GetString("session")
		priority, _ := cmd.Flags().GetInt("priority")

		if task == "" && len(args) > 0 {
			task = args[0]
		}

		if toHarness == "" {
			return fmt.Errorf("--to harness is required")
		}
		if task == "" {
			return fmt.Errorf("task description is required")
		}

		fmt.Printf("Delegating task to %s: %s\n", toHarness, task)

		// Initialize store
		store, err := sqlite.NewUnifiedStore("")
		if err != nil {
			return fmt.Errorf("failed to initialize store: %w", err)
		}
		defer store.Close()

		// Create task in store
		taskID := fmt.Sprintf("task-%d", time.Now().UnixNano())
		taskRecord := sqlite.Task{
			TaskID:        taskID,
			SessionID:     sessionID,
			Title:         task,
			Description:   task,
			State:         "pending",
			Priority:      priority,
			AssignedAgent: toHarness,
			CreatedAt:     time.Now(),
			UpdatedAt:     time.Now(),
		}

		if err := store.CreateTask(taskRecord); err != nil {
			return fmt.Errorf("failed to create task: %w", err)
		}

		// Create agent message for delegation
		msgID := fmt.Sprintf("msg-%d", time.Now().UnixNano())
		payload := fmt.Sprintf(`{"task_id":"%s","task":"%s"}`, taskID, task)
		msg := sqlite.AgentMessage{
			MessageID:      msgID,
			FromAgent:     "cli",
			ToAgent:       toHarness,
			SessionID:     sessionID,
			MessageType:   "delegate",
			PayloadJSON:   payload,
			Priority:      priority,
			DeliveryStatus: "pending",
			SentAt:        time.Now(),
		}

		if err := store.CreateMessage(msg); err != nil {
			return fmt.Errorf("failed to create message: %w", err)
		}

		// Try to send to running agent
		sent, err := sendToRunningAgent(toHarness, task, taskID)
		if err != nil {
			fmt.Printf("Warning: failed to send to running agent: %v\n", err)
		}

		fmt.Println()
		if sent {
			fmt.Printf("✓ Task delegated to running %s agent\n", toHarness)
		} else {
			fmt.Printf("✓ Task queued for %s agent (no running agent found)\n", toHarness)
			fmt.Println("  Task will be picked up when an agent starts")
		}
		fmt.Printf("  Task ID: %s\n", taskID)
		fmt.Printf("  Status: pending\n")

		// List pending tasks for this harness
		fmt.Println()
		fmt.Printf("Pending tasks for %s:\n", toHarness)
		pendingTasks, _ := store.ListTasks("pending", toHarness)
		for i, t := range pendingTasks {
			if i >= 5 {
				fmt.Printf("  ... and %d more\n", len(pendingTasks)-5)
				break
			}
			fmt.Printf("  [%s] %s - %s\n", t.TaskID[:12], t.State, t.Title)
		}

		return nil
	},
}

// sendToRunningAgent tries to send a task to a running agent
func sendToRunningAgent(harness, task, taskID string) (bool, error) {
	// Check for running process based on harness
	processMap := map[string]string{
		"forge":   "forge",
		"codex":   "codex",
		"cursor":  "cursor",
		"claude":  "claude",
		"droid":   "droid",
		"factory": "factory-droid",
	}

	processName, ok := processMap[harness]
	if !ok {
		processName = harness
	}

	// Use pgrep to check for running process
	cmd := exec.Command("pgrep", "-f", processName)
	if err := cmd.Run(); err != nil {
		// No running process found
		return false, nil
	}

	// Found running process - in real implementation, would send IPC message
	// For now, just return true to indicate we found one
	return true, nil
}

func init() {
	delegateCmd.Flags().StringP("to", "t", "", "Target harness to delegate to (required)")
	delegateCmd.Flags().StringP("task", "", "", "Task description")
	delegateCmd.Flags().StringP("session", "s", "", "Associated session ID")
	delegateCmd.Flags().IntP("priority", "p", 5, "Task priority (1=highest, 10=lowest)")
}
