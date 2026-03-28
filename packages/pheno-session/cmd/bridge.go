package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"
)

// Bridge to thegent's existing sitback command
// This allows pheno-session to delegate to the Python implementation
// when thegent is available in the system PATH.

var (
	thegentPath    string
	thegentProfile string
)

// discoverThegent searches for thegent in common locations
func discoverThegent() (string, error) {
	// Check if thegent is in PATH
	path, err := exec.LookPath("thegent")
	if err == nil {
		return path, nil
	}

	// Check common locations
	locations := []string{
		filepath.Join(os.Getenv("HOME"), "CodeProjects", "Phenotype", "repos", "thegent", "src", "thegent", "clode_main.py"),
		filepath.Join(os.Getenv("HOME"), "CodeProjects", "Phenotype", "repos", "thegent", "thegent", "clode_main.py"),
	}

	for _, loc := range locations {
		if _, err := os.Stat(loc); err == nil {
			return "python3 " + loc, nil
		}
	}

	return "", fmt.Errorf("thegent not found in PATH or common locations")
}

var bridgeCmd = &cobra.Command{
	Use:   "bridge",
	Short: "Bridge to thegent's sitback implementation",
	Long: `Bridge to the existing thegent sitback command when available.

This command allows pheno-session to leverage thegent's existing
sitback functionality while providing a unified interface.

If thegent is not available, this command will attempt to use the
built-in Go sitback implementation instead.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		// Try to find thegent
		path, err := discoverThegent()
		if err != nil {
			fmt.Println("thegent not found, using built-in sitback...")
			// Fall back to built-in sitback
			return runSitbackAudit()
		}

		// Build thegent command arguments
		thegentArgs := []string{}

		if thegentProfile != "" {
			thegentArgs = append(thegentArgs, "--profile", thegentProfile)
		}

		// Add any additional arguments
		thegentArgs = append(thegentArgs, args...)

		// Execute thegent
		fmt.Printf("Delegating to thegent: %s\n", path)

		var execCmd *exec.Cmd
		if strings.HasPrefix(path, "python3 ") {
			pythonPath := strings.TrimPrefix(path, "python3 ")
			execCmd = exec.Command("python3", pythonPath)
		} else {
			execCmd = exec.Command(path)
		}

		execCmd.Args = append(execCmd.Args, thegentArgs...)
		execCmd.Stdout = os.Stdout
		execCmd.Stderr = os.Stderr
		execCmd.Stdin = os.Stdin

		return execCmd.Run()
	},
}
