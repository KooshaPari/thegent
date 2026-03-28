package cmd

import (
	"fmt"
	"os/exec"
	"time"

	"github.com/KooshaPari/pheno-session/internal/adapter"
	"github.com/KooshaPari/pheno-session/internal/sqlite"
	"github.com/spf13/cobra"
)

// syncCmd syncs session data between harnesses and the unified store
var syncCmd = &cobra.Command{
	Use:   "sync",
	Short: "Sync session data from all harnesses",
	Long: `Sync session data from all connected harnesses into the unified store.

This command discovers all running agents and historical sessions from
each harness and imports them into the unified SQLite database.

Supported harnesses:
  - forge
  - codex
  - cursor
  - claude
  - factory-droid`,
	RunE: func(cmd *cobra.Command, args []string) error {
		verbose, _ := cmd.Flags().GetBool("verbose")

		// Handle watch mode
		if watchMode {
			return runSyncWatch(verbose)
		}

		// Single sync
		return runSyncOnce(verbose)
	},
}

// runSyncOnce performs a single sync
func runSyncOnce(verbose bool) error {
	if verbose {
		fmt.Println("=== SESSION SYNC (verbose) ===")
	} else {
		fmt.Println("=== SESSION SYNC ===")
	}
	fmt.Println()

	// Initialize store
	store, err := sqlite.NewUnifiedStore("")
	if err != nil {
		return fmt.Errorf("failed to initialize store: %w", err)
	}
	defer store.Close()

	// Discover and sync each harness
	harnesses := []struct {
		name    string
		process string
		adapter adapter.HarnessAdapter
	}{
		{"forge", "forge", adapter.NewForgeAdapterV2()},
		{"codex", "codex", adapter.NewCodexAdapter()},
		{"cursor", "cursor", adapter.NewCursorAdapter()},
		{"claude", "claude", adapter.NewClaudeAdapter()},
		{"droid", "droid", adapter.NewDroidAdapter()},
	}

	totalSessions := 0
	totalAgents := 0

	for _, h := range harnesses {
		if verbose {
			fmt.Printf("Syncing %s...", h.name)
		}

		// Sync sessions from adapter
		sessions, err := h.adapter.ListSessions()
		if err == nil {
			for _, s := range sessions {
				session := sqlite.Session{
					ID:              s.ID,
					Harness:         h.name,
					Model:           s.Model,
					State:           s.State,
					CompletionState: "in_progress",
					LastActivityAt:  s.LastActivityAt,
					StartedAt:       s.CreatedAt,
				}
				store.UpsertSession(session)
				totalSessions++
			}
		}

		// Check if harness is running
		isRunning := isProcessRunning(h.process)
		if isRunning {
			agentID := fmt.Sprintf("agent-%s-%d", h.name, time.Now().Unix())
			agent := sqlite.RunningAgent{
				AgentID:        agentID,
				Harness:        h.name,
				PID:            getPID(h.process),
				StartedAt:      time.Now(),
				LastHeartbeat:  time.Now(),
				Status:         "active",
			}
			store.CreateRunningAgent(agent)
			totalAgents++

			if verbose {
				fmt.Printf(" running (PID: %d)\n", agent.PID)
			}
		} else if verbose {
			fmt.Println(" not running")
		}

		// Record sync status
		sync := sqlite.HarnessSync{
			Harness:       h.name,
			LastSyncAt:   time.Now(),
			Status:       "success",
			SessionCount: len(sessions),
		}
		store.RecordHarnessSync(sync)

		if !verbose {
			if isRunning {
				fmt.Printf("✓ %s: %d sessions, agent running\n", h.name, len(sessions))
			} else {
				fmt.Printf("  %s: %d sessions, no agent\n", h.name, len(sessions))
			}
		}
	}

	fmt.Println()
	fmt.Printf("Synced %d sessions from %d harnesses\n", totalSessions, len(harnesses))
	fmt.Printf("Running agents: %d\n", totalAgents)
	fmt.Println()

	return nil
}

// runSyncWatch runs continuous sync in watch mode
func runSyncWatch(verbose bool) error {
	interval := time.Duration(syncInterval) * time.Second
	fmt.Println("=== SESSION SYNC (WATCH MODE) ===")
	fmt.Printf("Polling every %v. Press Ctrl+C to stop.\n\n", interval)

	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	// Initial sync
	if err := runSyncOnce(verbose); err != nil {
		return err
	}

	for {
		select {
		case <-ticker.C:
			fmt.Println("\n--- Re-syncing ---")
			if err := runSyncOnce(verbose); err != nil {
				fmt.Printf("Sync error: %v\n", err)
			}
		}
	}
}

var (
	watchMode    bool
	syncInterval int
)

func init() {
	rootCmd.AddCommand(syncCmd)
	syncCmd.Flags().BoolVarP(&watchMode, "watch", "w", false, "Watch mode: continuously sync")
	syncCmd.Flags().IntVarP(&syncInterval, "interval", "i", 30, "Sync interval in seconds (watch mode)")
}

// isProcessRunning checks if a process is running
func isProcessRunning(name string) bool {
	cmd := exec.Command("pgrep", "-f", name)
	return cmd.Run() == nil
}

// getPID gets the PID of a running process
func getPID(name string) int {
	cmd := exec.Command("pgrep", "-f", name)
	output, _ := cmd.Output()
	if len(output) > 0 {
		var pid int
		fmt.Sscanf(string(output), "%d", &pid)
		return pid
	}
	return 0
}

// boolToInt converts bool to int for JSON
func boolToInt(b bool) int {
	if b {
		return 1
	}
	return 0
}
