package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"

	"github.com/KooshaPari/pheno-session/internal/store"
	ui "github.com/KooshaPari/pheno-session/internal/ui/tui"
)

var (
	useSQLiteForTUI bool
)

var tuiCmd = &cobra.Command{
	Use:   "tui",
	Short: "Run interactive TUI",
	RunE: func(cmd *cobra.Command, args []string) error {
		// prefer SQLite if requested or exists
		var st store.Store
		var err error
		if useSQLiteForTUI {
			st, err = store.NewSQLiteStore("")
			if err != nil {
				return fmt.Errorf("sqlite store: %w", err)
			}
		} else {
			// try default sqlite path, if missing fallback to JSON
			home := os.Getenv("HOME")
			dbPath := ""
			if home != "" {
				dbPath = fmt.Sprintf("%s/.local/share/phenotype/sessions.db", home)
			}
			if dbPath != "" {
				if _, err := os.Stat(dbPath); err == nil {
					st, err = store.NewSQLiteStore(dbPath)
					if err != nil {
						// fallback to JSON
						st, err = store.NewJSONStore("")
						if err != nil {
							return fmt.Errorf("store fallback error: %w", err)
						}
					}
				} else {
					st, err = store.NewJSONStore("")
					if err != nil {
						return fmt.Errorf("json store error: %w", err)
					}
				}
			} else {
				st, err = store.NewJSONStore("")
				if err != nil {
					return fmt.Errorf("json store error: %w", err)
				}
			}
		}

		m := ui.NewListModel(st)
		if err := ui.Run(m); err != nil {
			return fmt.Errorf("tui run: %w", err)
		}
		return nil
	},
}

func init() {
	tuiCmd.Flags().BoolVar(&useSQLiteForTUI, "sqlite", false, "use sqlite store explicitly (default tries sqlite then json)")
}
