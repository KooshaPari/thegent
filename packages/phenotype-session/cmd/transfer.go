package cmd

import (
	"fmt"
	"time"

	"github.com/spf13/cobra"

	"github.com/KooshaPari/phenotype-session/internal/sqlite"
)

var (
	transferToHarness string
	transferProvider  string
	transferConfirm   bool
)

var transferCmd = &cobra.Command{
	Use:   "transfer <session-id>",
	Short: "Transfer a session to another harness",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		id := args[0]
		store, err := sqlite.NewUnifiedStore("")
		if err != nil {
			return err
		}
		defer store.Close()

		session, err := store.GetSession(id)
		if err != nil {
			return err
		}

		if transferToHarness == "" {
			return fmt.Errorf("--to-harness is required")
		}

		fmt.Printf("Transferring session %s\n", session.ID)
		fmt.Printf("  From: %s\n", session.Harness)
		fmt.Printf("  To: %s\n", transferToHarness)
		fmt.Printf("  Model: %s\n", session.Model)

		// Placeholder for actual transfer logic
		// In production, this would:
		// 1. Export session state from source harness
		// 2. Create new session in target harness
		// 3. Update session record with new harness info

		fmt.Println()
		fmt.Println("Note: Full transfer not yet implemented.")
		fmt.Println("To implement, integrate with harness-specific transfer APIs.")

		// Create a placeholder transfer record
		newSession := sqlite.Session{
			ID:              fmt.Sprintf("transferred-%d", time.Now().UnixNano()),
			ParentSessionID: session.ID,
			Harness:         transferToHarness,
			Model:           session.Model,
			State:           "transferred",
			CompletionState: "in_progress",
			StartedAt:       time.Now(),
			LastActivityAt:  time.Now(),
		}

		if err := store.CreateSession(newSession); err != nil {
			fmt.Printf("Warning: Failed to create transfer record: %v\n", err)
		}

		return nil
	},
}

func init() {
	transferCmd.Flags().StringVar(&transferToHarness, "to-harness", "", "target harness (cursor|forge|codex|claude|droid)")
	transferCmd.Flags().StringVar(&transferProvider, "provider", "", "target provider name (if different)")
	transferCmd.Flags().BoolVar(&transferConfirm, "confirm", false, "skip confirmation prompts")
}
