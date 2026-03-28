package cmd

import (
	"github.com/spf13/cobra"
)

// auditCmd performs a comprehensive audit of all sessions and agents
var auditCmd = &cobra.Command{
	Use:   "audit",
	Short: "Comprehensive audit of all sessions and agents",
	Long: `Perform a comprehensive audit of all sessions and agents across all harnesses.

This command:
  1. Lists all sessions with their completion states
  2. Checks health of all running agents
  3. Identifies stale or orphaned sessions
  4. Reports on pending tasks and blockers
  5. Logs audit results to the unified store

Example:
  pheno-session audit --limit 100`,
	RunE: func(cmd *cobra.Command, args []string) error {
		return runSitbackAudit()
	},
}

func init() {
	auditCmd.Flags().IntVar(&sitbackAuditLimit, "limit", 100,
		"Limit number of sessions to audit")
}

var sitbackAuditLimit int
