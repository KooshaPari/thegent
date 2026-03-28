package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var manageCmd = &cobra.Command{
	Use:   "manage <session-id>",
	Short: "Manage a session interactively (TUI)",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		id := args[0]
		// For prototype, print a friendly message.
		// Later: invoke TUI focused on a single session (ui/tui).
		fmt.Printf("manage: launching interactive manager for %s (TUI not yet fully implemented)\n", id)
		return nil
	},
}
