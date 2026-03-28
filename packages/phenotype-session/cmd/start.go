package cmd

import (
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/spf13/cobra"

	"github.com/KooshaPari/phenotype-session/internal/adapter"
	"github.com/KooshaPari/phenotype-session/internal/sqlite"
)

var (
	startProvider string
	startModel    string
	startDir      string
	startName     string
	startOpen     bool
	startNewModel bool
)

var startCmd = &cobra.Command{
	Use:   "start",
	Short: "Start a new session",
	RunE: func(cmd *cobra.Command, args []string) error {
		if startProvider == "" {
			return fmt.Errorf("provider is required (e.g. --provider forge)")
		}
		if startModel == "" {
			return fmt.Errorf("model is required (e.g. --model gpt-4o)")
		}

		params := adapter.StartParams{
			Provider: startProvider,
			Model:    startModel,
			Dir:      startDir,
			Name:     startName,
			Meta:     map[string]any{"new_model": startNewModel},
		}

		// Get adapter for the harness
		registry := adapter.NewAdapterRegistry()
		harnessType := adapter.HarnessType(startProvider)
		a := registry.Get(harnessType)

		sessionInfo, err := a.StartSession(params)
		if err != nil {
			return err
		}

		// Persist to unified SQLite store
		st, err := sqlite.NewUnifiedStore("")
		if err != nil {
			return fmt.Errorf("failed to open store: %w", err)
		}
		defer st.Close()

		// Create session ID if not provided
		sessionID := sessionInfo.ID
		if sessionID == "" {
			sessionID = uuid.New().String()
		}

		// Convert to unified session format
		session := sqlite.Session{
			ID:              sessionID,
			Harness:         string(harnessType),
			Provider:        startProvider,
			Model:           startModel,
			WorkingDir:      startDir,
			State:           "active",
			StartedAt:       time.Now(),
			LastActivityAt:  time.Now(),
			CompletionState: "in_progress",
			IndexedAt:       time.Now(),
		}

		if startName != "" {
			session.Summary = startName
		}

		if err := st.UpsertSession(session); err != nil {
			return fmt.Errorf("failed to create session: %w", err)
		}

		fmt.Printf("Session created: %s (harness=%s provider=%s model=%s)\n",
			sessionID, startProvider, startProvider, startModel)

		if startOpen {
			if err := a.OpenSession(sessionID, ""); err != nil {
				fmt.Printf("warning: open failed: %v\n", err)
			}
		}
		return nil
	},
}

func init() {
	startCmd.Flags().StringVar(&startProvider, "provider", "", "provider (forge, codex, cursor, claude, droid)")
	startCmd.Flags().StringVar(&startModel, "model", "", "model identifier to start (required)")
	startCmd.Flags().StringVar(&startDir, "dir", "", "working directory for session")
	startCmd.Flags().StringVar(&startName, "name", "", "optional session name")
	startCmd.Flags().BoolVar(&startOpen, "open", false, "open after start")
	startCmd.Flags().BoolVar(&startNewModel, "new-model", false, "explicitly start with a new model flow")
}
