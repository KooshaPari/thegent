package cmd

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/KooshaPari/pheno-session/internal/sqlite"
)

var (
	openSessionID string
	openIn        string
)

var openCmd = &cobra.Command{
	Use:   "open <session-id>",
	Short: "Open a session in a harness",
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

		target := openIn
		if target == "" {
			target = session.Harness
		}

		fmt.Printf("Opening session %s in harness: %s\n", session.ID, target)
		fmt.Printf("  Model: %s\n", session.Model)
		fmt.Printf("  Provider: %s\n", session.Provider)

		// Placeholder for actual harness integration
		fmt.Println()
		fmt.Println("Note: Full harness integration not yet implemented.")
		fmt.Println("To implement, integrate with harness-specific APIs or CLIs.")

		return nil
	},
}

func init() {
	openCmd.Flags().StringVar(&openIn, "open-in", "", "target harness to open in (cursor|forge|codex|claude|droid)")
}
