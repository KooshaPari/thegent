package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var (
	cfgFile string
	verbose bool
)

var rootCmd = &cobra.Command{
	Use:   "pheno-session",
	Short: "Unified session orchestrator for all LLM harnesses",
	Long: `pheno-session manages sessions across different LLM harnesses/providers
(codex, forge, cursor, claude, droid).

SITBACK ORCHESTRATION:
  sitback           - Autonomous orchestration dashboard
  sitback --audit   - Run audit report and exit
  bridge            - Bridge to thegent's sitback
  sync              - Sync session data from all harnesses
  delegate          - Delegate tasks to specific harnesses

SESSION MANAGEMENT:
  list              - List sessions (default: all, sorted by updated_by)
  start             - Start new session with provider/model
  open              - Open session in harness
  transfer          - Transfer session between harnesses

Default behavior: lists all sessions (directory filter off).
Default sort: updated_by (last message actor).`,
}

func Execute() error {
	return rootCmd.Execute()
}

func init() {
	rootCmd.PersistentFlags().StringVarP(&cfgFile, "config", "c", "", "config file path")
	rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "verbose output")

	// Session management subcommands
	rootCmd.AddCommand(listCmd)
	rootCmd.AddCommand(startCmd)
	rootCmd.AddCommand(openCmd)
	rootCmd.AddCommand(transferCmd)
	rootCmd.AddCommand(manageCmd)
	rootCmd.AddCommand(tuiCmd)

	// Sitback orchestration subcommands
	rootCmd.AddCommand(sitbackCmd)
	rootCmd.AddCommand(bridgeCmd)
	rootCmd.AddCommand(syncCmd)
	rootCmd.AddCommand(delegateCmd)
	rootCmd.AddCommand(auditCmd)

	// Generation subcommands
	rootCmd.AddCommand(completionCmd)
	rootCmd.AddCommand(genDocsCmd)
}

func mustGetEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		fmt.Printf("required env %s not set\n", key)
		os.Exit(2)
	}
	return v
}
