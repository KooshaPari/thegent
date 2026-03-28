package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"text/tabwriter"

	"github.com/spf13/cobra"

	"github.com/KooshaPari/pheno-session/internal/sqlite"
)

var (
	listHarness  string
	listProvider string
	listDir      string
	listAll      bool
	listSort     string
	listLimit    int
	listJSONOut  bool
)

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List sessions",
	RunE: func(cmd *cobra.Command, args []string) error {
		st, err := sqlite.NewUnifiedStore("")
		if err != nil {
			return fmt.Errorf("failed to open store: %w", err)
		}
		defer st.Close()

		filter := sqlite.SessionFilter{
			Harness:  listHarness,
			State:   "",
			TeamID:  "",
			WorkingDir: listDir,
			All:     listAll,
			SortBy:  listSort,
			Limit:   listLimit,
		}

		sessions, err := st.ListSessions(filter)
		if err != nil {
			return err
		}

		if listJSONOut {
			enc := json.NewEncoder(os.Stdout)
			enc.SetIndent("", "  ")
			return enc.Encode(sessions)
		}

		w := tabwriter.NewWriter(os.Stdout, 4, 4, 2, ' ', 0)
		fmt.Fprintf(w, "SESSION\tHARNESS\tMODEL\tSTATE\tCOMPLETION\tLAST_ACTIVITY\n")
		for _, s := range sessions {
			lastActivity := ""
			if !s.LastActivityAt.IsZero() {
				lastActivity = s.LastActivityAt.Format("2006-01-02 15:04")
			}
			completion := s.CompletionState
			if completion == "" {
				completion = "-"
			}
			fmt.Fprintf(w, "%s\t%s\t%s\t%s\t%s\t%s\n", 
				s.ID, s.Harness, s.Model, s.State, completion, lastActivity)
		}
		return w.Flush()
	},
}

func init() {
	listCmd.Flags().StringVarP(&listHarness, "harness", "H", "", "harness filter (codex|forge|cursor|claude|droid)")
	listCmd.Flags().StringVar(&listProvider, "provider", "", "provider filter")
	listCmd.Flags().StringVar(&listDir, "dir", "", "directory filter (off by default)")
	listCmd.Flags().BoolVar(&listAll, "all", true, "show all (default)")
	listCmd.Flags().StringVar(&listSort, "sort", "started_at", "sort by (started_at|last_activity|completion_state)")
	listCmd.Flags().IntVar(&listLimit, "limit", 100, "max sessions to return")
	listCmd.Flags().BoolVar(&listJSONOut, "json", false, "output JSON")
}
