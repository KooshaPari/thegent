package cmd

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
	"github.com/spf13/cobra/doc"
)

var genDocsCmd = &cobra.Command{
	Use:   "gen-docs [output-dir]",
	Short: "Generate markdown documentation",
	Long: `Generate markdown documentation for all pheno-session commands.

Output is written to the specified directory (default: ./docs).
Each command gets its own markdown file.

Example:
  $ pheno-session gen-docs ./docs
  $ ls docs/
  pheno-session.md  list.md  start.md  ...
`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		outDir := args[0]
		if outDir == "" {
			outDir = "docs"
		}

		// Create directory if it doesn't exist
		if err := os.MkdirAll(outDir, 0755); err != nil {
			return fmt.Errorf("create dir: %w", err)
		}

		// Generate docs
		linkHandler := func(s string) string {
			return s
		}

		if err := doc.GenMarkdownTreeCustom(rootCmd, outDir, linkHandler, linkHandler); err != nil {
			return fmt.Errorf("generate docs: %w", err)
		}

		// Also create index file
		indexContent := `# pheno-session Command Reference

## Overview

pheno-session is a unified session orchestrator for all LLM harnesses.

## Commands

### Session Management

| Command | Description |
|---------|-------------|
| [list](list.md) | List sessions (default: all, sorted by updated_by) |
| [start](start.md) | Start new session with provider/model |
| [open](open.md) | Open session in harness |
| [transfer](transfer.md) | Transfer session between harnesses |
| [manage](manage.md) | Interactive single-session management |
| [tui](tui.md) | Interactive TUI browser |

### Sitback Orchestration

| Command | Description |
|---------|-------------|
| [sitback](sitback.md) | Autonomous orchestration dashboard |
| [sync](sync.md) | Sync session data from all harnesses |
| [delegate](delegate.md) | Delegate tasks to specific harnesses |
| [audit](audit.md) | Comprehensive audit of all sessions |
| [bridge](bridge.md) | Bridge to thegent's sitback implementation |

### Utilities

| Command | Description |
|---------|-------------|
| [completion](completion.md) | Generate shell completion scripts |
| [gen-docs](gen-docs.md) | Generate markdown documentation |
`
		indexPath := filepath.Join(outDir, "README.md")
		if err := os.WriteFile(indexPath, []byte(indexContent), 0644); err != nil {
			return fmt.Errorf("write index: %w", err)
		}

		fmt.Printf("Created index: %s\n", indexPath)
		return nil
	},
}
