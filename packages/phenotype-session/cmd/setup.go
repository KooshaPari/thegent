package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
)

// Config holds all configuration
type Config struct {
	ForgeURL string `json:"forge_url"`
	CodexURL string `json:"codex_url"`
	NATSURL  string `json:"nats_url"`
}

var setupCmd = &cobra.Command{
	Use:   "setup",
	Short: "Setup configuration",
	Long: `Setup pheno-session configuration.
	
This tool uses OAuth-logged-in CLIs (no API keys needed).
It will create config at ~/.config/pheno-session/config.json`,
	RunE: runSetup,
}

func runSetup(cmd *cobra.Command, args []string) error {
	configDir := filepath.Join(os.Getenv("HOME"), ".config", "pheno-session")
	configPath := filepath.Join(configDir, "config.json")

	fmt.Println("=== pheno-session Setup ===")
	fmt.Println("Using OAuth-logged-in CLIs (no API keys needed)")
	fmt.Println()

	// Get optional URLs
	forgeURL := prompt("Forge API URL", "http://localhost:8080")
	codexURL := prompt("Codex API URL", "http://localhost:8090")
	natsURL := prompt("NATS URL", "nats://localhost:4222")

	config := Config{
		ForgeURL: forgeURL,
		CodexURL: codexURL,
		NATSURL:  natsURL,
	}

	// Create directories
	os.MkdirAll(configDir, 0755)

	// Write config
	data, _ := json.MarshalIndent(config, "", "  ")
	os.WriteFile(configPath, data, 0644)

	fmt.Println()
	fmt.Println("✓ Config saved to:", configPath)
	fmt.Println()
	fmt.Println("To run pheno-session:")
	fmt.Println("  pheno-session list")
	fmt.Println("  pheno-session sitback")
	fmt.Println("  pheno-session tui")

	return nil
}

func prompt(label, defaultVal string) string {
	fmt.Printf("%s [%s]: ", label, defaultVal)
	var val string
	fmt.Scanln(&val)
	if val == "" {
		return defaultVal
	}
	return val
}

func init() {
	rootCmd.AddCommand(setupCmd)
}
